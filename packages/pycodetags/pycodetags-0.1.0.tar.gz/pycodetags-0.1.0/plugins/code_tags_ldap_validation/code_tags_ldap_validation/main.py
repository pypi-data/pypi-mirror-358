import pluggy

from code_tags.config import CodeTagsConfig
from code_tags.todo_tag_types import TODO

hookimpl = pluggy.HookimplMarker("code_tags")

LDAP_USERS = {"alice", "bob", "charlie", "matth"}  # pretend LDAP list


class LdapAssigneePlugin:
    @hookimpl
    def code_tags_validate_todo(self, todo_item: TODO, config: CodeTagsConfig) -> list[str]:
        issues = []
        assignee = (todo_item.assignee or "").lower()

        if assignee and assignee not in LDAP_USERS:
            issues.append(f"Assignee '{assignee}' not found in LDAP directory.")
        return issues
