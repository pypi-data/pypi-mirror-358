from logging import getLogger
from pathlib import Path
from typing import Iterable, cast
import xml.etree.ElementTree as ET
from jaconv import kata2hira
from janome.tokenizer import Tokenizer, Token
from .font_converter import FontConverter
from .part_of_speech import PartOfSpeech

logger = getLogger(__name__)


class LonelySilhouetteMaker:
    def __init__(self, jmdict_e_xml_path: Path) -> None:
        self.tree = ET.parse(jmdict_e_xml_path)
        self.tokenizer = Tokenizer()

    def _find_kanji_entry(self, word: str, reading: str) -> ET.Element | None:
        # find entries that have both a keb element whose text is equal to the given word and a reb element whose text is equal to the given reading as descendants
        entry = self.tree.find(
            f"./entry/k_ele/keb[.='{word}']/../../r_ele/reb[.='{reading}']/../.."
        )
        return entry

    def _find_non_kanji_only_word_entry(self, word: str) -> ET.Element | None:
        return self.tree.find(f"./entry/r_ele/reb[.='{word}']/../..")

    def _find_entry(self, word: str, reading: str) -> ET.Element | None:
        return self._find_kanji_entry(
            word, reading
        ) or self._find_non_kanji_only_word_entry(word)

    def _translate_word_ja_to_en(
        self, ja_word: str, ja_reading: str
    ) -> Iterable[str] | None:
        # search an entry with a keb node whose text is equal to given Japanese word
        entry = self._find_entry(ja_word, ja_reading)
        if entry is None:
            return None
        glosses = entry.findall("./sense/gloss")
        for gloss in glosses:
            if gloss.text is not None:
                yield gloss.text
        return None

    def _translate_token_ja_to_en(self, token: Token) -> Iterable[str] | None:
        return self._translate_word_ja_to_en(token.surface, kata2hira(token.reading))

    def _is_noun(self, token: Token) -> bool:
        part_of_speech = PartOfSpeech.from_raw_part_of_speech(token.part_of_speech)
        return part_of_speech.category == "名詞"

    def make(self, text: str, font_converter: FontConverter) -> str:
        tokens = list(self.tokenizer.tokenize(text))
        # the last translatable token will be lonely silhouette
        token_to_be_lonely = None
        for token in reversed(tokens):
            if self._is_noun(token):
                en_words = self._translate_token_ja_to_en(token)
                if en_words is not None:
                    token_to_be_lonely = (token, list(en_words))
                    break

        if token_to_be_lonely is None:
            logger.debug("cannot find the word that should become a lonely silhouette")
            return text

        def lonely_silhouette_token(token: Token) -> str:
            if token != token_to_be_lonely[0]:
                return cast(
                    str, token.surface
                )  # TODO: mypy does not recognize token.surface
            en_words = token_to_be_lonely[1]
            # pick first word for now
            return font_converter.convert(en_words[0])

        return "".join(map(lonely_silhouette_token, tokens))
