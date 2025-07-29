"""
Config for code_tags library.

This is a basically valid config
```toml
[tool.code_tags]
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
user_env_var = "CODE_TAGS_USER"

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

from code_tags.user import get_current_user
from code_tags.users_from_authors import parse_authors_file_simple

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

        self._config = data.get("tool", {}).get("code_tags", {})

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
