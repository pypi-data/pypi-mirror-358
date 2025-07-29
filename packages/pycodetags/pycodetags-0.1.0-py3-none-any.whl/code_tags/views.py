"""
Given data structure returned by collect submodule, creates human-readable reports.
"""

from __future__ import annotations

import datetime
import json
import logging
from collections import defaultdict
from typing import Any

from code_tags.collection_types import CollectedTODOs
from code_tags.config import get_code_tags_config
from code_tags.todo_tag_types import TODO, TodoException
from code_tags.view_tools import group_and_sort

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
