from dataclasses import dataclass
from typing import Self


@dataclass
class PartOfSpeech:
    category: str
    subcategory1: str
    subcategory2: str
    subcategory3: str

    @classmethod
    def from_raw_part_of_speech(cls, raw_part_of_speech: str) -> Self:
        (
            category,
            subcategory1,
            subcategory2,
            subcategory3,
        ) = raw_part_of_speech.split(",")
        return cls(
            category,
            subcategory1,
            subcategory2,
            subcategory3,
        )
