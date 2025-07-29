# Contents of pycodetags source tree

## File: config.py

```python
"""
Config for pycodetags library.

This is a basically valid config
```toml
[tool.pycodetags]
# Range Validation, Range Sources

# Empty list means use file
# If validated, originator and assignee must be on author list
valid_authors = []
valid_authors_file = "AUTHORS.md"
# Can be Gnits, single_column, humans.txt
valid_authors_schema = "single_column"

# Active can be validated against author list.
# Active user from "os", "env", "git"
user_identification_technique = "os"
# .env variable if method is "env"
user_env_var = "PYCODETAGS_USER"

# Case insensitive. Needs at least "done"
valid_status = [
    "planning",
    "ready",
    "done",
    "development",
    "inprogress",
    "testing",
    "closed",
    "fixed",
    "nobug",
    "wontfix"
]

# Categories, priorities, iterations are only displayed
valid_categories = []
valid_priorities = ["high", "medium", "low"]

# Used to support change log generation and other features.
closed_status = ["done", "closed", "fixed", "nobug", "wontfix"]

# Empty list means no restrictions
valid_releases = []

# Use to look up valid releases (versions numbers)
valid_releases_file = "CHANGELOG.md"
valid_releases_file_schema = "CHANGELOG.md"

# Used in sorting and views
releases_schema = "semantic"

# Subsection of release. Only displayed.
valid_iterations = ["1", "2", "3", "4"]

# Empty list means all are allowed
valid_custom_field_names = []

# Originator and origination date are important for issue identification
# Without it, heuristics are more likely to fail to match issues to their counterpart in git history
mandatory_fields = ["originator", "origination_date"]

# Helpful for parsing tracker field, used to make ticket a clickable url
tracker_domain = "example.com"
# Can be url or ticket
tracker_style = "url"

# Defines the action for a TODO condition: "stop", "warn", "nothing".
enable_actions = true
default_action = "warn"
action_on_past_due = true
action_only_on_responsible_user = true

# Environment detection
disable_on_ci = true

# Use .env file
use_dot_env = true
```

"""

from __future__ import annotations

import logging
import os
import sys
from typing import Any

from pycodetags.user import get_current_user
from pycodetags.users_from_authors import parse_authors_file_simple

try:
    import tomllib  # Python 3.11+
except ModuleNotFoundError:
    try:
        import toml
    except ImportError:
        # This probably shouldn't raise in a possible production environment.
        pass


logger = logging.getLogger(__name__)


def careful_to_bool(value: Any, default: bool) -> bool:
    if isinstance(value, bool):
        return value
    if str(value).lower() in ("false", "0"):
        return False
    if value is None:
        return default
    if value == "":
        return default
    return default


class CodeTagsConfig:
    _instance: CodeTagsConfig | None = None
    _config: dict[str, Any] = {}

    def __init__(self, pyproject_path: str = "pyproject.toml", set_user: str | None = None):

        self._pyproject_path = pyproject_path
        self._load()
        self.user_override = set_user

    def current_user(self) -> str:
        if self.user_override:
            return self.user_override
        return get_current_user(self.user_identification_technique(), self.user_env_var())

    def _load(self) -> None:
        if not os.path.exists(self._pyproject_path):
            self._config = {}
            return

        with open(self._pyproject_path, "rb" if "tomllib" in sys.modules else "r") as f:
            # pylint: disable=used-before-assignment
            data = tomllib.load(f) if "tomllib" in sys.modules else toml.load(f)

        self._config = data.get("tool", {}).get("pycodetags", {})

    # Property accessors
    def valid_authors(self) -> list[str]:
        """Author list, if empty or None, all are valid, unless file specified"""
        author_file = self.valid_authors_file()
        schema = self.valid_authors_schema()
        if author_file and schema:
            if schema == "single_column":
                with open(author_file, encoding="utf-8") as file_handle:
                    authors = [_ for _ in file_handle.readlines() if _]
                return authors
            if schema == "gnu_gnits":
                authors = parse_authors_file_simple(author_file)
                return authors

        return [_.lower() for _ in self._config.get("valid_authors", [])]

    def valid_authors_file(self) -> str:
        """Author list, overrides valid authors if specified. File must exist."""
        field = "valid_authors_file"
        return str(self._config.get(field, ""))

    def valid_authors_schema(self) -> str:
        """Author schema, must be specified if authors from file is set."""
        field = "valid_authors_schema"
        result = self._config.get(field, "")
        accepted = ("gnu_gnits", "single_column", "")
        if result not in accepted:
            raise TypeError(f"Invalid configuration: {field} must be in {accepted}")
        if self.valid_authors_file() and result == "":
            raise TypeError(
                "Invalid configuration: if valid_authors_from_file is set, "
                f"then must be valid_authors_schema must be set to one of {accepted}"
            )
        return str(self._config.get("valid_authors_schema", ""))

    def valid_status(self) -> list[str]:
        """Status list, if empty or None, all are valid"""
        return [str(_).lower() for _ in self._config.get("valid_status", [])]

    def valid_categories(self) -> list[str]:
        """Category list, if empty or None, all are valid"""
        return [str(_).lower() for _ in self._config.get("valid_categories", [])]

    def closed_status(self) -> list[str]:
        """If status equals this,then it is closed, needed for business rules"""
        closed_status = self._config.get("closed_status", [])
        return [str(_).lower() for _ in closed_status]

    def valid_releases(self) -> list[str]:
        """Releases (Version numbers), if empty or None, all are valid.
        Past releases that do not match current schema are valid.
        """
        return [str(_).lower() for _ in self._config.get("valid_releases", [])]

    def valid_releases_file(self) -> str:
        """File name of file with valid releases"""
        valid_releases_from_file = self._config.get("valid_releases_file", "")
        return str(valid_releases_from_file).lower() if valid_releases_from_file else str(valid_releases_from_file)

    def valid_releases_file_schema(self) -> str:
        """Schema used to read from a known file type the valid versions."""
        field = "valid_releases_file_schema"
        result = self._config.get(field, "")
        accepted = ("keepachangelog",)
        if result not in accepted:
            raise TypeError(f"Invalid configuration: {field} must be in {accepted}")
        if self.valid_releases_file() and not result:
            raise TypeError(f"When valid_releases_from_file is set, {field} must be in {accepted}")
        return str(result)

    def releases_schema(self) -> str:
        """Schema used to parse, sort release (version) numbers.
        Not used to validate anything
        """
        field = "releases_schema"
        result = self._config.get(field, "")
        accepted = ("semantic", "pep440", "")
        if result not in accepted:
            raise TypeError(f"Invalid configuration: {field} must be in {accepted}")
        return str(result)

    def valid_priorities(self) -> list[str]:
        """Priority list, if empty or None, all are valid"""
        return [_.lower() for _ in self._config.get("valid_priorities", [])]

    def valid_iterations(self) -> list[str]:
        """Iteration list, if empty or None, all are valid."""
        return [_.lower() for _ in self._config.get("valid_iterations", [])]

    def valid_custom_field_names(self) -> list[str]:
        """Custom field names, if empty or None, all are valid."""
        return [_.lower() for _ in self._config.get("valid_custom_field_names", [])]

    def mandatory_fields(self) -> list[str]:
        """Mandatory fields, if empty or None, no mandatory fields."""
        return [_.lower() for _ in self._config.get("mandatory_fields", [])]

    def tracker_domain(self) -> str:
        """Domain of the tracker, used to make ticket links clickable."""
        return str(self._config.get("tracker_domain", ""))

    def tracker_style(self) -> str:
        """Style of the tracker, used to make ticket links clickable."""
        field = "tracker_style"
        result = self._config.get(field, "")
        accepted = ("url", "ticket", "")
        if result not in accepted:
            raise TypeError(f"Invalid configuration: {field} must be in {accepted}")
        return str(result)

    def user_identification_technique(self) -> str:
        """Technique for identifying current user. If not set, related features are disabled."""
        field = "user_identification_technique"
        result = self._config.get(field, "")
        accepted = ("os", "env", "git", "")
        if result not in accepted:
            raise TypeError(f"Invalid configuration: {field} must be in {accepted}")
        return str(result)

    def user_env_var(self) -> str:
        """Environment variable with active user."""
        return str(self._config.get("user_env_var", ""))

    def disable_all_runtime_behavior(self) -> bool:
        """Minimize performance costs when in production"""
        return careful_to_bool(self._config.get("disable_all_runtime_behavior", False), False)

    def enable_actions(self) -> bool:
        """Enable logging, warning, and stopping (TypeError raising)"""
        return careful_to_bool(self._config.get("enable_actions", False), False)

    def default_action(self) -> str:
        """Do actions log, warn, stop or do nothing"""
        field = "default_action"
        result = self._config.get(field, "")
        accepted = ("warn", "warning", "stop", "nothing", "")
        if result not in accepted:
            raise TypeError(f"Invalid configuration: {field} must be in {accepted}")
        return str(result)

    def action_on_past_due(self) -> bool:
        """Do actions do the default action"""
        return careful_to_bool(self._config.get("action_on_past_due", False), False)

    def action_only_on_responsible_user(self) -> bool:
        """Do actions do the default action when active user matches"""
        return careful_to_bool(self._config.get("action_only_on_responsible_user", False), False)

    def disable_on_ci(self) -> bool:
        """Disable actions on CI, overrides other."""
        return careful_to_bool(self._config.get("disable_on_ci", True), True)

    def use_dot_env(self) -> bool:
        """Look for a load .env"""
        return careful_to_bool(self._config.get("use_dot_env", True), True)

    @property
    def runtime_behavior_enabled(self) -> bool:
        """Check if runtime behavior is enabled based on the config."""
        return bool(self._config) and not careful_to_bool(
            self._config.get("disable_all_runtime_behavior", False), False
        )

    def modules_to_scan(self) -> list[str]:
        """Allows user to skip listing modules on CLI tool"""
        return [_.lower() for _ in self._config.get("modules", [])]

    def source_folders_to_scan(self) -> list[str]:
        """Allows user to skip listing src on CLI tool"""
        return [_.lower() for _ in self._config.get("src", [])]

    def active_schemas(self) -> list[str]:
        """Schemas to detect in source comments."""
        return [str(_).lower() for _ in self._config.get("active_schemas", [])]

    @classmethod
    def get_instance(cls, pyproject_path: str = "pyproject.toml") -> CodeTagsConfig:
        """Get the singleton instance of CodeTagsConfig."""
        if cls._instance is None:
            cls._instance = cls(pyproject_path)
        return cls._instance

    @classmethod
    def set_instance(cls, instance: CodeTagsConfig | None) -> None:
        """Set a custom instance of CodeTagsConfig."""
        cls._instance = instance


def get_code_tags_config() -> CodeTagsConfig:
    return CodeTagsConfig.get_instance()


if __name__ == "__main__":

    # ------------------------ USAGE EXAMPLES ------------------------

    # Lazy loading singleton config

    def example_usage() -> None:
        """Example usage of the CodeTagsConfig."""
        config = get_code_tags_config()
        if not config.runtime_behavior_enabled:
            print("Runtime behavior is disabled.")
            return

        print("Valid priorities:", config.valid_priorities())

    # Setting a custom or mock config for testing or alternate use
    class MockConfig(CodeTagsConfig):
        """Mock configuration for testing purposes."""

        def __init__(self, pyproject_path: str = "pyproject.toml"):
            super().__init__(pyproject_path)
            self._config = {"valid_priorities": ["urgent"], "disable_all_runtime_behavior": False}

    # Set the mock instance
    CodeTagsConfig.set_instance(MockConfig())

    # Now using get_code_tags_config will use the mock
    example_usage()

```

## File: view_tools.py

```python
"""
Like itertools, this is the functional programming code for list[TODO]
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable
from typing import Any


def group_and_sort(
    items: list[Any],
    key_fn: Callable[[Any], str],
    sort_items: bool = True,
    sort_key: Callable[[Any], Any] | None = None,
) -> dict[str, list[Any]]:
    """
    Groups and optionally sorts a list of items by a key function.

    Args:
        items: The list of items to group.
        key_fn: A function that returns the grouping key for an item.
        sort_items: Whether to sort the items within each group.
        sort_key: A custom sort key function for sorting items in each group.

    Returns:
        A dictionary mapping keys to lists of items.
        Keys with None or empty values are grouped under '(unlabeled)'.
    """
    grouped: dict[str, list[Any]] = defaultdict(list)

    for item in items:
        raw_key = key_fn(item)
        norm_key = str(raw_key).strip().lower() if raw_key else "(unlabeled)"
        grouped[norm_key].append(item)

    if sort_items:
        for norm_key, group in grouped.items():
            try:
                grouped[norm_key] = sorted(group, key=sort_key or key_fn)
            except Exception as e:
                raise ValueError(f"Failed to sort group '{norm_key}': {e}") from e

    return dict(sorted(grouped.items(), key=lambda x: x[0]))

```

## File: todo_tag_types_aliases.py

```python
"""
Aliases for TODO
"""

from __future__ import annotations

from pycodetags.todo_tag_types import TODO


def REQUIREMENT(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Factory function to create a REQUIREMENT item."""
    return TODO(
        code_tag="REQUIREMENT",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def STORY(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Variation on TODO"""
    return TODO(
        code_tag="STORY",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def IDEA(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Variation on TODO"""
    return TODO(
        code_tag="IDEA",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def FIXME(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """This is broken, please fix"""
    return TODO(
        code_tag="FIXME",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def BUG(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """This is broken, please fix"""
    return TODO(
        code_tag="BUG",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def HACK(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Make code quality better"""
    return TODO(
        code_tag="HACK",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def CLEVER(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Make code quality better"""
    return TODO(
        code_tag="CLEVER",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def MAGIC(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Make code quality better"""
    return TODO(
        code_tag="MAGIC",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def ALERT(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """An urgent TODO"""
    return TODO(
        code_tag="ALERT",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def PORT(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Make this work in more environments"""
    return TODO(
        code_tag="PORT",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )


def DOCUMENT(
    assignee: str | None = None,
    originator: str | None = None,
    comment: str | None = None,
    origination_date: str | None = None,
    due: str | None = None,
    release_due: str | None = None,
    release: str | None = None,
    iteration: str | None = None,
    change_type: str = "Added",
    closed_date: str | None = None,
    closed_comment: str | None = None,
    tracker: str | None = None,
    file_path: str | None = None,
    line_number: int | None = None,
    original_text: str | None = None,
    original_schema: str | None = None,
    custom_fields: dict[str, str] | None = None,
    priority: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> TODO:
    """Add documentation. The code tag itself is not documentation."""
    return TODO(
        code_tag="DOCUMENT",
        assignee=assignee,
        originator=originator,
        comment=comment,
        origination_date=origination_date,
        due=due,
        release_due=release_due,
        release=release,
        iteration=iteration,
        change_type=change_type,
        closed_date=closed_date,
        closed_comment=closed_comment,
        tracker=tracker,
        file_path=file_path,
        line_number=line_number,
        original_text=original_text,
        original_schema=original_schema,
        custom_fields=custom_fields,
        priority=priority,
        status=status,
        category=category,
    )

```

