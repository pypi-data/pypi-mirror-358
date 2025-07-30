import logging

import pluggy

from pycodetags.plugin_specs import CodeTagsSpec

logger = logging.getLogger(__name__)

PM = pluggy.PluginManager("pycodetags")
PM.add_hookspecs(CodeTagsSpec)
PM.load_setuptools_entrypoints("pycodetags")


def reset_plugin_manager() -> None:
    """For testing or events can double up"""
    # pylint: disable=global-statement
    global PM  # nosec # noqa
    PM = pluggy.PluginManager("pycodetags")
    PM.add_hookspecs(CodeTagsSpec)
    PM.load_setuptools_entrypoints("pycodetags")


if logger.isEnabledFor(logging.DEBUG):
    # magic line to set a writer function
    PM.trace.root.setwriter(print)
    undo = PM.enable_tracing()


# At class level or module-level:
def get_plugin_manager() -> pluggy.PluginManager:
    return PM
