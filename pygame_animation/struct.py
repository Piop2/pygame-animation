from __future__ import annotations

from dataclasses import dataclass

from pygame import Surface

from pygame_animation.direction import DirectionType


@dataclass(frozen=True)
class Tag:
    name: str
    start: int
    end: int
    direction_type: DirectionType
    repeat: int

    def copy(self) -> Tag:
        return Tag(self.name, self.start, self.end, self.direction_type, self.repeat)


@dataclass(frozen=True)
class Frame:
    image: Surface
    duration: int
