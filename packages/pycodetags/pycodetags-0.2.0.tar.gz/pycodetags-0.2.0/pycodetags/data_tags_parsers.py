"""
Parse specific schemas of data tags
"""

from __future__ import annotations

import logging
from collections.abc import Generator
from pathlib import Path

from pycodetags import folk_code_tags
from pycodetags.comment_finder import find_comment_blocks
from pycodetags.data_tags import DataTag, DataTagSchema, parse_codetags
from pycodetags.folk_code_tags import FolkTag

logger = logging.getLogger(__name__)


def iterate_comments(file: str, schemas: list[DataTagSchema], include_folk_tags: bool) -> Generator[DataTag | FolkTag]:
    """
    Collect PEP-350 style code tags from a given file.

    Args:
        file (str): The path to the file to process.
        schemas (DataTaSchema): Schemas that will be detected in file
        include_folk_tags (bool): Include folk schemas that do not strictly follow PEP350

    Yields:
        PEP350Tag: A generator yielding PEP-350 style code tags found in the file.
    """
    logger.info(f"collect_pep350_code_tags: processing {file}")
    things: list[DataTag | FolkTag] = []
    for _start_line, _start_char, _end_line, _end_char, final_comment in find_comment_blocks(Path(file)):
        # Can only be one comment block now!
        thing = []
        for schema in schemas:
            thing = parse_codetags(final_comment, schema, strict=False)
            things.extend(thing)
        if not thing and include_folk_tags:
            # BUG: fails if there are two in th same.
            # TODO: blank out consumed text, reconsume bock
            found_folk_tags: list[FolkTag] = []
            # TODO: support config of folk schema.
            folk_code_tags.process_text(
                final_comment,
                allow_multiline=True,
                default_field_meaning="assignee",
                found_tags=found_folk_tags,
                file_path=file,
                valid_tags=[],
            )
            things.extend(found_folk_tags)

    yield from things