## File: todo_tag_types_generate_aliases.py

```python
"""
Generate main_types_aliases.py in a way that ensures intellisense works.
"""

import inspect
import textwrap
from dataclasses import field, fields
from typing import Any

from pycodetags.todo_tag_types import TODO


def generate_code_tags_file(output_filename: str = "main_types_aliases.py") -> None:
    """
    Generates a Python file containing the TODO dataclass and
    aliased factory functions with full IntelliSense support.
    """
    # --- 1. Define the TODO dataclass (or import it if it's in a separate file) ---
    # For this example, we'll embed the TODO definition for self-containment.
    # In a real project, you might import it from 'code_tags.main_types'.

    _temp_globals: dict[str, Any] = {}
    _TODO_cls = TODO

    # --- 2. Inspect TODO's fields for signature generation ---
    todo_init_fields = [f for f in fields(_TODO_cls) if f.init and f.name != "code_tag"]

    # Build the parameters string for the function signature
    params_str_parts = []
    for f in todo_init_fields:
        param_name = f.name
        param_type = inspect.formatannotation(f.type)  # Gets the string representation of the type

        # Handle default values
        if f.default is not field:
            # For simple defaults (strings, numbers, None)
            params_str_parts.append(f"{param_name}: {param_type} = {repr(f.default)}")
        elif f.default_factory is not field:
            # For default_factory, we can't put the factory in the signature directly.
            # Treat it as Optional and let the TODO constructor handle the default_factory.
            # Or you might omit it from the signature if it's always default-generated.
            # For IntelliSense, making it Optional[Type] is often best.
            if "None" not in param_type:  # Avoid double Optional or None | None
                params_str_parts.append(f"{param_name}: {param_type} | None = None")
            else:
                params_str_parts.append(f"{param_name}: {param_type} = None")
        else:
            # Required parameter with no default
            params_str_parts.append(f"{param_name}: {param_type}")

    # Add **kwargs to allow for future flexibility or passing through other arguments
    params_str = ", ".join(params_str_parts)
    if params_str:
        params_str += ", "
    # params_str += "**kwargs: Any"

    # Build the arguments string to pass to the TODO constructor
    args_to_pass = ", ".join([f"{f.name}={f.name}" for f in todo_init_fields])
    if args_to_pass:
        args_to_pass += ", "
    # args_to_pass += "**kwargs"

    # --- 3. Define the aliases and their corresponding code_tag values and docstrings ---
    aliases = {
        "REQUIREMENT": "Factory function to create a REQUIREMENT item.",
        "STORY": "Variation on TODO",
        "IDEA": "Variation on TODO",
        "FIXME": "This is broken, please fix",
        "BUG": "This is broken, please fix",
        "HACK": "Make code quality better",
        "CLEVER": "Make code quality better",
        "MAGIC": "Make code quality better",
        "ALERT": "An urgent TODO",
        "PORT": "Make this work in more environments",
        "DOCUMENT": "Add documentation. The code tag itself is not documentation.",
    }

    generated_alias_functions = []
    for alias_name, doc_string in aliases.items():
        func_code = textwrap.dedent(
            f"""
        def {alias_name}({params_str}) -> TODO:
            \"\"\"{doc_string}\"\"\"
            return TODO(code_tag="{alias_name}", {args_to_pass})
        """
        )
        generated_alias_functions.append(func_code)

    # --- 4. Assemble the full content of the output file ---
    full_output_content = ["\n\n".join(generated_alias_functions)]

    # --- 5. Write the content to the output file ---
    with open(output_filename, "w", encoding="utf-8") as file:
        file.write(
            """
\"\"\"
Aliases for TODO
\"\"\"
from __future__ import annotations

from typing import Any
from pycodetags.main_types import TODO
"""
        )
        file.write("\n\n".join(full_output_content))

    print(f"Successfully generated '{output_filename}' with IntelliSense-friendly aliases.")


if __name__ == "__main__":
    generate_code_tags_file()

```

## File: aggregate.py

```python
"""
Aggregate live module and source files for all known schemas
"""

from __future__ import annotations

import importlib
import logging
import logging.config
import pathlib

import pycodetags.folk_code_tags as folk_code_tags
import pycodetags.standard_code_tags as standard_code_tags
from pycodetags.collect import collect_all_todos
from pycodetags.collection_types import CollectedTODOs
from pycodetags.config import get_code_tags_config
from pycodetags.converters import convert_folk_tag_to_TODO, convert_pep350_tag_to_TODO
from pycodetags.plugin_manager import get_plugin_manager

logger = logging.getLogger(__name__)


def merge_collected(all_found: list[CollectedTODOs]) -> CollectedTODOs:
    merged: CollectedTODOs = {"todos": [], "exceptions": []}
    for found in all_found:
        merged["todos"] += found.get("todos", [])
        merged["exceptions"] += found.get("exceptions", [])
    return merged


def aggregate_all_kinds_multiple_input(module_names: list[str], source_paths: list[str]) -> CollectedTODOs:
    """Refactor to support lists of modules and lists of source paths"""
    if not module_names:
        module_names = []
    if not source_paths:
        source_paths = []
    collected: CollectedTODOs = {"todos": [], "exceptions": []}

    for module_name in module_names:
        found = aggregate_all_kinds(module_name, "")
        collected["todos"] += found["todos"]
        collected["exceptions"] += found["exceptions"]
    for source_path in source_paths:
        found = aggregate_all_kinds("", source_path)
        collected["todos"] += found["todos"]
        collected["exceptions"] += found["exceptions"]
    return collected


def aggregate_all_kinds(module_name: str, source_path: str) -> CollectedTODOs:
    """
    Aggregate all TODOs and DONEs from a module and source files.

    Args:
        module_name (str): The name of the module to search in.
        source_path (str): The path to the source files.

    Returns:
        CollectedTODOs: A dictionary containing collected TODOs, DONEs, and exceptions.
    """
    config = get_code_tags_config()

    active_schemas = config.active_schemas()
    all_schemas = False
    if not active_schemas:
        all_schemas = True

    pm = get_plugin_manager()
    found: CollectedTODOs = {}
    if bool(module_name):
        logging.info(f"Checking {module_name}")
        module = importlib.import_module(module_name)

        found = collect_all_todos(module, include_submodules=False, include_exceptions=True)

    found_folk_code_tags = []
    found_pep350_code_tags = []

    if source_path:
        src_found = 0
        path = pathlib.Path(source_path)
        files = [path] if path.is_file() else path.rglob("*.*")
        for file in files:
            if file.name.endswith(".py"):
                if all_schemas or "todo" in config.active_schemas():
                    found_pep350_code_tags.extend(
                        list(
                            convert_pep350_tag_to_TODO(_)
                            for _ in standard_code_tags.collect_pep350_code_tags(file=str(file))
                        )
                    )
                    src_found += 1

                if all_schemas or "folk" in config.active_schemas():
                    found_folk_code_tags.extend(
                        list(convert_folk_tag_to_TODO(_) for _ in folk_code_tags.find_source_tags(str(file)))
                    )
                    src_found += 1
            else:
                # Collect folk tags from plugins
                plugin_results = pm.hook.find_source_tags(
                    already_processed=False, file_path=str(file), config=get_code_tags_config()
                )
                for result_list in plugin_results:
                    found_folk_code_tags.extend(convert_folk_tag_to_TODO(tag) for tag in result_list)
                if plugin_results:
                    src_found += 1
        if src_found == 0:
            raise TypeError(f"Can't find any files in source folder {source_path}")

    folk_separated: CollectedTODOs = {"todos": found_folk_code_tags, "exceptions": []}
    pep30_separated = {"todos": found_pep350_code_tags, "exceptions": []}

    temp: CollectedTODOs = {}
    for thing in (folk_separated, pep30_separated, found):
        for key, value in thing.items():
            if key not in temp:
                # HACK: This is ugly.
                if key == "todos":
                    temp["todos"] = value  # type: ignore[typeddict-item]
                else:
                    temp["exceptions"] = value  # type: ignore[typeddict-item]
            else:
                if key == "todos":
                    temp["todos"].extend(value)  # type: ignore[arg-type]
                else:
                    temp["exceptions"].extend(value)  # type: ignore[arg-type]

    found = temp
    return found

```

## File: converters.py

```python
"""
Converters for FolkTag and PEP350Tag to TODO
"""

from __future__ import annotations

import logging

from pycodetags.data_tags import DataTag
from pycodetags.folk_code_tags import FolkTag
from pycodetags.todo_object_schema import TODO_KEYWORDS
from pycodetags.todo_tag_types import TODO

logger = logging.getLogger(__name__)


def blank_to_null(value: str | None) -> str | None:
    """
    Convert a blank string to None.

    Args:
        value (str | None): The value to convert.

    Returns:
        str | None: The converted value.
    """
    if isinstance(value, list):
        return [_.strip() for _ in value]
    if value is None or value.strip() == "":
        return None
    return value.strip()


def convert_folk_tag_to_TODO(folk_tag: FolkTag) -> TODO:
    """
    Convert a FolkTag to a TODO object.

    Args:
        folk_tag (FolkTag): The FolkTag to convert.
    """
    kwargs = {
        "code_tag": folk_tag.get("code_tag"),
        "file_path": folk_tag.get("file_path"),
        "line_number": folk_tag.get("line_number"),
        # folk_tag.get("default_field"),
        "custom_fields": folk_tag.get("custom_fields"),
        "comment": folk_tag["comment"],  # required
        "tracker": folk_tag.get("tracker"),
        "assignee": blank_to_null(folk_tag.get("assignee")),
        "originator": blank_to_null(folk_tag.get("originator")),
        # person=folk_tag.get("person")
        "original_text": folk_tag.get("original_text"),
        "original_schema": "folk",
    }
    custom_fields = folk_tag.get("custom_fields", {})
    for keyword in TODO_KEYWORDS:
        for field_key, field_value in custom_fields.items():
            # Promote custom fields to kwargs if they match the keyword
            # and the keyword is not already in kwargs
            if keyword == field_key and keyword not in kwargs:
                kwargs[keyword] = field_value
            if keyword == field_key and keyword not in kwargs:
                logger.warning("Duplicate keyword found in custom fields: %s", keyword)
    return TODO(**kwargs)  # type: ignore[arg-type]


def convert_pep350_tag_to_TODO(pep350_tag: DataTag) -> TODO:
    """
    Convert a PEP350Tag to a TODO object.

    Args:
        pep350_tag (PEP350Tag): The PEP350Tag to convert.
    """
    # default fields should have already been promoted to data_fields by now.
    data_fields = pep350_tag["fields"]["data_fields"]
    custom_fields = pep350_tag["fields"]["custom_fields"]
    kwargs = {
        "code_tag": pep350_tag["code_tag"],
        "comment": pep350_tag["comment"],
        "custom_fields": custom_fields,
        # specific fields
        "assignee": blank_to_null(data_fields.get("assignee")),
        "originator": blank_to_null(data_fields.get("originator")),
        # due dates
        "due": data_fields.get("due"),
        "iteration": data_fields.get("iteration"),
        "release": data_fields.get("release"),
        # integrations
        "tracker": data_fields.get("tracker"),
        # idiosyncratic
        "priority": data_fields.get("priority"),
        "status": data_fields.get("status"),
        "category": data_fields.get("category"),
        # Source Mapping
        "file_path": data_fields.get("file_path"),
        "line_number": data_fields.get("line_number"),
        "original_text": pep350_tag.get("original_text"),
        "original_schema": "pep350",
    }

    custom_fields = pep350_tag["fields"].get("custom_fields", {})
    for keyword in TODO_KEYWORDS:
        for field_key, field_value in custom_fields.items():
            # Promote custom fields to kwargs if they match the keyword
            # and the keyword is not already in kwargs
            if keyword == field_key and keyword not in kwargs:
                kwargs[keyword] = field_value
            if keyword == field_key and keyword not in kwargs:
                logger.warning("Duplicate keyword found in custom fields: %s", keyword)

    return TODO(**kwargs)  # type: ignore[arg-type]

```

## File: comment_finder.py

