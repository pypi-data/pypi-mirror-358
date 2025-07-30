from abc import ABC, abstractmethod
from enum import Enum


class FontStyle(Enum):
    ITALIC = "italic"
    SCRIPT = "script"


class FontConverter(ABC):
    @abstractmethod
    def convert(self, text: str) -> str: ...

    # simple factory as a current barely sufficient solution
    @staticmethod
    # TODO: How to define return type in simple factory method?
    def create(font_style: FontStyle):  # type: ignore[no-untyped-def]
        if font_style == FontStyle.ITALIC:
            return Italicizer()
        if font_style == FontStyle.SCRIPT:
            return Scriptizer()


class Italicizer(FontConverter):
    def convert(self, text: str) -> str:
        # mathematical italic small series from mathematical alphanumeric symbols block
        italic_mapping = {
            "a": "𝑎",
            "b": "𝑏",
            "c": "𝑐",
            "d": "𝑑",
            "e": "𝑒",
            "f": "𝑓",
            "g": "𝑔",
            "h": "ℎ",  # planck constant from letterlike symbols block
            "i": "𝑖",
            "j": "𝑗",
            "k": "𝑘",
            "l": "𝑙",
            "m": "𝑚",
            "n": "𝑛",
            "o": "𝑜",
            "p": "𝑝",
            "q": "𝑞",
            "r": "𝑟",
            "s": "𝑠",
            "t": "𝑡",
            "u": "𝑢",
            "v": "𝑣",
            "w": "𝑤",
            "x": "𝑥",
            "y": "𝑦",
            "z": "𝑧",
        }

        trans_table = str.maketrans(italic_mapping)
        italic_string = text.translate(trans_table)
        return italic_string


class Scriptizer(FontConverter):
    def convert(self, text: str) -> str:
        # mathematical script small series from mathematical alphanumeric symbols block
        script_mapping = {
            "a": "𝒶",
            "b": "𝒷",
            "c": "𝒸",
            "d": "𝒹",
            "e": "ℯ",  # script small e from letterlike symbols block
            "f": "𝒻",
            "g": "ℊ",  # script small g from letterlike symbols block
            "h": "𝒽",
            "i": "𝒾",
            "j": "𝒿",
            "k": "𝓀",
            "l": "𝓁",
            "m": "𝓂",
            "n": "𝓃",
            "o": "ℴ",  # script small o from letterlike symbols block
            "p": "𝓅",
            "q": "𝓆",
            "r": "𝓇",
            "s": "𝓈",
            "t": "𝓉",
            "u": "𝓊",
            "v": "𝓋",
            "w": "𝓌",
            "x": "𝓍",
            "y": "𝓎",
            "z": "𝓏",
        }

        trans_table = str.maketrans(script_mapping)
        script_string = text.translate(trans_table)
        return script_string
