from types import TracebackType
from typing import Optional, Type
from pydantic import Field
from rath import rath
import contextvars

from rath.links.auth import AuthTokenLink

from rath.links.compose import TypedComposedLink
from rath.links.dictinglink import DictingLink
from rath.links.shrink import ShrinkingLink
from rath.links.split import SplitLink

current_alpaka_rath: contextvars.ContextVar[Optional["AlpakaRath"]] = (
    contextvars.ContextVar("current_alpaka_rath", default=None)
)


class AlpakaLinkComposition(TypedComposedLink):
    shrinking: ShrinkingLink = Field(default_factory=ShrinkingLink)
    dicting: DictingLink = Field(default_factory=DictingLink)
    auth: AuthTokenLink
    split: SplitLink


class AlpakaRath(rath.Rath):
    """Fluss Rath

    Args:
        rath (_type_): _description_
    """

    async def __aenter__(self):
        await super().__aenter__()
        current_alpaka_rath.set(self)
        return self

    async def __aexit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        traceback: Optional[TracebackType],
    ) -> None:
        await super().__aexit__(exc_type, exc_val, traceback)
        current_alpaka_rath.set(None)