```python
from __future__ import annotations

import logging
from ast import walk
from collections.abc import Generator
from pathlib import Path
from typing import Any

try:
    from ast_comments import Comment, parse
except ImportError:
    Comment: Any = None  # type: ignore[no-redef]
    parse: Any = None  # type: ignore[no-redef]

LOGGER = logging.getLogger(__name__)


def find_comment_blocks(path: Path) -> Generator[tuple[int, int, int, int, str], None, None]:
    """Parses a Python source file and yields comment block ranges.

    Uses `ast-comments` to locate all comments, and determines the exact offsets
    for each block of contiguous comments.

    Args:
        path (Path): Path to the Python source file.

    Yields:
        Tuple[int, int, int, int, str]: (start_line, start_char, end_line, end_char, comment)
        representing the comment block's position in the file (0-based).
    """
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix != ".py":
        raise ValueError(f"Expected a Python file (.py), got: {path.suffix}")

    source = path.read_text(encoding="utf-8")
    tree = parse(source)
    lines = source.splitlines()

    # Filter out comment nodes
    # BUG, fails to walk the whole tree. This is shallow.
    comments = [node for node in walk(tree) if isinstance(node, Comment)]

    def comment_pos(comment: Comment) -> tuple[int, int, int, int]:
        """Get the position of a comment as (start_line, start_char, end_line, end_char)."""
        for i, line in enumerate(lines):
            idx = line.find(comment.value)
            if idx != -1:
                return (i, idx, i, idx + len(comment.value))
        raise ValueError(f"Could not locate comment in source: {comment.value}")

    # Group comments into blocks
    block: list[tuple[int, int, int, int]] = []

    for comment in comments:
        pos = comment_pos(comment)

        if not block:
            block.append(pos)
        else:
            prev_end_line = block[-1][2]
            if pos[0] == prev_end_line + 1:
                # Consecutive line: extend block
                block.append(pos)
            else:
                # Yield previous block
                start_line, start_char, _, _ = block[0]
                end_line, _, _, end_char = block[-1]
                final_comment = extract_comment_text(source, (start_line, start_char, end_line, end_char))
                yield (start_line, start_char, end_line, end_char, final_comment)
                block = [pos]

    if block:
        start_line, start_char, _, _ = block[0]
        end_line, _, _, end_char = block[-1]
        final_comment = extract_comment_text(source, (start_line, start_char, end_line, end_char))
        yield (start_line, start_char, end_line, end_char, final_comment)


def extract_comment_text_from_file(path: Path, offsets: tuple[int, int, int, int]) -> str:
    return extract_comment_text(path.read_text(encoding="utf-8"), offsets)


def extract_comment_text(text: str, offsets: tuple[int, int, int, int]) -> str:
    """Extract the comment text from a file given start/end line/char offsets.

    Args:
        text (str): text of source code
        offsets (tuple): A tuple of (start_line, start_char, end_line, end_char),
            all 0-based.

    Returns:
        str: The exact substring from the file containing the comment block.
    """
    start_line, start_char, end_line, end_char = offsets

    lines = text.splitlines()

    if start_line == end_line:
        return lines[start_line][start_char:end_char]

    # Multi-line block
    block_lines = [lines[start_line][start_char:]]
    for line_num in range(start_line + 1, end_line):
        block_lines.append(lines[line_num])
    block_lines.append(lines[end_line][:end_char])

    return "\n".join(block_lines)


def find_comment_blocks_fallback(path: Path) -> Generator[tuple[int, int, int, int, str], None, None]:
    """Parse a Python file and yield comment block positions and content.

    Args:
        path (Path): Path to the Python source file.

    Yields:
        Tuple[int, int, int, int, str]: A tuple of (start_line, start_char, end_line, end_char, comment)
        representing the block's location and the combined comment text. All indices are 0-based.
    """
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {path}")
    if path.suffix != ".py":
        raise ValueError(f"Expected a Python file (.py), got: {path.suffix}")

    LOGGER.info("Reading Python file: %s", path)

    with path.open("r", encoding="utf-8") as f:
        lines = f.readlines()

    in_block = False
    start_line = start_char = 0
    end_line = end_char = 0
    comment_lines: list[str] = []

    for idx, line in enumerate(lines):
        line_wo_newline = line.rstrip("\n")
        comment_pos = line.find("#")

        if comment_pos != -1:
            if not in_block:
                # Start a new block
                in_block = True
                start_line = idx
                start_char = comment_pos
                comment_lines = []
                LOGGER.debug("Starting comment block at line %d, char %d", start_line, start_char)

            end_line = idx
            end_char = len(line_wo_newline)
            comment_lines.append(line_wo_newline[comment_pos:])

            # Check if next line is non-comment or this is a standalone inline comment
            next_line = lines[idx + 1] if idx + 1 < len(lines) else ""
            next_comment_pos = next_line.find("#")
            next_stripped = next_line.strip()

            if not next_stripped or next_comment_pos == -1:
                # End of comment block
                comment_text = "\n".join(comment_lines)
                LOGGER.debug("Ending comment block at line %d, char %d", end_line, end_char)
                yield (start_line, start_char, end_line, end_char, comment_text)
                in_block = False

        else:
            if in_block:
                # Previous line had comment, current one doesn't: close block
                comment_text = "\n".join(comment_lines)
                LOGGER.debug("Ending comment block at line %d, char %d", end_line, end_char)
                yield (start_line, start_char, end_line, end_char, comment_text)
                in_block = False

    if in_block:
        comment_text = "\n".join(comment_lines)
        LOGGER.debug("Ending final comment block at line %d, char %d", end_line, end_char)
        yield (start_line, start_char, end_line, end_char, comment_text)


if parse is None:
    # Hack for 3.7!
    find_comment_blocks = find_comment_blocks_fallback  # type: ignore[no-redef,unused-ignore]

```

## File: dotenv.py

```python
"""
.env file support to avoid another dependency.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def _strip_inline_comment(value: str) -> str:
    """Strip unquoted inline comments starting with '#'."""
    result = []
    in_single = in_double = False

    for i, char in enumerate(value):
        if char == "'" and not in_double:
            in_single = not in_single
        elif char == '"' and not in_single:
            in_double = not in_double
        elif char == "#" and not in_single and not in_double:
            logger.debug(f"Stripping inline comment starting at index {i}")
            break
        result.append(char)
    return "".join(result).strip()


def _unquote(value: str) -> str:
    """Remove surrounding quotes from a string if they match."""
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    return value


def load_dotenv(file_path: Path | None = None) -> None:
    """Load environment variables from a .env file into os.environ.

    Args:
        file_path (Optional[Path]): Optional custom path to a .env file.
            If not provided, defaults to ".env" in the current working directory.

    Notes:
        - Lines that are blank, comments (starting with #), or shebangs (#!) are ignored.
        - Lines must be in the form of `KEY=VALUE` or `export KEY=VALUE`.
        - Existing environment variables will not be overwritten.
        - Inline comments (starting with unquoted #) are stripped.
        - Quoted values are unwrapped.
    """
    if file_path is None:
        file_path = Path.cwd() / ".env"

    logger.info(f"Looking for .env file at: {file_path}")

    if not file_path.exists():
        logger.warning(f".env file not found at: {file_path}")
        return

    logger.info(".env file found. Starting to parse...")

    with file_path.open("r", encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            original_line = line.rstrip("\n")
            line = line.strip()

            logger.debug(f"Line {line_number}: '{original_line}'")

            if not line or line.startswith("#") or line.startswith("#!") or line.startswith("!/"):
                logger.debug(f"Line {line_number} is blank, a comment, or a shebang. Skipping.")
                continue

            if line.startswith("export "):
                line = line[len("export ") :].strip()

            if "=" not in line:
                logger.warning(f"Line {line_number} is not a valid assignment. Skipping: '{original_line}'")
                continue

            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if not key:
                logger.warning(f"Line {line_number} has empty key. Skipping: '{original_line}'")
                continue

            value = _strip_inline_comment(value)
            value = _unquote(value)

            if key in os.environ:
                logger.info(f"Line {line_number}: Key '{key}' already in os.environ. Skipping.")
                continue

            os.environ[key] = value
            logger.info(f"Line {line_number}: Loaded '{key}' = '{value}'")


if __name__ == "__main__":
    load_dotenv()

```

## File: todo_tag_types.py

```python
"""
Strongly typed code tag types.
"""

from __future__ import annotations

import datetime
import logging
import os
import warnings
from collections.abc import Callable
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, cast

from pycodetags.data_tag_types import DATA
from pycodetags.specific_schemas import PEP350Schema

try:
    from typing import Literal  # type:ignore[assignment,unused-ignore]
except ImportError:
    from typing import Literal  # type:ignore[assignment,unused-ignore]

from pycodetags.config import get_code_tags_config
from pycodetags.todo_object_schema import TODO_KEYWORDS

logger = logging.getLogger(__name__)


class TodoException(Exception):
    """Exception raised when a required feature is not implemented."""

    def __init__(self, message: str, assignee: str | None = None, due: str | None = None):
        super().__init__(message)
        self.assignee = assignee
        self.due = due
        self.message = message
        # Needs same fields as TODO

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the object to a dictionary representation.
        """
        d = self.__dict__.copy()
        for key, value in list(d.items()):
            if isinstance(value, datetime.datetime):
                d[key] = value.isoformat()
            if key.startswith("_"):
                del d[key]
            if key == "todo_meta":
                del d[key]
        return d


# class Serializable:
#     """A base class for objects that can be serialized to a dictionary."""
#
#     def to_dict(self) -> dict[str, Any]:
#         """
#         Convert the object to a dictionary representation.
#         """
#         d = self.__dict__.copy()
#         for key, value in list(d.items()):
#             if isinstance(value, datetime.datetime):
#                 d[key] = value.isoformat()
#             if key.startswith("_"):
#                 del d[key]
#             if key == "todo_meta":
#                 del d[key]
#         return d


def parse_due_date(date_str: str) -> datetime.datetime:
    """
    Parses a date string in the format 'YYYY-MM-DD' and returns a datetime object.

    Args:
        date_str (str): The date string to parse.

    Returns:
        datetime.datetime: The parsed datetime object.

    Raises:
        ValueError: If the date string is not in the format 'YYYY-MM-DD'.

    Examples:
        >>> parse_due_date("2023-10-01")
        datetime.datetime(2023, 10, 1, 0, 0)

        >>> parse_due_date("invalid-date")
        Traceback (most recent call last):
        ...
        ValueError: Invalid date format for due_date: 'invalid-date'. Use YYYY-MM-DD.
    """
    try:
        return datetime.datetime.strptime(date_str, "%Y-%m-%d")
    except Exception as e:
        raise ValueError(f"Invalid date format for due_date: '{date_str}'. Use YYYY-MM-DD.") from e


@dataclass
class TODO(DATA):
    """
    Represents a TODO item with various metadata fields.
    """

    assignee: str | None = None
    """User who will do the work"""
    originator: str | None = None
    """User who created the issue"""

    # Due fields
    origination_date: str | None = None
    """Date issue created in YYYY-MM-DD format"""
    due: str | None = None
    """Date issue will be done in YYYY-MM-DD format"""
    release_due: str | None = None
    """Release due, will attempt to parse as semantic version A.B.C"""
    release: str | None = None
    """Release completed, will attempt to parse as semantic version A.B.C"""
    iteration: str | None = None
    """User specified meaning, a milestone in a release"""

    # Done fields
    change_type: str | None = None
    """Field for Keepachangelog support"""
    closed_date: str | None = None
    """Date issue closed in YYYY-MM-DD format"""
    closed_comment: str | None = None

    # Integration fields
    tracker: str | None = None
    """A URL or Issue as determined by config or URL detection"""

    priority: str | None = None
    """User specified meaning, urgency of task"""
    status: str | None = None
    """Done, plus other user specified values"""
    category: str | None = None
    """User specified meaning, any useful categorization of issues"""

    # Internal state
    _due_date_obj: datetime.datetime | None = field(init=False, default=None)
    """Strongly typed due_date"""

    todo_meta: TODO | None = field(init=False, default=None)
    """Necessary internal field for decorators"""

    def disable_behaviors(self) -> bool:
        """Don't do anything because we are in CI, production, end users machine or we just aren't using
        the action feature
        """
        config = get_code_tags_config()
        if (
            config.disable_all_runtime_behavior()
            or not config.enable_actions()
            or config.disable_on_ci()
            and "CI" in os.environ
        ):
            return True
        return False

    def __post_init__(self) -> None:
        """
        Validation and complex initialization
        """
        if self.disable_behaviors():
            return

        if self.due:
            # TODO: find better way to upgrade string to strong type.
            try:
                parsed_date = parse_due_date(self.due)
                self._due_date_obj = parsed_date
            except ValueError:
                pass

        self.todo_meta = self

    def is_probably_done(self) -> bool:
        config = get_code_tags_config()
        date_is_done = bool(self.closed_date)
        status_is_done = bool(self.status) and (self.status or "").lower() in config.closed_status()

        return date_is_done or status_is_done

    @property
    def current_user(self) -> str:
        config = get_code_tags_config()
        return config.current_user()

    def _is_condition_met(self) -> bool:
        """Checks if the conditions for triggering an action are met."""
        if self.disable_behaviors():
            return False

        is_past_due = bool(self._due_date_obj and datetime.datetime.now() > self._due_date_obj)

        user_matches = self.assignee.lower() == self.current_user.lower() if self.assignee else False
        config = get_code_tags_config()

        on_past_due = config.action_on_past_due()
        only_on_user_match = config.action_only_on_responsible_user()

        if on_past_due and not only_on_user_match:
            return is_past_due and user_matches
        if on_past_due:
            return is_past_due
        if only_on_user_match and user_matches:
            return user_matches
        return False

    def _perform_action(self) -> None:
        """Performs the configured action if conditions are met."""
        if self.disable_behaviors():
            return

        if self._is_condition_met():
            config = get_code_tags_config()
            action = config.default_action().lower()
            message = f"TODO Reminder: {self.comment} (assignee: {self.assignee}, due: {self.due})"
            if action == "stop":
                raise TodoException(message, assignee=self.assignee, due=self.due)
            if action == "warn":
                warnings.warn(message, stacklevel=3)

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            self._perform_action()
            return cast(Callable[..., Any], func(*args, **kwargs))

        cast(Any, wrapper).todo_meta = self
        return wrapper

    def __enter__(self) -> TODO:
        self._perform_action()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> Literal[False]:
        return False  # propagate exceptions

    def validate(self) -> list[str]:
        """Validates the TODO item.

        Only developer tooling should call this.
        """
        config = get_code_tags_config()

        issues = []
        # Required if done to support features
        if self.is_probably_done():
            if not self.assignee:
                issues.append("Item is done, missing assignee")
            if not self.release:
                valid_releases = config.valid_releases()
                if valid_releases:
                    issues.append(f"Item is done, missing release, suggest {valid_releases}")
                else:
                    issues.append("Item is done, missing release (version number)")
            if not self.closed_date:
                issues.append(f"Item is done, missing closed date, suggest {datetime.datetime.now()}")

        # TODO: check for mandatory fields
        mandatory_fields = config.mandatory_fields()
        if mandatory_fields:
            for mandatory_field in mandatory_fields:
                if not getattr(self, mandatory_field):
                    issues.append(f"{mandatory_field} is required")

        # Authors from config.
        # TODO: Implement authors from files
        authors_list = config.valid_authors()
        if authors_list:
            for person in (self.originator, self.assignee):
                if person and person.lower() not in authors_list:
                    issues.append(f"Person '{person}' is not on the valid authors list")

        # TODO: Implement release/version from files
        release_list = config.valid_releases()
        if release_list:
            if self.release and self.release not in release_list:
                issues.append(f"Release '{self.release}' is not on the valid release list {release_list}")

        # TODO: Implement release/version from files

        valid_change_list = ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]
        if self.is_probably_done():
            if (self.change_type or "").lower().strip() not in [_.lower() for _ in valid_change_list]:
                issues.append(f"change_type '{self.change_type}' is not on the valid list {valid_change_list}")

        # Zero business logic checks

        valid_lists_meta = {
            "status": config.valid_status,
            "priority": config.valid_priorities,
            "iteration": config.valid_iterations,
            "category": config.valid_categories,
        }

        for valid_field, valid_list_func in valid_lists_meta.items():
            valid_list = valid_list_func()
            if valid_list:
                value = getattr(self, valid_field)
                if value is None:
                    value = ""
                if value.lower() not in valid_list + [""]:
                    issues.append(f"Invalid {valid_field} {value}, valid {valid_field} {valid_list}")

        custom_fields_list = config.valid_custom_field_names()
        if custom_fields_list:
            if self.custom_fields:
                for custom_field in self.custom_fields:
                    if custom_field.lower() not in custom_fields_list:
                        issues.append(
                            f"Custom field '{custom_field}' is not on the valid custom field list {custom_fields_list}"
                        )

        # Plugin-based validation
        plugin_issues: list[str] = []

        # pylint: disable=import-outside-toplevel
        from pycodetags.plugin_manager import get_plugin_manager

        for new_issues in get_plugin_manager().hook.code_tags_validate_todo(
            todo_item=self, config=get_code_tags_config()
        ):
            plugin_issues += new_issues
            issues.extend(plugin_issues)

        return issues

    def as_pep350_comment(self) -> str:
        """Print as if it was a PEP-350 comment.
        Upgrades folk schema to PEP-350
        """
        # self._extract_data_fields()

        # default fields
        if self.default_fields is None:
            self.default_fields = {}

        if self.data_fields is None:
            self.data_fields = {}
        if self.custom_fields is None:
            self.custom_fields = {}

        for _, name in PEP350Schema["default_fields"].items():
            value = getattr(self, name)
            if value is not None:
                self.default_fields[name] = value

        # data_fields
        for name in TODO_KEYWORDS:
            value = getattr(self, name)
            if value is not None:
                self.data_fields[name] = value

        return self.as_data_comment()

```

