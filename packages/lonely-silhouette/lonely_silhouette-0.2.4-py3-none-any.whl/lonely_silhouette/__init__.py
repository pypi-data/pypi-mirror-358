from __future__ import annotations
from logging import getLogger, NullHandler
from pathlib import Path
from tempfile import NamedTemporaryFile
from typing import TYPE_CHECKING, Never
import requests
from .font_converter import FontConverter, FontStyle
from .lonely_silhouette_maker import LonelySilhouetteMaker

if TYPE_CHECKING:
    from _typeshed import SupportsWrite


__all__ = ["lonely_silhouette", "FontStyle"]


logger = getLogger(__name__)
logger.addHandler(NullHandler())


def download_latest_jmdict_e(dest_file: SupportsWrite[bytes]) -> None:
    response = requests.get("http://ftp.edrdg.org/pub/Nihongo/JMdict_e")
    response.raise_for_status()
    logger.debug("File downloaded successfully")
    dest_file.write(response.content)
    logger.debug("Saved successfully to the destination file")


# TODO: How to define closure method type?
def build_default_lonely_silhouette():  # type: ignore[no-untyped-def]
    lonely_silhouette_maker_cache = None

    def default_lonely_silhouette(
        text: str, *_: Never, font_style: FontStyle = FontStyle.ITALIC
    ) -> str:
        # Download the file only for the first time you call this inner method, and cache the parsed result throughout runtime
        nonlocal lonely_silhouette_maker_cache
        if lonely_silhouette_maker_cache is None:
            with NamedTemporaryFile("r+b") as f:
                download_latest_jmdict_e(f)
                jmdict_e_path = Path(f.name)
                lonely_silhouette_maker_cache = LonelySilhouetteMaker(jmdict_e_path)

        font_converter = FontConverter.create(font_style)
        return lonely_silhouette_maker_cache.make(text, font_converter)

    return default_lonely_silhouette


lonely_silhouette = build_default_lonely_silhouette()  # type: ignore[no-untyped-call]
