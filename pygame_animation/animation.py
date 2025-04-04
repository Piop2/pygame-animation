from __future__ import annotations

from typing import Optional, final
from os import PathLike
from pathlib import Path

from pygame import Surface

from pygame_animation.timer import CountUpTimer
from pygame_animation.direction import (
    DirectionType,
    DirectionIterable,
    DirectionIterator,
    Forward,
    Reverse,
)
from pygame_animation.struct import Tag, Frame
from pygame_animation.loader import BaseLoader


@final
class Animation:
    def __init__(
        self,
        frames: Optional[list[Frame]] = None,
        repeat: int = 0,
        direction_type: Optional[DirectionType] = None,
        tags: Optional[dict[str, Tag]] = None,
    ) -> None:
        if frames is None:
            frames = []
        self.__frames: list[Frame] = frames

        if tags is None:
            tags = {}
        self.__tags: dict[str, Tag] = tags

        self.__timer: CountUpTimer = CountUpTimer()

        if direction_type is None:
            direction_type = DirectionType.FORWARD
        direction_class: type[DirectionIterable]
        match direction_type:
            case DirectionType.FORWARD:
                direction_class = Forward
            case DirectionType.REVERSE:
                direction_class = Reverse
            case _:
                raise RuntimeError

        self.__direction: DirectionIterable = direction_class(
            repeat=repeat, frame_length=len(frames)
        )
        self.__direction_iterator: DirectionIterator = iter(self.__direction)
        self.__index: int = next(self.__direction_iterator)
        return
    
    @classmethod
    def load(self, path: str | Path | PathLike, loader: Optional[BaseLoader] = None) -> Animation:
        loader = ... # TODO 기본 로더 구현 필요
        raise NotImplementedError

    def get_size(self) -> tuple[int, int]:
        if not self.__frames:
            raise RuntimeError

        return self.__frames[0].image.get_size()

    def get_frames(self) -> tuple[Frame]:
        return self.__frames

    def get_index(self) -> int:
        return self.__index

    def get_tags(self) -> tuple[Tag]:
        return tuple(self.__tags.values())

    def is_playing(self) -> bool:
        return self.__timer.is_paused()

    def play(self) -> None:
        self.__timer.unpause()
        return

    def pause(self) -> None:
        self.__timer.pause()
        return

    def reset(self) -> None:
        self.play()
        self.__timer.reset()
        self.__direction_iterator = iter(self.__direction)
        self.__index = next(self.__direction_iterator)
        return

    def split_by_tag(self, tag_name: str) -> Animation:
        main_tag: Tag = self.__tags[tag_name]

        sub_tags: list[Tag] = []
        for tag in list(self.__tags.values()):
            if tag == main_tag:
                continue

            if main_tag.start <= tag.start and tag.end <= main_tag.end:
                new_start = tag.start - main_tag.start
                new_end = main_tag.end - tag.end

                sub_tags.append(
                    Tag(tag.name, new_start, new_end, tag.direction_type, tag.repeat)
                )

        return Animation(
            self.__frames[main_tag.start : main_tag.end + 1],
            main_tag.repeat,
            main_tag.direction_type,
            sub_tags,
        )

    def update(self, ms: int) -> None:
        if not self.is_playing():
            return

        if self.__timer.get_time() >= self.__frames[self.__index].duration:
            try:
                self.__index = next(self.__direction_iterator)
            except StopIteration:
                self.pause()

        self.__timer.update(ms)
        return

    def render(self) -> Surface:
        return self.__frames[self.__index].image