## File: specific_schemas.py

```python
from pycodetags.data_tags import DataTagSchema

PEP350Schema: DataTagSchema = {
    "default_fields": {"str": "assignee", "date": "origination_date"},
    "data_fields": {
        "priority": "priority",
        "due": "due",
        "tracker": "tracker",
        "status": "status",
        "category": "category",
        "iteration": "iteration",
        "release": "release",
        "assignee": "assignee",
        "originator": "originator",
    },
    "data_field_aliases": {
        "p": "priority",
        "d": "due",
        "t": "tracker",
        "s": "status",
        "c": "category",
        "i": "iteration",
        "r": "release",
        "a": "assignee",
    },
}

```

## File: todo_object_schema.py

```python
"""
Extract to break cyclical import
"""

TODO_KEYWORDS = [
    # People
    "assignee",
    "originator",
    # Dates
    "origination_date",
    "due",
    "closed_date",
    # Version number
    "release_due",
    "release",
    # keepachangelog field, done fields
    "change_type",
    # integration fields
    "tracker",
    # custom workflow fields
    # Source Mapping
    "file_path",
    "line_number",
    "custom_fields",
    # Idiosyncratic fields
    "iteration",
    "priority",
    "status",
    "category",
]

```

## File: plugin_manager.py

```python
import logging

import pluggy

from pycodetags.plugin_specs import CodeTagsSpec

logger = logging.getLogger(__name__)

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

```

## File: users_from_authors.py

```python
"""
Author file parsing.
"""

from __future__ import annotations

import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)


def parse_authors_file_simple(file_path: str) -> list[str]:
    """Parses an AUTHORS file to extract unique author names."""
    authors = set()
    for item in parse_authors_file(file_path):
        for _, value in item.items():
            authors.add(value)
    return list(authors)


def parse_authors_file(file_path: str) -> list[dict[str, str | Any]]:
    """
    Parses an AUTHORS file, attempting to extract names and emails.
    Handles common formats but is flexible due to the "folk schema" nature.

    Args:
        file_path (str): The path to the AUTHORS file.

    Returns:
        list: A list of dictionaries, where each dictionary represents an author
              and may contain 'name' and 'email' keys.
    """
    authors = []
    # Regex to capture name and optional email
    # Groups: 1=name, 2=email (if present)
    author_pattern = re.compile(r"^\s*(.*?)(?:\s+<([^>]+)>)?\s*$")

    with open(file_path, encoding="utf-8") as file_handle:
        for line in file_handle:
            line = line.strip()
            if not line or line.startswith("#"):  # Skip empty lines and comments
                continue

            match = author_pattern.match(line)
            if match:
                name = match.group(1).strip()
                email = match.group(2)

                author_info = {"name": name}
                if email:
                    author_info["email"] = email.strip()
                authors.append(author_info)
            else:
                # If a line doesn't match the common pattern, you might
                # want to log it or handle it differently.
                # For simplicity, we'll just add the whole line as a name.
                authors.append({"name": line})
                print(f"Warning: Could not fully parse line: '{line}'")

    return authors


# --- Example Usage ---
if __name__ == "__main__":

    def example() -> None:
        """
        Example function to demonstrate how to use the parse_authors_file function.
        """
        # Create a dummy AUTHORS file for testing
        dummy_authors_content = """
# Project Contributors

John Doe <john.doe@example.com>
Jane Smith
Alice Wonderland <alice@wonderland.org>
Bob The Builder (Maintenance Lead)
    # A comment line
Charlie Chaplin
    """
        with open("AUTHORS_test.txt", "w", encoding="utf-8") as f:
            f.write(dummy_authors_content.strip())

        parsed_authors = parse_authors_file("AUTHORS_test.txt")

        print("Parsed Authors:")
        for author in parsed_authors:
            print(author)

        os.remove("AUTHORS_test.txt")

    example()

```

## File: data_tag_types.py

```python
"""
Strongly typed data tags, base for all code tags
"""

from __future__ import annotations

import datetime
import logging
from collections.abc import Callable
from dataclasses import dataclass, field, fields
from functools import wraps
from typing import Any, cast

try:
    from typing import Literal  # type: ignore[assignment,unused-ignore]
except ImportError:
    from typing import Literal  # type: ignore[assignment,unused-ignore]

logger = logging.getLogger(__name__)


class Serializable:
    """A base class for objects that can be serialized to a dictionary."""

    def to_dict(self) -> dict[str, Any]:
        """
        Convert the object to a dictionary representation.
        """
        d = self.__dict__.copy()
        for key, value in list(d.items()):
            if isinstance(value, datetime.datetime):
                d[key] = value.isoformat()
            if key.startswith("_"):
                del d[key]
            if key == "todo_meta":
                del d[key]
        return d


@dataclass
class DATA(Serializable):
    """
    Represents a data record that can be serialized into python source code comments.
    """

    code_tag: str | None = "DATA"
    """Capitalized tag name"""
    comment: str | None = None
    """Unstructured text"""

    # Derived classes will have properties/fields for each data_field.
    # assignee: str

    # Custom workflow
    default_fields: dict[str, str] | None = None
    data_fields: dict[str, str] | None = None
    custom_fields: dict[str, str] | None = None
    strict: bool = False

    # Source mapping, original parsing info
    file_path: str | None = None
    line_number: int | None = None
    original_text: str | None = None
    original_schema: str | None = None
    offsets: tuple[int, int, int, int] | None = None

    data_meta: DATA | None = field(init=False, default=None)
    """Necessary internal field for decorators"""

    def __post_init__(self) -> None:
        """
        Validation and complex initialization
        """
        self.data_meta = self

    def _perform_action(self) -> None:
        """
        Hook for performing an action when used as a decorator or context manager.
        Override in subclasses.
        """

    def __call__(self, func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Callable[..., Any]:
            self._perform_action()
            return cast(Callable[..., Any], func(*args, **kwargs))

        cast(Any, wrapper).todo_meta = self
        return wrapper

    def __enter__(self) -> DATA:
        # self._perform_action()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: Any,
    ) -> Literal[False]:
        return False  # propagate exceptions

    # overridable?
    def validate(self) -> list[str]:
        """Validates the Data item."""
        return []

    def _extract_data_fields(self) -> dict[str, str]:
        d = {}
        for f in fields(self):
            # only data_fields, default_fields are strongly typed
            if f.name in ("data_fields", "default_fields"):
                continue
            val = getattr(self, f.name)
            # BUG: ignores if field is both data/default
            if val is not None:
                if isinstance(val, datetime.datetime):
                    d[f.name] = val.isoformat()
                else:
                    d[f.name] = str(val)
        return d

    def as_data_comment(self) -> str:
        """Print as if it was a PEP-350 comment."""
        the_fields = ""
        to_skip = []
        if self.default_fields:
            for key, value in self.default_fields.items():
                to_skip.append(key)
                if isinstance(value, list) and len(value) == 1:
                    value = value[0]
                elif isinstance(value, list):
                    value = ",".join(value)
                the_fields += f"{value} "

        for field_set in (self.custom_fields, self.data_fields):
            if field_set:
                for key, value in field_set.items():

                    if value and key != "custom_fields" and key not in to_skip:
                        if isinstance(value, list) and len(value) == 1:
                            value = value[0]
                        elif isinstance(value, list):
                            value = ",".join(value)
                        else:
                            value = str(value)
                        if " " in value and "'" in value and '"' in value:
                            value = f'"""{value}"""'
                        elif " " in value and '"' not in value:
                            value = f'"{value}"'
                        elif " " in value and "'" not in value:
                            value = f"'{value}'"
                        elif ":" in value or "=" in value:
                            value = f'"{value}"'

                        the_fields += f"{key}:{value} "

        first_line = f"# {(self.code_tag or '').upper()}: {self.comment}"
        complete = f"{first_line} <{the_fields.strip()}>"
        if len(complete) > 80:
            first_line += "\n# "
            complete = f"{first_line}<{the_fields.strip()}>"
        return complete

```

## File: plugin_specs.py

```python
"""
Pluggy supports
"""

from __future__ import annotations

# pylint: disable=unused-argument
import argparse

import pluggy

from pycodetags.collection_types import CollectedTODOs
from pycodetags.config import CodeTagsConfig
from pycodetags.folk_code_tags import FolkTag
from pycodetags.todo_tag_types import TODO

hookspec = pluggy.HookspecMarker("pycodetags")


class CodeTagsSpec:
    """A hook specification namespace for pycodetags."""

    @hookspec
    def code_tags_print_report(
        self, format_name: str, found_data: CollectedTODOs, output_path: str, config: CodeTagsConfig
    ) -> bool:
        """
        Allows plugins to define new output report formats.

        Args:
            format_name: The name of the report format to print.
            found_data: The CollectedTODOs data to be printed.
            output_path: The path where the report should be saved.
            config: The CodeTagsConfig instance containing configuration settings.

        Returns:
            bool: True if the plugin handled the report printing, False otherwise.
        """
        return False

    @hookspec
    def code_tags_print_report_style_name(self) -> list[str]:
        """
        Allows plugins announce report format names.

        Returns:
            List of supported format
        """
        return []

    @hookspec
    def code_tags_add_cli_subcommands(self, subparsers: argparse._SubParsersAction) -> None:  # type: ignore[type-arg]
        """
        Allows plugins to add new subcommands to the pycodetags CLI.

        Args:
            subparsers (argparse._SubParsersAction): The ArgumentParser subparsers object to add subcommands to.
        """

    @hookspec
    def code_tags_run_cli_command(
        self, command_name: str, args: argparse.Namespace, found_data: CollectedTODOs, config: CodeTagsConfig
    ) -> bool:
        """
        Allows plugins to handle the execution of their registered CLI commands.

        Args:
            command_name: The name of the command to run.
            args: The parsed arguments for the command.
            found_data: The CollectedTODOs data to be processed.
            config: The CodeTagsConfig instance containing configuration settings.

        Returns:
            bool: True if the command was handled by the plugin, False otherwise.
        """
        return False

    @hookspec
    def code_tags_validate_todo(self, todo_item: TODO, config: CodeTagsConfig) -> list[str]:
        """
        Allows plugins to add custom validation logic to TODO items.

        Args:
            todo_item: The TODO item to validate.
            config: The CodeTagsConfig instance containing configuration settings.

        Returns:
            List of validation error messages.
        """
        return []

    @hookspec
    def find_source_tags(self, already_processed: bool, file_path: str, config: CodeTagsConfig) -> list[FolkTag]:
        """
        Allows plugins to provide folk-style code tag parsing for non-Python source files.

        Args:
            already_processed: first pass attempt to find all tags. Be careful of duplicates.
            file_path: The path to the source file.
            config: The CodeTagsConfig instance containing configuration settings.

        Returns:
            A list of FolkTag dictionaries.
        """
        return []

    @hookspec
    def file_handler(self, already_processed: bool, file_path: str, config: CodeTagsConfig) -> bool:
        """
        Allows plugins to do something with source file.

        Args:
            already_processed: Indicates if the file has been processed before.
            file_path: The path to the source file.
            config: The CodeTagsConfig instance containing configuration settings.

        Returns:
            True if file processed by plugin
        """
        return False

```

## File: folk_code_tags.py

