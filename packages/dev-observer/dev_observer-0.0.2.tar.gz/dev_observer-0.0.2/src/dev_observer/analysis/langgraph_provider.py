import asyncio
import dataclasses
import logging
from typing import Optional, List, Union

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage, SystemMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableConfig
from langfuse.callback import CallbackHandler
from langgraph.constants import END
from langgraph.graph.state import CompiledStateGraph, StateGraph
from langgraph.store.memory import InMemoryStore
from langgraph.utils.config import ensure_config
from pydantic import BaseModel

from dev_observer.analysis.provider import AnalysisProvider, AnalysisResult
from dev_observer.api.types.ai_pb2 import ModelConfig
from dev_observer.log import s_
from dev_observer.prompts.langfuse import LangfuseAuthProps
from dev_observer.prompts.provider import FormattedPrompt
from dev_observer.storage.provider import StorageProvider

_log = logging.getLogger(__name__)


@dataclasses.dataclass
class AnalysisInfo:
    prompt: FormattedPrompt

    def append(self, config: RunnableConfig) -> RunnableConfig:
        md = config.get("metadata", {})
        md[AnalysisInfo.get_key()] = self
        config["metadata"] = md
        return config

    @classmethod
    def get_key(cls):
        return "dev_observer:analysis_info"

    @classmethod
    def from_config(cls, config: RunnableConfig) -> "AnalysisInfo":
        metadata = config.get("metadata", {})
        info = metadata.get(AnalysisInfo.get_key())
        if info is None:
            _log.warning(s_("No analysis info in metadata", metadata=metadata))
            raise ValueError("No analysis info in metadata")
        return info

def _masking_function(data):
    return "[REDACTED]"

class LanggraphAnalysisProvider(AnalysisProvider):
    _lf_auth: Optional[LangfuseAuthProps] = None
    _mask: bool
    _storage: StorageProvider

    def __init__(self, storage: StorageProvider, langfuse_auth: Optional[LangfuseAuthProps] = None, mask: bool = True):
        self._lf_auth = langfuse_auth
        self._mask = mask
        self._storage = storage

    async def analyze(self, prompt: FormattedPrompt, session_id: Optional[str] = None) -> AnalysisResult:
        g = await _get_graph()
        info = AnalysisInfo(prompt=prompt)
        config = info.append(ensure_config())
        global_config = await self._storage.get_global_config()
        disable_masking = global_config.HasField("analysis") and global_config.analysis.disable_masking
        should_mask = self._mask and not disable_masking
        if self._lf_auth is not None:
            public_key = self._lf_auth.public_key
            secret_key = self._lf_auth.secret_key
            _log.debug(s_("Initializing Langfuse CallbackHandler",
                          host=self._lf_auth.host,
                          public_key=public_key,
                          secret_key=f"{secret_key[:5]}****",
                          session_id=session_id,
                          ))
            callbacks = [CallbackHandler(
                mask=_masking_function if should_mask else None,
                public_key=public_key,
                secret_key=secret_key,
                host=self._lf_auth.host,
                session_id=session_id,
            )]
            config["callbacks"] = callbacks
        result = await g.ainvoke({}, config, output_keys=["response"])
        analysis = result.get("response", "")
        _log.debug(s_("Content analyzed", anaysis_len=len(analysis)))
        return AnalysisResult(analysis=analysis)


_in_memory_store = InMemoryStore()

_lock = asyncio.Lock()
_graph: Optional[CompiledStateGraph] = None


async def _get_graph() -> CompiledStateGraph:
    global _lock
    async with _lock:
        global _graph
        if _graph is not None:
            return _graph

        nodes = AnalysisNodes()
        workflow = StateGraph(AnalysisNodes)
        workflow.add_node("analyze", nodes.analyze)
        workflow.add_edge("analyze", END)
        workflow.set_entry_point("analyze")

        _graph = workflow.compile()
        return _graph


class AnalysisState(BaseModel):
    response: Optional[str] = None


class AnalysisNodes:
    async def analyze(self, _: AnalysisState, config: RunnableConfig):
        info = AnalysisInfo.from_config(config)
        prompt = info.prompt
        prompt_config = prompt.config
        if prompt_config is None or prompt_config.model is None:
            raise ValueError("Missing model in prompt config")

        prompt_name: Optional[str] = None
        if prompt.langfuse_prompt is not None:
            prompt_name = prompt.langfuse_prompt.name

        messages: List[BaseMessage] = []
        if prompt.system is not None:
            messages.append(SystemMessage(content=prompt.system.text))
        if prompt.user is not None:
            contents: List[Union[str, dict]] = []
            text = prompt.user.text
            image_url = prompt.user.image_url
            if text is not None and len(text) > 0:
                contents.append({"type": "text", "text": text})
            if image_url is not None and len(image_url) > 0:
                contents.append({"type": "image_url", "image_url": {"url": image_url}})
            messages.append(HumanMessage(content=contents))

        model = _model_from_config(prompt_config.model)
        _log.debug(s_("Calling model", prompt_config=prompt_config, prompt_name=prompt_name))
        pt = ChatPromptTemplate.from_messages(messages)
        if prompt.langfuse_prompt is not None:
            pt.metadata = {"langfuse_prompt": prompt.langfuse_prompt}
        pv = await pt.ainvoke({}, config=config)
        response = await model.ainvoke(pv, config=config)
        _log.debug(s_("Model replied", prompt_config=prompt_config, prompt_name=prompt_name))
        return {"response": f"{response.content}"}


def _model_from_config(config: ModelConfig) -> BaseChatModel:
    return init_chat_model(f"{config.provider}:{config.model_name}")
