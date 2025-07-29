"""
This module provides functionality to render collected TODOs into an HTML report using Jinja2 templates.
"""

from __future__ import annotations

try:
    import importlib_resources as pkg_resources
except ImportError:
    import importlib.resources as pkg_resources

import logging
import os
import webbrowser
from pathlib import Path

import code_tags_html_temlplates.templates as templates  # make sure templates is a real subpackage
import jinja2

from code_tags.collection_types import CollectedTODOs

logger = logging.getLogger(__name__)


def print_html(found: CollectedTODOs, output: Path = Path("todo_site")) -> None:
    """Generate an HTML report from collected TODOs.

    Args:
        found (CollectedTODOs): An instance of CollectedTODOs containing the collected TODOs.
        output (Path): The directory where the HTML report will be saved. Defaults to "todo_site".
    """
    # Load template from package
    with pkg_resources.files(templates).joinpath("report.html.jinja2").open("r", encoding="utf-8") as f:
        template_src = f.read()

    # Render HTML with data
    template = jinja2.Template(template_src)
    total_to_render = len(found["todos"]) + len(found["exceptions"])
    logger.info(f"Total to render: {total_to_render}")
    if total_to_render == 0:
        raise TypeError("No data to render.")

    rendered = template.render(
        dones=list(_ for _ in found["todos"] if _.is_probably_done()),
        todos=list(_ for _ in found["todos"] if not _.is_probably_done()),
        exceptions=found["exceptions"],
        undefined=jinja2.StrictUndefined,
    )

    # Ensure output directory exists
    output.mkdir(parents=True, exist_ok=True)

    # Write rendered HTML to index.html in output dir
    output_file = output / "index.html"
    output_file.write_text(rendered, encoding="utf-8")

    # Skip browser launch if on CI (e.g., GitHub Actions, etc.)
    if not any(key in os.environ for key in ("CI", "GITHUB_ACTIONS", "CODE_TAGS_NO_OPEN_BROWSER")):
        webbrowser.open(output_file.resolve().as_uri())