```python
"""
Finds all folk schema tags in source files.

Folk tags roughly follow

# TODO: comment
# TODO(user): comment
# TODO(ticket): comment
# TODO(default_field): Message with domain.com/ticket-123

Optionally

# TODO: Multiline
# comment

Valid tags lists are important for doing looser parsing, e.g. omitting colon, multiline, lowercase etc.

Not sure if I will implement completely loose parsing.
"""

from __future__ import annotations

import logging
import os
import re

try:
    from typing import Literal, TypedDict  # type: ignore[assignment,unused-ignore]
except ImportError:
    from typing import Literal  # type: ignore[assignment,unused-ignore]

    from typing_extensions import TypedDict


logger = logging.getLogger(__name__)

DefaultFieldMeaning = Literal[
    "person",  # accurate because who knows what that name in parens means
    "assignee",
    "originator",  # compatible with pep350
    "tracker",
]


class FolkTag(TypedDict, total=False):
    """Represents a folk tag found in source code."""

    # data
    file_path: str
    line_number: int
    start_char: int
    # data
    code_tag: str
    default_field: str | None
    custom_fields: dict[str, str]
    comment: str
    tracker: str
    assignee: str
    originator: str
    person: str
    original_text: str


def folk_tag_to_comment(tag: FolkTag) -> str:
    """Convert a FolkTag to a comment string."""
    people_text = ""
    custom_field_text = ""
    if tag.get("assignee") or tag.get("originator"):
        people = ",".join(_ for _ in (tag.get("assignee", ""), tag.get("originator", "")) if _)
        people.strip(", ")
        if people:
            people_text = f"({people.strip()})"
    if tag["custom_fields"]:

        for key, value in tag["custom_fields"].items():
            custom_field_text += f"{key}={value.strip()} "
        custom_field_text = f"({custom_field_text.strip()}) "

    return f"# {tag['code_tag'].upper()}{people_text}: {custom_field_text}{tag['comment'].strip()}".strip()


def find_source_tags(
    source_path: str,
    valid_tags: list[str] | None = None,
    allow_multiline: bool = False,
    default_field_meaning: DefaultFieldMeaning = "assignee",
) -> list[FolkTag]:
    """
    Finds all folk tags in the source files.

    Args:
        source_path (str): Path to the source file or directory.
        valid_tags (list[str], optional): List of valid code tags to look for. If None, all tags are considered valid.
        allow_multiline (bool, optional): Whether to allow multiline comments. Defaults to False.
        default_field_meaning (DefaultFieldMeaning, optional): Meaning of the default field. Defaults to "assignee".

    Returns:
        list[FolkTag]: A list of FolkTag dictionaries found in the source files.
    """
    if allow_multiline and not valid_tags:
        raise TypeError("Must include valid tag list if you want to allow multiline comments")

    if not valid_tags:
        valid_tags = []

    found_tags: list[FolkTag] = []

    if not os.path.exists(source_path):
        raise FileNotFoundError(f"The path '{source_path}' does not exist.")

    if os.path.isfile(source_path):
        files_to_scan = [source_path]
    else:
        files_to_scan = []
        for root, _, files in os.walk(source_path):
            for file in files:
                files_to_scan.append(os.path.join(root, file))

    for file_path in files_to_scan:
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            idx = 0
            while idx < len(lines):
                consumed = process_line(
                    file_path, found_tags, lines, idx, valid_tags, allow_multiline, default_field_meaning
                )
                idx += consumed

    return found_tags


def extract_first_url(text: str) -> str | None:
    """
    Extracts the first URL from a given text.

    Args:
        text (str): The text to search for URLs.

    Returns:
        str | None: The first URL found in the text, or None if no URL is found.
    """
    # Regex pattern to match URLs with or without scheme
    pattern = r"(https?://[^\s]+|[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/[^\s]+)"
    match = re.search(pattern, text)
    return match.group(0) if match else None


def process_line(
    file_path: str,
    found_tags: list[FolkTag],
    lines: list[str],
    start_idx: int,
    valid_tags: list[str],
    allow_multiline: bool,
    default_field_meaning: DefaultFieldMeaning,
) -> int:
    """
    Processes a single line to find and parse folk tags.

    Args:
        file_path (str): Path to the source file.
        found_tags (list): List to accumulate found tags.
        lines (list[str]): List of lines in the source file.
        start_idx (int): Index of the line to process.
        valid_tags (list): List of valid code tags to look for.
        allow_multiline (bool): Whether to allow multiline comments.
        default_field_meaning (DefaultFieldMeaning): Meaning of the default field.

    Returns:
        int: Number of lines consumed by this tag.
    """
    if not valid_tags:
        valid_tags = []
    line = lines[start_idx]

    # Match any comment line with an uppercase code_tag
    match = re.match(r"\s*#\s*([A-Z]+)\b(.*)", line)
    if not match:
        return 1

    code_tag_candidate = match.group(1)
    content = match.group(2).strip()

    if valid_tags and code_tag_candidate not in valid_tags:
        return 1

    if content.startswith(":"):
        content = content[1:].lstrip()

    # Accumulate multiline if enabled
    current_idx = start_idx
    if allow_multiline and valid_tags:
        multiline_content = [content]
        next_idx = current_idx + 1
        while next_idx < len(lines):
            next_line = lines[next_idx].strip()
            if next_line.startswith("#") and not any(re.match(rf"#\s*{t}\b", next_line) for t in valid_tags):
                multiline_content.append(next_line.lstrip("# "))
                next_idx += 1
            else:
                break
        content = " ".join(multiline_content)
        consumed_lines = next_idx - start_idx
    else:
        consumed_lines = 1

    # Parse fields
    default_field = None
    custom_fields = {}
    comment = content

    field_match = re.match(r"\(([^)]*)\):(.*)", content)
    if field_match:
        field_section = field_match.group(1).strip()
        comment = field_match.group(2).strip()

        for part in field_section.split(","):
            part = part.strip()
            if not part:
                continue
            if "=" in part:
                key, val = part.split("=", 1)
                custom_fields[key.strip()] = val.strip()
            else:
                if default_field is None:
                    default_field = part
                else:
                    default_field += ", " + part
    else:
        id_match = re.match(r"(\d+):(.*)", content)
        if id_match:
            default_field = id_match.group(1)
            comment = id_match.group(2).strip()

    found_tag: FolkTag = {
        # locatoin
        "file_path": file_path,
        "line_number": start_idx + 1,
        "start_char": 0,
        # data
        "code_tag": code_tag_candidate,
        "default_field": default_field,
        "custom_fields": custom_fields,
        "comment": comment,
        "original_text": content,
    }

    if default_field and default_field_meaning:
        found_tag[default_field_meaning] = default_field

    url = extract_first_url(comment)
    if url:
        found_tag["tracker"] = url

    found_tags.append(found_tag)
    return consumed_lines

```

## File: collect_ast.py

```python
"""
Collection methods that rely on AST parsing

TODO: https://pypi.org/project/ast-comments/
"""

from __future__ import annotations

import ast
import logging
from types import ModuleType
from typing import Any, cast

from pycodetags.todo_tag_types import TodoException

logger = logging.getLogger(__name__)


class TodoExceptionCollector:
    """Collector for TodoExceptions that are raised during code execution."""

    def __init__(self) -> None:
        self.exceptions: list[TodoException] = []

    def collect_from_source_analysis(self, module: ModuleType) -> list[TodoException]:
        """
        Analyze source code to find TodoException raises.

        This method parses the source code to find TodoException raises
        without actually executing the code.
        """
        exceptions: list[TodoException] = []

        if not hasattr(module, "__file__") or module.__file__ is None:
            return exceptions

        try:
            with open(module.__file__, encoding="utf-8") as f:
                source = f.read()

            tree = ast.parse(source)

            for node in ast.walk(tree):
                if isinstance(node, ast.Raise) and node.exc:
                    if (
                        isinstance(node.exc, ast.Call)
                        and isinstance(node.exc.func, ast.Name)
                        and node.exc.func.id == "TodoException"
                    ):

                        # Extract arguments from the TodoException call
                        exception_data = self._extract_exception_args(node.exc)
                        if exception_data:
                            exceptions.append(TodoException(**exception_data))

        except (FileNotFoundError, SyntaxError, UnicodeDecodeError):
            pass

        return exceptions

    def _extract_exception_args(self, call_node: ast.Call) -> dict[str, Any]:
        """Extract arguments from a TodoException call node.

        Args:
            call_node: The AST Call node representing the TodoException call

        Returns:
            dict: Dictionary of extracted arguments
        """
        args = {}

        # Handle keyword arguments
        for keyword in call_node.keywords:
            if keyword.arg in ["assignee", "due_date", "message"]:
                if isinstance(keyword.value, ast.Constant):
                    args[keyword.arg] = keyword.value.value
                elif isinstance(keyword.value, ast.Str):  # Python < 3.8 compatibility
                    args[cast(Any, keyword.value)] = keyword.value.s

        return args if args else {}

```

## File: plugin_diagnostics.py

```python
"""
Tool for plugin developers
"""

import pluggy


def plugin_currently_loaded(pm: pluggy.PluginManager) -> None:
    print("--- Loaded pycodetags Plugins ---")
    loaded_plugins = pm.get_plugins()  #
    if not loaded_plugins:
        print("No plugins currently loaded.")
    else:
        for plugin in loaded_plugins:
            plugin_name = pm.get_canonical_name(plugin)  #
            blocked_status = " (BLOCKED)" if pm.is_blocked(plugin_name) else ""  #
            print(f"- {plugin_name}{blocked_status}")

            # Optional: print more detailed info about hooks implemented by this plugin
            # For each hookspec, list if this plugin implements it
            for hook_name in pm.hook.__dict__:
                if hook_name.startswith("_"):  # Skip internal attributes
                    continue
                hook_caller = getattr(pm.hook, hook_name)
                if (
                    plugin in hook_caller.get_hookimpls()
                ):  # Check if this specific plugin has an implementation for this hook
                    print(f"  - Implements hook: {hook_name}")

    print("------------------------------")

```

## File: logging_config.py

```python
"""
Logging configuration.
"""

from __future__ import annotations

import logging
import os
from typing import Any


def generate_config(level: str = "DEBUG", enable_bug_trail: bool = False) -> dict[str, Any]:
    """
    Generate a logging configuration.
    Args:
        level: The logging level.
        enable_bug_trail: Whether to enable bug trail logging.

    Returns:
        dict: The logging configuration.
    """
    config: dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {"format": "[%(levelname)s] %(name)s: %(message)s"},
            "colored": {
                "()": "colorlog.ColoredFormatter",
                "format": "%(log_color)s%(levelname)-8s%(reset)s %(green)s%(message)s",
            },
        },
        "handlers": {
            "default": {
                "level": level,
                "formatter": "colored",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",  # Default is stderr
            },
        },
        "loggers": {
            "pycodetags": {
                "handlers": ["default"],
                "level": level,
                "propagate": False,
            }
        },
    }
    if os.environ.get("NO_COLOR") or os.environ.get("CI"):
        config["handlers"]["default"]["formatter"] = "standard"

    if enable_bug_trail:
        try:
            # pylint: disable=import-outside-toplevel
            import bug_trail_core
        except ImportError:
            print("bug_trail_core is not installed, skipping bug trail handler configuration.")
            return config

        section = bug_trail_core.read_config(config_path="pyproject.toml")
        print(section)
        # handler = bug_trail_core.BugTrailHandler(section.database_path, minimum_level=logging.DEBUG)
        config["handlers"]["bugtrail"] = {
            "class": "bug_trail_core.BugTrailHandler",
            "db_path": section.database_path,
            "minimum_level": logging.DEBUG,
        }
        config["loggers"]["pycodetags"]["handlers"].append("bugtrail")

    return config

```

## File: __about__.py

```python
"""Metadata for pycodetags."""

__all__ = [
    "__title__",
    "__version__",
    "__description__",
    "__readme__",
    "__keywords__",
    "__license__",
    "__requires_python__",
    "__status__",
    "__repository__",
    "__homepage__",
    "__documentation__",
]

__title__ = "pycodetags"
__version__ = "0.1.1"
__description__ = "TODOs in source code as a first class construct, follows PEP350"
__readme__ = "README.md"
__keywords__ = ["pep350", "pep-350", "codetag", "codetags", "code-tags", "code-tag", "TODO", "FIXME"]
__license__ = "MIT"
__requires_python__ = ">=3.7"
__status__ = "4 - Beta"
__repository__ = "https://github.com/matthewdeanmartin/pycodetags"
__homepage__ = "https://github.com/matthewdeanmartin/pycodetags"
__documentation__ = "https://github.com/matthewdeanmartin/pycodetags"

```

## File: user.py

```python
"""
Some alternative ways to identify the current developer, which can be used to stop code if unimplemented code
is the responsibility of that developer.
"""

from __future__ import annotations

import logging
import os

# I could use git library but that also uses shell
import subprocess  # nosec
from functools import lru_cache

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def get_git_user() -> str:
    """Gets user name from local git config."""
    try:
        user = subprocess.check_output(["git", "config", "user.name"]).strip().decode("utf-8")  # nosec
        return user
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown_git_user"


def get_os_user() -> str:
    """Gets user from OS environment variables."""
    return os.getenv("USER") or os.getenv("USERNAME") or "unknown_os_user"


def get_env_user(user_env_var: str) -> str:
    """Gets user from the configured .env variable."""
    return os.getenv(user_env_var, "")


def get_current_user(method: str, user_env_var: str) -> str:
    """
    Determines the current user based on the method in the configuration.
    """
    if method == "git":
        return get_git_user()
    if method == "env":
        return get_env_user(user_env_var)
    if method == "os":
        return get_os_user()
    raise NotImplementedError("Not a known ID method")

```

## File: __init__.py

```python
"""
Code Tags is a tool and library for putting TODOs into source code.

Only the strongly typed decorators, exceptions and context managers are exported.

Everything else is a tool.
"""

__all__ = [
    "TODO",
    "FIXME",
    "TodoException",
    "REQUIREMENT",
    "STORY",
    "IDEA",
    "BUG",
    "HACK",
    "CLEVER",
    "MAGIC",
    "ALERT",
    "PORT",
    "DOCUMENT",
]

from pycodetags.todo_tag_types import TODO, TodoException
from pycodetags.todo_tag_types_aliases import (
    ALERT,
    BUG,
    CLEVER,
    DOCUMENT,
    FIXME,
    HACK,
    IDEA,
    MAGIC,
    PORT,
    REQUIREMENT,
    STORY,
)

```

## File: views.py

