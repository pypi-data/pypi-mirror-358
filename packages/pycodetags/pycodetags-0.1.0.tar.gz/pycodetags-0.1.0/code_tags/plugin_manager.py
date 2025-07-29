import logging

import pluggy

from code_tags.plugin_specs import CodeTagsSpec

logger = logging.getLogger(__name__)

PM = pluggy.PluginManager("code_tags")
PM.add_hookspecs(CodeTagsSpec)
PM.load_setuptools_entrypoints("code_tags")

if logger.isEnabledFor(logging.DEBUG):
    # magic line to set a writer function
    PM.trace.root.setwriter(print)
    undo = PM.enable_tracing()


# At class level or module-level:
def get_plugin_manager() -> pluggy.PluginManager:
    return PM
