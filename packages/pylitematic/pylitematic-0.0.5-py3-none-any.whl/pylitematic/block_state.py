from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from nbtlib import Compound
from typing import Any, Iterator

from .block_property import Properties
from .resource_location import ResourceLocation


@dataclass(frozen=True, order=True)
class BlockId(ResourceLocation):

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BlockState):
            return self == other.id
        else:
            return super().__eq__(other)


class BlockState:

    __slots__ = ("_id", "_props")

    def __init__(self, _id: str | BlockId, **props: Any) -> None:
        if isinstance(_id, str):
            _id = BlockId.from_string(_id)
        elif not isinstance(_id, BlockId):
            raise TypeError(
                f"'_id' has to be str or {BlockId.__name__}, got"
                f" {type(_id).__name__}")
        self._id: BlockId = _id

        self._props: Properties = Properties(**props)

    def __getitem__(self, name: str) -> Any:
        try:
            return self._props[name]
        except KeyError as exc:
            raise KeyError(
                f"{type(self).__name__} '{self}' does not"
                f" have {name!r} property") from exc

    # def __getattr__(self, name: str) -> Any:
    #     return self[name]

    def __contains__(self, name: str) -> bool:
        return name in self._props

    def __len__(self) -> int:
        return len(self._props)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, str):
            try:
                other = BlockState.from_string(other)
                return self == other
            except ValueError:
                return False

        if isinstance(other, BlockId):
            return self.id == other
        elif isinstance(other, BlockState):
            return (self.id, self._props) == (other.id, other._props)
        else:
            return NotImplemented

    def __lt__(self, other: Any) -> bool:
        if not isinstance(other, BlockState):
            return NotImplemented
        return (self.id, self._props) < (other.id, other._props)

    def __hash__(self) -> int:
        return hash((self._id, self._props))

    def __str__(self) -> str:
        props_str = "" if not self._props else str(self._props)
        return f"{self.id}{props_str}"

    def __repr__(self) -> str:
        return (
            f"{type(self).__name__}("
            f"id: {self._id!r}, props: {self._props!r})")

    @property
    def id(self) -> BlockId:
        return self._id

    def props(self) -> Iterator[tuple[str, Any]]:
        return self._props.items()

    def to_string(self) -> str:
        return str(self)

    @classmethod
    def from_string(cls, string: str) -> BlockState:
        idx = string.find("[") # basic parsing to separate block:id[name=value]
        if idx == -1:
            id, props = string, ""
        else:
            id, props = string[:idx], string[idx:]

        state = cls(id)
        state._props = Properties.from_string(props)
        return state

    def to_nbt(self) -> Compound:
        nbt = Compound()
        nbt["Name"] = self._id.to_nbt()
        if self._props:
            nbt["Properties"] = self._props.to_nbt()
        return nbt

    @classmethod
    def from_nbt(cls, nbt: Compound) -> BlockState:
        state = cls(str(nbt["Name"]))
        state._props = Properties.from_nbt(nbt.get("Properties", Compound()))
        return state

    def with_id(self, id: str) -> BlockState:
        state = type(self)(id)
        state._props = deepcopy(self._props)
        return state

    def with_props(self, **props: Any) -> BlockState:
        state = type(self)(self.id)
        new_props = deepcopy(self._props)
        for name, value in props.items():
            if value is None:
                del new_props[name]
            else:
                new_props[name] = value
        state._props = new_props
        return state

    def without_props(self) -> BlockState:
        return BlockState(self.id)


AIR = BlockState("air")