```python
"""
Given data structure returned by collect submodule, creates human-readable reports.
"""

from __future__ import annotations

import datetime
import json
import logging
from collections import defaultdict
from typing import Any

from pycodetags.collection_types import CollectedTODOs
from pycodetags.config import get_code_tags_config
from pycodetags.todo_tag_types import TODO, TodoException
from pycodetags.view_tools import group_and_sort

logger = logging.getLogger(__name__)

# import sys
# import io
# breaks pycharm test runner!
# sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")


def print_validate(found: CollectedTODOs) -> None:
    """
    Prints validation errors for TODOs.

    Args:
        found (CollectedTODOs): The collected TODOs and Dones.
    """
    todos: list[TODO] = found["todos"]
    # TODO: validate exceptions
    # exceptions: list[TodoException] = found["exceptions"]

    print("TODOs")
    for item in sorted(todos, key=lambda x: x.code_tag or ""):
        validations = item.validate()
        if validations:
            print(item.as_pep350_comment())
            print(item.as_pep350_comment())
            for validation in validations:
                print(f"  {validation}")
            print()


def print_html(found: CollectedTODOs) -> None:
    """
    Prints TODOs and Dones in a structured HTML format.

    Args:
        found (CollectedTODOs): The collected TODOs and Dones.
    """
    todos: list[TODO] = found["todos"]
    exceptions: list[TodoException] = found["exceptions"]

    tags = set()
    for todo in todos:
        tags.add(todo.code_tag)

    for tag in tags:
        for todo in todos:
            # TODO: find more efficient way to filter.
            if todo.code_tag == tag:
                print(f"<h1>{tag}</h1>")
                print("<ul>")
                if not todo.is_probably_done():
                    print(
                        f"<li><strong>{todo.comment}</strong><br>Author: {todo.assignee}<br>Close: {todo.closed_date}</li>"
                    )
                else:
                    print(f"<li><strong>{todo.comment}</strong><br>Assignee: {todo.assignee}<br>Due: {todo.due}</li>")
                print("</ul>")

    print("<h1>TODO Exceptions</h1>")
    print("<ul>")
    for ex in exceptions:
        print(f"<li><strong>{ex.message}</strong><br>Assignee: {ex.assignee}<br>Due: {ex.due}</li>")
    print("</ul>")


def print_text(found: CollectedTODOs) -> None:
    """
    Prints TODOs and Dones in text format.
    Args:
        found (CollectedTODOs): The collected TODOs and Dones.
    """
    todos = found.get("todos", [])
    exceptions = found.get("exceptions", [])

    if todos:
        grouped = group_and_sort(
            todos, key_fn=lambda x: x.code_tag or "N/A", sort_items=True, sort_key=lambda x: x.comment or "N/A"
        )
        for tag, items in grouped.items():
            print(f"--- {tag.upper()} ---")
            for todo in items:
                print(todo.as_pep350_comment())
                print()
    else:
        print("No Code Tags found.")

    print("\n--- Exceptions ---")
    if exceptions:
        for exception in exceptions:
            print(exception)
    else:
        print("No Dones found.")


def print_json(found: CollectedTODOs) -> None:
    """
    Prints TODOs and Dones in a structured JSON format.
    Args:
        found (CollectedTODOs): The collected TODOs and Dones.
    """
    todos = found.get("todos", [])

    todo_exceptions = found.get("exceptions", [])
    output = {
        "todos": [t.todo_meta.to_dict() for t in todos if t.todo_meta],
        "exceptions": [e.to_dict() for e in todo_exceptions],
    }

    def default(o: Any) -> str:
        if hasattr(o, "todo_meta"):
            o.todo_meta = None

        return json.dumps(o.to_dict()) if hasattr(o, "to_dict") else str(o)

    print(json.dumps(output, indent=2, default=default))


def print_changelog(found: CollectedTODOs) -> None:
    """Prints Done items in the 'Keep a Changelog' format.

    Args:
        found (CollectedTODOs): The collected TODOs and Dones.
    """
    todos = found.get("todos", [])

    found.get("exceptions", [])
    dones_meta = [d.todo_meta for d in todos if d.is_probably_done()]

    # Deal with dodgy data because validation is optional
    for done in dones_meta:
        if done and not done.release:
            done.release = "N/A"

    # BUG: This probably isn't he right way to sort a version
    dones_meta.sort(
        key=lambda d: ((d.release if d.release else "N/A", d.closed_date if d.closed_date else "") if d else ("", "")),
        reverse=True,
    )

    changelog: dict[str, Any] = defaultdict(lambda: defaultdict(list))

    versions = sorted(list({d.release or "N/A" for d in dones_meta if d}), reverse=True)

    for done in dones_meta:
        if done:
            changelog[done.release or ""][done.change_type or "Add"].append(done)

    print("# Changelog\n")
    print("All notable changes to this project will be documented in this file.\n")

    for version in versions:
        first_done = changelog[version][next(iter(changelog[version]))][0]
        if first_done.closed_date and isinstance(first_done.closed_date, (datetime.date, datetime.datetime)):
            version_date = first_done.closed_date.strftime("%Y-%m-%d")
        else:
            version_date = "Unknown date"

        print(f"## [{version}] - {version_date}\n")

        for change_type in ["Added", "Changed", "Deprecated", "Removed", "Fixed", "Security"]:
            if change_type in changelog[version]:
                print(f"### {change_type}")
                for done in changelog[version][change_type]:
                    if done.tracker:
                        ticket_id = done.tracker.split("/")[-1]
                        print(f"- {done.comment} ([{ticket_id}]({done.tracker}))")
                    else:
                        print(f"- {done.comment}")

                print()


def print_todo_md(found: CollectedTODOs) -> None:
    """
    Outputs TODO and Done items in a markdown board-style format.

    https://github.com/todomd/todo.md?tab=readme-ov-file

    Format:
    # Project Name
    Project Description

    ### Column Name
    - [ ] Task title ~3d #type @name yyyy-mm-dd
      - [ ] Sub-task or description

    ### Completed Column ✓
    - [x] Completed task title
    """
    todos = found.get("todos", [])

    print("# Code Tags TODO Board")
    print("Tasks and progress overview.\n")
    print("Legend:")
    print("~ means due")
    print("@ means assignee")
    print("# means category")

    config = get_code_tags_config()

    custom_status = config.valid_status()
    closed_status = config.closed_status()
    if not custom_status:
        custom_status = ["TODO", "DONE"]

    # HACK: This works poorly when statuses are missing or if they don't sync up with the code tag.

    for status in custom_status:
        print(f"### {status.capitalize()}")
        is_done = False
        if status in closed_status:
            done_symbol = "[x]"
            is_done = True
        else:
            done_symbol = "[ ]"
        for todo in todos:
            if todo.status == status or (todo.code_tag and todo.code_tag.lower() == status):
                meta = todo.todo_meta
                if not meta:
                    continue
                task_line = f"- {done_symbol} {meta.comment}"
                if not is_done:
                    if meta.due:
                        task_line += f" ~{meta.due}"
                    if meta.category:
                        task_line += f" #{meta.category.lower()}"
                    if meta.assignee:
                        task_line += f" @{meta.assignee}"
                if meta.closed_date and isinstance(meta.closed_date, (datetime.date, datetime.datetime)):
                    task_line += f" ({meta.closed_date.strftime('%Y-%m-%d')})"
                print(task_line)


def print_done_file(found: CollectedTODOs) -> None:
    """
    Structure:
        TODO in comment format.
        Done date + done comment in square bracket
        Blank line

    Problems:
        This will have a problem with comment identity. (which TODO corresponds to which in the DONE file).
        Identity is not a problem for when the TODO is deleted immediately after DONE.txt generation.

    Example:
        # TODO: Recurse into subdirs only on blue
        # moons. <MDE 2003-09-26>
        [2005-09-26 Oops, I underestimated this one a bit.  Should have
        used Warsaw's First Law!]

        # FIXME: ...
        ...

    """
    dones = found.get("todos", [])
    for done in dones:
        if not done.is_probably_done():
            continue
        # This is valid python. The PEP-350 suggestion was nearly valid python.
        print(done.as_pep350_comment())
        done_date = done.closed_date or ""

        if not done_date:
            after = f", after {done.origination_date}" if done.origination_date else ""
            now = datetime.datetime.now()
            now_day = now.strftime("%Y-%m-%d")
            done_date = f"before {now_day}"
            if after:
                done_date += after
        done_text = f"{done_date} {done.closed_comment or 'no comment'}".strip()
        print(f'["{done_text}"]')
        print()

```

## File: data_tags.py

```python
"""
Abstract data serialization format, of which PEP-350 is one schema.

In scope:
    - parsing a data tag as a data serialization format.
    - defining a schema
    - domain free concepts
    - Parsing python to extract # comments, be it AST or regex or other strategy
    - Round tripping to and from data tag format
    - Equivalence checking by value
    - Merging and promoting fields among default, data and custom.

Out of scope:
    - File system interation
    - Any particular schema (PEP350 code tags, discussion tags, documentation tags, etc)
    - Domain specific concepts (users, initials, start dates, etc)
    - Docstring style comments and docstrings

Inputs:
    - A block of valid python comment text
    - A schema

Outputs:
    - A python data structure that represents a data structure

Half-hearted goal:
    - Minimize python concepts so this can be implemented in Javascript, etc.
"""

from __future__ import annotations

import logging
import re
from typing import Any

try:
    from typing import TypedDict
except ImportError:
    from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


class DataTagSchema(TypedDict):
    default_fields: dict[str, str]
    """type:name, e.g. str:assignees"""

    data_fields: dict[str, str]
    """name:type, e.g. priority:str"""

    data_field_aliases: dict[str, str]
    """name:alias, e.g. priority:p"""


class DataTagFields(TypedDict):
    # When deserializating a field value could appear in default, data and custom field positions.
    default_fields: dict[str, list[Any]]
    """Field without label identified by data type, range or fallback, e.g. user and date"""

    # TODO: support dict[str, int | date | str | list[int, date, str]] ?
    data_fields: dict[str, Any]
    """Expected fields with labels, e.g. category, priority"""

    custom_fields: dict[str, str]
    """Key value pairs, e.g. SAFe program increment number"""

    # TODO: think about adding meaning of default fields here?

    strict: bool
    """If true, the same field can't appear in two places"""


def get_data_field_value(schema: DataTagSchema, fields: DataTagFields, field_name: str) -> Any:
    values = []
    # default fields should already be resolved to a data_field by this point
    if field_name in schema:
        if field_name in fields["data_fields"]:
            values.append(fields["data_fields"][field_name])
        if field_name in fields["custom_fields"]:
            values.append(fields["custom_fields"][field_name])
    if len(set(values)) == 1:
        return values[0]
    if fields["strict"]:
        raise TypeError(f"Double field with different values {field_name} : {values}")
    logger.warning(f"Double field with different values {field_name} : {values}")
    # TODO: do we want to support str | list[str]?
    return values[0]


class DataTag(TypedDict, total=False):
    """An abstract data code tag."""

    code_tag: str
    comment: str
    fields: DataTagFields

    # metadata
    original_text: str


def promote_fields(tag: DataTag, data_tag_schema: DataTagSchema) -> None:
    fields = tag["fields"]
    if not fields.get("custom_fields", {}) and not fields.get("default_fields", {}):
        # nothing to promote
        return

    # It is already there, just move it over.
    for default_key, default_value in tag["fields"]["default_fields"].items():
        if default_key in fields["data_fields"] and fields["data_fields"][default_key] != default_value:
            # Strict?
            logger.warning(
                "Field in both data_fields and default_fields and they don't match: "
                f'{default_key}: {fields["data_fields"][default_key]} != {default_value}'
            )
            if isinstance(fields["data_fields"][default_key], list) and isinstance(default_value, list):
                fields["data_fields"][default_key].extend(default_value)
            elif isinstance(fields["data_fields"][default_key], list) and isinstance(default_value, str):
                fields["data_fields"][default_key].append(default_value)
            elif isinstance(fields["data_fields"][default_key], str) and isinstance(default_value, list):
                fields["data_fields"][default_key] = default_value + [fields["data_fields"][default_key]]
            elif isinstance(fields["data_fields"][default_key], str) and isinstance(default_value, str):
                # promotes str to list[str], ugly!
                fields["data_fields"][default_key] = [fields["data_fields"][default_key], default_value]

        else:
            fields["data_fields"][default_key] = default_value

    # promote a custom_field to root field if it should have been a root field.
    field_aliases: dict[str, str] = data_tag_schema["data_field_aliases"]
    # putative custom field, is it actually standard?
    for custom_field, custom_value in fields["custom_fields"].items():
        if custom_field in field_aliases:
            # Okay, found a custom field that should have been standard
            full_alias = field_aliases[custom_field]

            if fields["data_fields"][full_alias]:
                # found something already there
                consumed = False
                if isinstance(fields["data_fields"][full_alias], list):
                    # root is list
                    if isinstance(custom_value, list):
                        # both are list: merge list into parent list
                        fields["data_fields"][full_alias].extend(custom_value)
                        consumed = True
                    elif isinstance(custom_value, str):
                        # list/string promote parent string to list (ugh!)
                        fields["data_fields"][full_alias] = fields["data_fields"][full_alias].append(custom_value)
                        consumed = True
                    else:
                        # list/surprise
                        logger.warning(f"Promoting custom_field {full_alias}/{custom_value} to unexpected type")
                        fields["data_fields"][full_alias].append(custom_value)
                        consumed = True
                elif isinstance(fields["data_fields"][full_alias], str):
                    if isinstance(custom_value, list):
                        # str/list: parent str joins custom list
                        fields["data_fields"][full_alias] = [fields["data_fields"][full_alias]] + custom_value
                        consumed = True
                    elif isinstance(custom_value, str):
                        # str/str forms a list
                        fields["data_fields"][full_alias] = [fields["data_fields"][full_alias], custom_value]
                        consumed = True
                    else:
                        # str/surprise
                        logger.warning(f"Promoting custom_field {full_alias}/{custom_value} to unexpected type")
                        fields["data_fields"][full_alias] = [
                            fields["data_fields"][full_alias],
                            custom_value,
                        ]  # xtype: ignore
                        consumed = True
                else:
                    # surprise/surprise = > list
                    logger.warning(f"Promoting custom_field {full_alias}/{custom_value} to unexpected type")
                    fields[full_alias] = [fields[full_alias], custom_value]  # type: ignore
                    consumed = True
                if consumed:
                    del fields["custom_fields"][custom_field]
                else:
                    # This might not  be reachable.
                    logger.warning(f"Failed to promote custom_field {full_alias}/{custom_value}, not consumed")


def is_int(s: str) -> bool:
    """Check if a string can be interpreted as an integer.
    Args:
        s (str): The string to check.

    Returns:
        bool: True if the string is an integer, False otherwise.

    Examples:
        >>> is_int("123")
        True
        >>> is_int("-456")
        True
        >>> is_int("+789")
        True
        >>> is_int("12.3")
        False
        >>> is_int("abc")
        False
        >>> is_int("")
        False
    """
    if len(s) and s[0] in ("-", "+"):
        return s[1:].isdigit()
    return s.isdigit()


def parse_fields(field_string: str, schema: DataTagSchema, strict: bool) -> DataTagFields:
    """
    Parse a field string from a PEP-350 style code tag and return a dictionary of fields.

    Args:
        field_string (str): The field string to parse.
        schema (DataTagSchema): The schema defining the fields and their aliases.
        strict: bool: If True, raises an error if a field appears in multiple places.

    Returns:
        Fields: A dictionary containing the parsed fields.
    """
    field_aliases: dict[str, str] = merge_two_dicts(schema["data_field_aliases"], schema["data_fields"])

    fields: DataTagFields = {"default_fields": {}, "data_fields": {}, "custom_fields": {}, "strict": strict}

    # Updated key_value_pattern:
    # - Handles quoted values (single or double) allowing any characters inside.
    # - For unquoted values, it now strictly matches one or more characters that are NOT:
    #   - whitespace `\s`
    #   - single quote `'`
    #   - double quote `"`
    #   - angle bracket `<` (which signals end of field string)
    #   - a comma `,` (unless it's part of a quoted string or explicitly for assignee splitting)
    #   The change here ensures it stops at whitespace, which correctly separates '1' from '2025-06-15'.
    key_value_pattern = re.compile(
        r"""
        ([a-zA-Z_][a-zA-Z0-9_]*) # Key (group 1): alphanumeric key name
        \s*[:=]\s* # Separator (colon or equals, with optional spaces)
        (                        # Start of value group (group 2)
            '(?:[^'\\]|\\.)*' |  # Match single-quoted string (non-greedy, allowing escaped quotes)
            "(?:[^"\\]|\\.)*" |  # Match double-quoted string (non-greedy, allowing escaped quotes)
            (?:[^\s'"<]+)       # Unquoted value: one or more characters not in \s ' " <
        )
        """,
        re.VERBOSE,  # Enable verbose regex for comments and whitespace
    )

    key_value_matches = []
    # Find all key-value pairs in the field_string
    for match in key_value_pattern.finditer(field_string):
        # Store the span (start, end indices) of the match, the key, and the raw value
        key_value_matches.append((match.span(), match.group(1), match.group(2)))

    # Process extracted key-value pairs
    for (_start_idx, _end_idx), key, value_raw in key_value_matches:
        key_lower = key.lower()

        # Strip quotes from the value if it was quoted
        value = value_raw
        if value.startswith("'") and value.endswith("'"):
            value = value[1:-1]
        elif value.startswith('"') and value.endswith('"'):
            value = value[1:-1]

        # Assign the parsed value to the appropriate field
        if key_lower in field_aliases:
            normalized_key: str = field_aliases[key_lower]
            if normalized_key == "assignee":
                # Assignees can be comma-separated in unquoted values
                if "assignee" in fields["data_fields"]:
                    fields["data_fields"]["assignee"].extend([v.strip() for v in value.split(",") if v])
                else:
                    fields["data_fields"]["assignee"] = [v.strip() for v in value.split(",") if v]
            else:
                fields["data_fields"][normalized_key] = value
        else:
            # If not a predefined field, add to custom_fields
            fields["custom_fields"][key] = value

    # Extract remaining tokens that were not part of any key-value pair
    consumed_spans = sorted([span for span, _, _ in key_value_matches])

    unconsumed_segments = []
    current_idx = 0
    # Iterate through the field_string to find segments not covered by key-value matches
    for start, end in consumed_spans:
        if current_idx < start:
            # If there's a gap between the last consumed part and the current match, it's unconsumed
            segment = field_string[current_idx:start].strip()
            if segment:  # Only add non-empty segments
                unconsumed_segments.append(segment)
        current_idx = max(current_idx, end)  # Move current_idx past the current consumed area

    # Add any remaining part of the string after the last key-value match
    if current_idx < len(field_string):
        segment = field_string[current_idx:].strip()
        if segment:  # Only add non-empty segments
            unconsumed_segments.append(segment)

    # Join the unconsumed segments and then split by whitespace to get individual tokens
    other_tokens_raw = " ".join(unconsumed_segments)
    other_tokens = [token.strip() for token in other_tokens_raw.split() if token.strip()]

    # Process these remaining tokens for dates (origination_date) and assignees (initials)
    date_pattern = re.compile(r"(\d{4}-\d{2}-\d{2})")

    # This is too domain specific. Let a plugin handle user aliases.
    # initials_pattern = re.compile(r"^[A-Z,]+$")  # Matches comma-separated uppercase initials

    for token in other_tokens:
        # handles this case:
        # <foo:bar
        #   fizz:buzz
        #  bing:bong>
        if token == "#":  # nosec
            continue
        matched_default = False
        # for default_type, default_key in schema["default_fields"].items():
        # str must go last, it matches everything!
        for default_type in ["int", "date", "str"]:
            default_key = schema["default_fields"].get(default_type)
            if default_key:
                if not matched_default:
                    # Default fields!
                    if default_type == "date" and date_pattern.match(token):
                        # Assign default_key from a standalone date token
                        fields["default_fields"][default_key] = token  # type: ignore[assignment]
                        matched_default = True
                    elif default_type == "str":  #  initials_pattern.match(token):
                        # Add standalone initials to assignees list
                        if default_key in fields["default_fields"]:
                            fields["default_fields"][default_key].extend([t.strip() for t in token.split(",") if t])
                        else:
                            fields["default_fields"][default_key] = [t.strip() for t in token.split(",") if t]
                        matched_default = True
                    elif default_type == "int" and is_int(token):
                        fields["default_fields"][default_key] = token  # type: ignore[assignment]
                        matched_default = True

    # TODO: promote default fields to data_fields
    return fields


