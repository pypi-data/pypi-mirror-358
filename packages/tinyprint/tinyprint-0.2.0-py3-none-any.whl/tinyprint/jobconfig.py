from __future__ import annotations

from dataclasses import dataclass
import enum
from typing import Any, Optional, TypeAlias

from dataclasses_json import DataClassJsonMixin


class Orientation(enum.Enum):
    """Set if book has vertical or horizontal layout

    Horizontal: | | |

                __
    Vertical:   __
                __
    """

    HORIZONTAL = 0
    VERTICAL = 1

    @classmethod
    def parse(cls, v: str):
        return _parse_str(cls, v)


def _parse_str(cls, v):
    try:
        return getattr(cls, v.upper())
    except Exception:
        raise AttributeError("{cls}: enum {v} not found")


@dataclass
class PageSize(DataClassJsonMixin):
    width: float
    heigth: float

    @classmethod
    def from_any(cls, obj: Any) -> PageSize:
        match obj:
            case PageSize():
                return obj
            case tuple() | list():
                return PageSize(*obj)
            case _:
                raise NotImplementedError(f"can't parse {obj} to PageSize")


@dataclass
class Resource:
    path: str
    fragment_height: Optional[int] = None
    # Either 0 (= black) or 1 (= red)
    color: int = 0


@dataclass
class JobConfig(DataClassJsonMixin):
    resource_list: list[Resource]
    printer_config: Optional[str] = None
    copy_count: int = 1
    cut: bool = True
    orientation: Orientation = Orientation.HORIZONTAL
    page_size: Optional[PageSize] = None
    sleep_time: Optional[float] = None

    def to_file(self, path: str):
        with open(path, "w") as f:
            f.write(self.to_json())

    @classmethod
    def from_file(cls, path: str):
        with open(path, "r") as f:
            return cls.from_json(f.read())
