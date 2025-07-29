from pathlib import Path

import pluggy
from code_tags_html_temlplates.views_templated import print_html

from code_tags.collect import CollectedTODOs
from code_tags.config import CodeTagsConfig

# Use the same marker name as defined in the host's hookspecs
hookimpl = pluggy.HookimplMarker("code_tags")


@hookimpl
def code_tags_print_report(
    format_name: str, found_data: CollectedTODOs, output_path: str, config: CodeTagsConfig
) -> bool:
    if format_name == "html_pretty":
        print_html(found_data, output=Path(output_path))
        return True  # Indicates this plugin handled the request
    return False  # This plugin does not handle the requested format


@hookimpl
def code_tags_print_report_style_name() -> list[str]:
    return ["html_pretty"]