def merge_two_dicts(x: dict[str, Any], y: dict[str, Any]) -> dict[str, Any]:
    z = x.copy()  # start with keys and values of x
    z.update(y)  # modifies z with keys and values of y
    return z


def parse_codetags(text_block: str, data_tag_schema: DataTagSchema, strict: bool) -> list[DataTag]:
    """
    Parse PEP-350 style code tags from a block of text.

    Args:
        text_block (str): The block of text containing PEP-350 style code tags.
        data_tag_schema: DataTagSchema: The schema defining the fields and their aliases.
        strict: bool: If True, raises an error if a field appears in multiple places.

    Returns:
        list[PEP350Tag]: A list of PEP-350 style code tags found in the text block.
    """
    results: list[DataTag] = []
    code_tag_regex = re.compile(
        r"""
        (?P<code_tag>[A-Z\?\!]{3,}) # Code tag (e.g., TODO, FIXME, BUG)
        \s*:\s* # Colon separator with optional whitespace
        (?P<comment>.*?)            # Comment text (non-greedy)
        <                           # Opening angle bracket for fields
        (?P<field_string>.*?)       # Field string (non-greedy)
        >                           # Closing angle bracket for fields
        """,
        re.DOTALL | re.VERBOSE,  # DOTALL allows . to match newlines, VERBOSE allows comments in regex
    )

    matches = list(code_tag_regex.finditer(text_block))
    for match in matches:
        tag_parts = {
            "code_tag": match.group("code_tag").strip(),
            "comment": match.group("comment").strip().rstrip(" \n#"),  # Clean up comment
            "field_string": match.group("field_string")
            .strip()
            .replace("\n", " "),  # Replace newlines in fields with spaces
        }
        fields = parse_fields(tag_parts["field_string"], data_tag_schema, strict)
        results.append(
            {
                "code_tag": tag_parts["code_tag"],
                "comment": tag_parts["comment"],
                "fields": fields,
                "original_text": "N/A",  # BUG: Regex doesn't allow for showing this!
            }
        )

    # promote standard fields in custom_fields to root, merging if already exist
    for result in results:
        promote_fields(result, data_tag_schema)
    return results

```

## File: collection_types.py

```python
from __future__ import annotations

try:
    from typing import TypedDict  # noqa: F401
except ImportError:
    from typing_extensions import TypedDict

from pycodetags import TODO, TodoException


class CollectedTODOs(TypedDict, total=False):
    """TypedDict for collected TODOs, Dones, and exceptions."""

    todos: list[TODO]
    exceptions: list[TodoException]

```

## File: __main__.py

```python
"""
CLI for pycodetags.
"""

from __future__ import annotations

import argparse
import logging
import logging.config
import sys
from collections.abc import Sequence

import pluggy

import pycodetags.__about__ as __about__
from pycodetags.aggregate import aggregate_all_kinds, aggregate_all_kinds_multiple_input, merge_collected
from pycodetags.collection_types import CollectedTODOs
from pycodetags.config import CodeTagsConfig, get_code_tags_config
from pycodetags.dotenv import load_dotenv
from pycodetags.logging_config import generate_config
from pycodetags.plugin_diagnostics import plugin_currently_loaded
from pycodetags.plugin_manager import get_plugin_manager
from pycodetags.views import (
    print_changelog,
    print_done_file,
    print_html,
    print_json,
    print_text,
    print_todo_md,
    print_validate,
)


def main(argv: Sequence[str] | None = None) -> int:
    """
    Main entry point for the pycodetags CLI.

    Args:
        argv (Sequence[str] | None): Command line arguments. If None, uses sys.argv.
    """
    pm = get_plugin_manager()

    class InternalViews:
        """Register internal views as a plugin"""

        @pluggy.HookimplMarker("pycodetags")
        def code_tags_print_report(self, format_name: str, found_data: CollectedTODOs) -> bool:
            """
            Internal method to handle printing of reports in various formats.

            Args:
                format_name (str): The name of the format requested by the user.
                found_data (CollectedTODOs): The data collected from the source code.

            Returns:
                bool: True if the format was handled, False otherwise.
            """
            if format_name == "text":
                print_text(found_data)
                return True
            if format_name == "html":
                print_html(found_data)
                return True
            if format_name == "json":
                print_json(found_data)
                return True
            if format_name == "keep-a-changelog":
                print_changelog(found_data)
                return True
            if format_name == "todo.md":
                print_todo_md(found_data)
                return True
            if format_name == "done":
                print_done_file(found_data)
                return True
            return False

    pm.register(InternalViews())
    # --- end pluggy setup ---

    parser = argparse.ArgumentParser(description=f"{__about__.__description__} (v{__about__.__version__})")

    # Basic arguments that apply to all commands (like verbose/info/bug-trail/config)
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("--config", help="Path to config file, defaults to current folder pyproject.toml")
    base_parser.add_argument("--verbose", default=False, action="store_true", help="verbose level logging output")
    base_parser.add_argument("--info", default=False, action="store_true", help="info level logging output")
    base_parser.add_argument("--bug-trail", default=False, action="store_true", help="enable bug trail, local logging")
    # validate switch
    base_parser.add_argument("--validate", action="store_true", help="Validate all the items found")

    # Create subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # 'report' command
    report_parser = subparsers.add_parser("report", parents=[base_parser], help="Generate code tag reports")
    # report runs collectors, collected things can be validated
    report_parser.add_argument("--module", action="append", help="Python module to inspect (e.g., 'my_project.main')")
    report_parser.add_argument("--src", action="append", help="file or folder of source code")

    report_parser.add_argument("--output", help="destination file or folder")

    extra_supported_formats = []
    for result in pm.hook.code_tags_print_report_style_name():
        extra_supported_formats.extend(result)

    report_parser.add_argument(
        "--format",
        choices=["text", "html", "json", "keep-a-changelog", "todo.md", "done"] + extra_supported_formats,
        default="text",
        help="Output format for the report.",
    )
    # report_parser.add_argument("--validate", action="store_true", help="Validate all the items found")

    _plugin_info_parser = subparsers.add_parser(
        "plugin-info", parents=[base_parser], help="Display information about loaded plugins"
    )

    # Allow plugins to add their own subparsers
    new_subparsers = pm.hook.code_tags_add_cli_subcommands(subparsers=subparsers)
    # Hack because we don't want plugins to have to wire up the basic stuff
    for new_subparser in new_subparsers:
        new_subparser.add_argument("--config", help="Path to config file, defaults to current folder pyproject.toml")
        new_subparser.add_argument("--verbose", default=False, action="store_true", help="verbose level logging output")
        new_subparser.add_argument("--info", default=False, action="store_true", help="info level logging output")
        new_subparser.add_argument(
            "--bug-trail", default=False, action="store_true", help="enable bug trail, local logging"
        )
        # validate switch
        new_subparser.add_argument("--validate", action="store_true", help="Validate all the items found")

    args = parser.parse_args(args=argv)

    if args.config:
        code_tags_config = CodeTagsConfig(pyproject_path=args.config)
    else:
        code_tags_config = CodeTagsConfig()

    if code_tags_config.use_dot_env():
        load_dotenv()

    if args.verbose:
        config = generate_config(level="DEBUG", enable_bug_trail=args.bug_trail)
        logging.config.dictConfig(config)
    elif args.info:
        config = generate_config(level="INFO", enable_bug_trail=args.bug_trail)
        logging.config.dictConfig(config)
    else:
        # Essentially, quiet mode
        config = generate_config(level="FATAL", enable_bug_trail=args.bug_trail)
        logging.config.dictConfig(config)

    if not args.command:
        parser.print_help()
        return 1

    # Handle the 'report' command
    if args.command == "report":
        modules = args.module or code_tags_config.modules_to_scan()
        src = args.src or code_tags_config.source_folders_to_scan()
        if not modules and not src:
            print(
                "Need to specify one or more importable modules (--module) "
                "or source code folders/files (--src) or specify in config file.",
                file=sys.stderr,
            )
            sys.exit(1)

        try:
            found = aggregate_all_kinds_multiple_input(modules, src)
        except ImportError:
            print(f"Error: Could not import module(s) '{args.module}'", file=sys.stderr)
            return 1

        if args.validate:
            if len(found["todos"]) + len(found["exceptions"]) == 0:
                raise TypeError("No data to validate.")
            print_validate(found)
        else:
            if len(found["todos"]) + len(found["exceptions"]) == 0:
                raise TypeError("No data to report.")
            # Call the hook.
            results = pm.hook.code_tags_print_report(
                format_name=args.format, output_path=args.output, found_data=found, config=get_code_tags_config()
            )

            # results = pm.hook.code_tags_print_report(format_name=args.format, found_data=found)
            if not any(results):
                print(f"Error: Format '{args.format}' is not supported.", file=sys.stderr)
                return 1
                # --- NEW: Handle 'plugin-info' command ---
    elif args.command == "plugin-info":
        plugin_currently_loaded(pm)
    else:
        # Pass control to plugins for other commands
        # Aggregate data if plugins might need it
        found_data_for_plugins: CollectedTODOs = {}
        modules = []
        src = []
        if hasattr(args, "module") and args.module:
            modules = getattr(args, "module", [])
        else:
            modules = code_tags_config.modules_to_scan()

        if hasattr(args, "src") and args.src:
            src = getattr(args, "src", [])
        else:
            modules = code_tags_config.source_folders_to_scan()

        try:
            # BUG: this needs to be a list
            all_found: list[CollectedTODOs] = []
            for source in src:
                all_found.append(aggregate_all_kinds("", source))
            for module in modules:
                all_found.append(aggregate_all_kinds(module, ""))

            found_data_for_plugins = merge_collected(all_found)
        except ImportError:
            logging.warning(f"Could not aggregate data for command {args.command}, proceeding without it.")
            found_data_for_plugins = {"todos": [], "exceptions": []}

        handled_by_plugin = pm.hook.code_tags_run_cli_command(
            command_name=args.command, args=args, found_data=found_data_for_plugins, config=get_code_tags_config()
        )
        if not any(handled_by_plugin):
            print(f"Error: Unknown command '{args.command}'.", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

```

## File: collect.py

```python
"""
Finds all strongly typed code tags in a module.

Three ways to find strongly typed TODOs:

- import module, walk the object graph. Easy to miss anything without a public interface
- See other modules for techniques using AST parsing
- See other modules for source parsing.

"""

from __future__ import annotations

import inspect
import logging
import os
import sysconfig
import types
from types import ModuleType, SimpleNamespace
from typing import Any

from pycodetags.collect_ast import TodoExceptionCollector
from pycodetags.collection_types import CollectedTODOs
from pycodetags.todo_tag_types import TODO, TodoException

logger = logging.getLogger(__name__)


def is_stdlib_module(module: types.ModuleType | SimpleNamespace) -> bool:
    """
    Check if a module is part of the Python standard library.

    Args:
        module: The module to check

    Returns:
        bool: True if the module is part of the standard library, False otherwise
    """
    # Built-in module (no __file__ attribute, e.g. 'sys', 'math', etc.)
    if not hasattr(module, "__file__"):
        return True

    stdlib_path = sysconfig.get_paths()["stdlib"]
    the_path = getattr(module, "__file__", "")
    if not the_path:
        return True
    module_path = os.path.abspath(the_path)

    return module_path.startswith(os.path.abspath(stdlib_path))


class TodoCollector:
    """Comprehensive collector for TODO, Done, and TodoException items."""

    def __init__(self) -> None:
        self.todos: list[TODO] = []
        self.todo_exceptions: list[TodoException] = []
        self.visited: set[int] = set()

    def collect_from_module(
        self, module: ModuleType, include_submodules: bool = True, max_depth: int = 10
    ) -> tuple[list[TODO], list[TodoException]]:
        """
        Collect all TODO/Done items and TodoExceptions from a module.

        Args:
            module: The module to inspect
            include_submodules: Whether to recursively inspect submodules
            max_depth: Maximum recursion depth for submodules

        Returns:
            Tuple of (todos, dones, todo_exceptions)
        """
        self._reset()
        self._collect_recursive(module, include_submodules, max_depth, 0)
        return self.todos.copy(), self.todo_exceptions.copy()

    def _reset(self) -> None:
        """Reset internal collections."""
        self.todos.clear()
        self.todo_exceptions.clear()
        self.visited.clear()

    def _collect_recursive(self, obj: Any, include_submodules: bool, max_depth: int, current_depth: int) -> None:
        """Recursively collect TODO/Done items from an object.

        Args:
            obj: The object to inspect
            include_submodules: Whether to recursively inspect submodules
            max_depth: Maximum recursion depth for submodules
            current_depth: Current recursion depth
        """
        if current_depth > max_depth or id(obj) in self.visited:
            if current_depth > max_depth:
                logger.debug(f"Maximum depth {max_depth}")
            else:
                logger.debug(f"Already visited {id(obj)}")
            return

        self.visited.add(id(obj))

        # Check if object itself is a TODO/Done item
        # self._check_object_for_todos(obj)

        # Handle modules
        if inspect.ismodule(obj) and not is_stdlib_module(obj):
            logger.debug(f"Collecting module {obj}")
            self._collect_from_module_attributes(obj, include_submodules, max_depth, current_depth)

        if isinstance(obj, SimpleNamespace):
            logger.debug(f"Collecting namespace {obj}")
            self._collect_from_module_attributes(obj, include_submodules, max_depth, current_depth)

        # Handle classes
        if inspect.isclass(obj):
            logger.debug(f"Collecting class {obj}")
            self._collect_from_class_attributes(obj, include_submodules, max_depth, current_depth)

        # Handle functions and methods
        if inspect.isfunction(obj) or inspect.ismethod(obj):
            logger.debug(f"Collecting function/method {obj}")
            self._check_object_for_todos(obj)
            # Classes are showing up as functions?! Yes.
            self._collect_from_class_attributes(obj, include_submodules, max_depth, current_depth)
        if isinstance(obj, (list, set, tuple)) and obj:
            logger.debug(f"Found a list/set/tuple {obj}")
            for item in obj:
                self._check_object_for_todos(item)
        else:
            # self._collect_from_class_attributes(obj, include_submodules, max_depth, current_depth)
            logger.debug(f"Don't know what to do with {obj}")

    def _check_object_for_todos(self, obj: Any) -> None:
        """Check if an object has TODO/Done metadata."""
        if hasattr(obj, "todo_meta"):
            if isinstance(obj.todo_meta, TODO):
                logger.info(f"Found todo, by instance and has todo_meta attr on {obj}")
                self.todos.append(obj.todo_meta)

    def _collect_from_module_attributes(
        self, module: ModuleType | SimpleNamespace, include_submodules: bool, max_depth: int, current_depth: int
    ) -> None:
        """Collect from all attributes of a module.

        Args:
            module: The module to inspect
            include_submodules: Whether to recursively inspect submodules
            max_depth: Maximum recursion depth for submodules
            current_depth: Current recursion depth
        """
        if is_stdlib_module(module) or module.__name__ == "builtins":
            return

        for attr_name in dir(module):
            if attr_name.startswith("__"):
                continue
            # User could put a TODO on a private method and even if it isn't exported, it still is a TODO
            # if attr_name.startswith("_"):
            #     continue

            logger.debug(f"looping : {module} : {attr_name}")

            try:
                attr = getattr(module, attr_name)

                # Handle submodules
                if include_submodules and inspect.ismodule(attr):
                    # Avoid circular imports and built-in modules
                    if (
                        hasattr(attr, "__file__")
                        and attr.__file__ is not None
                        and not attr.__name__.startswith("builtins")
                    ):
                        self._collect_recursive(attr, include_submodules, max_depth, current_depth + 1)
                # elif isinstance(list, attr) and attr:
                #     for item in attr:
                #         self._collect_recursive(item, include_submodules, max_depth, current_depth + 1)
                # elif is_stdlib_module(module) or module.__name__ == "builtins":
                #     pass
                else:
                    logger.debug(f"Collecting something ...{attr_name}: {attr}")
                    self._collect_recursive(attr, include_submodules, max_depth, current_depth + 1)

            except (AttributeError, ImportError, TypeError):
                # Skip attributes that can't be accessed
                continue

    def _collect_from_class_attributes(
        self,
        cls: type | types.FunctionType | types.MethodType,
        include_submodules: bool,
        max_depth: int,
        current_depth: int,
    ) -> None:
        """
        Collect from all attributes of a class.

        Args:
            cls: The class to inspect
            include_submodules: Whether to recursively inspect submodules
            max_depth: Maximum recursion depth for submodules
            current_depth: Current recursion depth
        """
        logger.debug("Collecting from class attributes ------------")
        # Check class methods and attributes
        for attr_name in dir(cls):
            if attr_name.startswith("__"):
                continue

            try:
                attr = getattr(cls, attr_name)
                self._collect_recursive(attr, include_submodules, max_depth, current_depth + 1)
            except (AttributeError, TypeError):
                logger.error(f"ERROR ON attr_name {attr_name}")
                continue

    def collect_standalone_items(self, items_list: list[TODO]) -> tuple[list[TODO], list[TODO]]:
        """
        Collect standalone TODO/Done items from a list.

        Args:
            items_list: List containing TODO and Done instances

        Returns:
            Tuple of (todos, dones)
        """
        todos = [item for item in items_list if isinstance(item, TODO)]
        dones = []
        for item in todos:
            if item.is_probably_done():
                dones.append(item)
                todos.remove(item)
        return todos, dones


def collect_all_todos(
    module: ModuleType,
    standalone_items: list[TODO] | None = None,
    include_submodules: bool = True,
    include_exceptions: bool = True,
) -> CollectedTODOs:
    """
    Comprehensive collection of all TODO/Done items and exceptions.

    Args:
        module: Module to inspect
        standalone_items: List of standalone TODO/Done items
        include_submodules: Whether to inspect submodules
        include_exceptions: Whether to analyze source for TodoExceptions

    Returns:
        Dictionary with 'todos', 'dones', and 'exceptions' keys
    """
    collector = TodoCollector()
    # BUG: _runtime_exceptions is never really used.
    todos, _runtime_exceptions = collector.collect_from_module(module, include_submodules)
    logger.info(f"Found {len(todos)} TODOs in module '{module.__name__}'.")

    # Collect standalone items if provided
    if standalone_items:
        standalone_todos, standalone_dones = collector.collect_standalone_items(standalone_items)
        logger.info(f"Found {len(standalone_todos)} standalone TODOs and {len(standalone_dones)} standalone Dones.")
        todos.extend(standalone_todos)

    # Collect exceptions from source analysis
    exceptions = []
    if include_exceptions:
        exception_collector = TodoExceptionCollector()
        exceptions = exception_collector.collect_from_source_analysis(module)

    return {"todos": todos, "exceptions": exceptions}

```

## File: standard_code_tags.py

```python
"""
Find and parse PEP-350 style code tags.

Examples:
List value in a default field.
# FIXME: Seems like this Loop should be finite. <MDE, CLE d:2015-1-1 p:2>

After code, field aliases, default fields
while True: # BUG: Crashes if run on Sundays. <MDE 2005-09-04 d:2015-6-6 p:2>

Multiline, mixed key-value separators
# TODO: This is a complex task that needs more details.
# <
#   assignee=JRNewbie
#   priority:3
#   due=2025-12-25
#   custom_field: some_value
# >

A default field with explicit key
# RFE: Add a new feature for exporting. <assignee:Micahe,CLE priority=1 2025-06-15>

"""

from __future__ import annotations

import logging
import tokenize
from collections.abc import Generator
from pathlib import Path

from pycodetags.comment_finder import find_comment_blocks
from pycodetags.data_tags import DataTag, parse_codetags
from pycodetags.specific_schemas import PEP350Schema

try:
    from typing import TypedDict
except ImportError:

    from typing_extensions import TypedDict

logger = logging.getLogger(__name__)


class Fields(TypedDict, total=False):
    """Fields extracted from PEP-350 style code tags."""

    # HACK: maybe make these always a list?
    assignee: str  # make this go away and always promote to assignee, isomorphic with custom_tags?
    assignees: list[str]

    # Best identity fields, when they exist!
    originator: str
    origination_date: str

    # Metadata, shouldn't be set by user.
    file_path: str  # mutable across time, identity for same revision
    line_number: str  # mutable across time, identity for same revision
    file_revision: str  # With file_path, line_number, forms identity

    # When all of these mutable fields, or almost all of these are they same, the object probably points
    # to the same real world entity.
    # creates need for promotion
    custom_fields: dict[str, str]  # mutable
    priority: str  # mutable
    due: str  # mutable
    tracker: str  # mutable
    status: str  # mutable
    category: str  # mutable
    iteration: str  # mutable
    release: str  # mutable

    # creates need for alias merging, when both priority and p exist
    p: str
    d: str
    t: str
    s: str
    c: str
    i: str
    r: str
    a: str


field_aliases: dict[str, str] = {
    "p": "priority",
    "d": "due",
    "t": "tracker",
    "s": "status",
    "c": "category",
    "i": "iteration",
    "r": "release",
    "a": "assignee",
    "priority": "priority",
    "due": "due",
    "tracker": "tracker",
    "status": "status",
    "category": "category",
    "iteration": "iteration",
    "release": "release",
    "assignee": "assignee",
    "originator": "originator",
}


def extract_comment_blocks_fallback(filename: str) -> list[list[str]]:
    """
    Dead code, useful if comment-ast isn't avail

    Extract comment blocks from a Python file, grouping consecutive comments together.

    Args:
        filename (str): The path to the Python file to extract comments from.

    Returns:
        list[list[str]]: A list of lists, where each inner list contains consecutive comment lines.
    """
    comment_blocks = []
    current_block = []
    last_comment_lineno = -2

    with open(filename, "rb") as f:
        tokens = list(tokenize.tokenize(f.readline))

    for token in tokens:
        if token.type == tokenize.COMMENT:
            lineno = token.start[0]
            comment_text = token.string.strip()

            # Group consecutive comment lines
            if lineno == last_comment_lineno + 1:
                current_block.append(comment_text)
            else:
                # Start a new block if the current line is not consecutive
                if current_block:
                    comment_blocks.append(current_block)
                current_block = [comment_text]

            last_comment_lineno = lineno

        # If a non-comment, non-whitespace token is encountered, it breaks a comment block
        elif token.type not in (tokenize.NL, tokenize.NEWLINE, tokenize.ENCODING, tokenize.INDENT, tokenize.DEDENT):
            if token.start[0] > last_comment_lineno + 1:  # Check if there's a gap
                if current_block:
                    comment_blocks.append(current_block)
                    current_block = []
                last_comment_lineno = -2  # Reset to indicate no recent comment

    # Add any remaining current block at the end of the file
    if current_block:
        comment_blocks.append(current_block)

    return comment_blocks


def collect_pep350_code_tags(file: str) -> Generator[DataTag]:
    """
    Collect PEP-350 style code tags from a given file.

    Args:
        file (str): The path to the file to process.

    Yields:
        PEP350Tag: A generator yielding PEP-350 style code tags found in the file.
    """
    logger.info(f"collect_pep350_code_tags: processing {file}")
    things = []
    for _start_line, _start_char, _end_line, _end_char, final_comment in find_comment_blocks(Path(file)):
        # Can only be one comment block now!
        thing = parse_codetags(final_comment, PEP350Schema, strict=False)
        things.extend(thing)
    yield from things

```

