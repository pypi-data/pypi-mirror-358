#❯ code_tags --help
#usage: code_tags [-h] {report,plugin-info,jira-sync} ...
#
#TODOs in source code as a first class construct (v0.1.0)
#
#positional arguments:
#  {report,plugin-info,jira-sync}
#                        Available commands
#    report              Generate code tag reports
#    plugin-info         Display information about loaded plugins
#    jira-sync           Synchronize TODOs with Jira
#
#options:
#  -h, --help            show this help message and exit
set -e
export CODE_TAGS_NO_OPEN_BROWSER=1
uv run code_tags report --module demo.__main__ --module code_tags --src demo --src tests
echo "-------------------------------------"
uv run code_tags report --module demo.__main__ --module code_tags --src demo --src tests --format text
echo "-------------------------------------"
uv run code_tags report --module demo.__main__ --module code_tags --src demo --src tests --format html
echo "-------------------------------------"
uv run code_tags report --module demo.__main__ --module code_tags --src demo --src tests --format json
echo "-------------------------------------"
uv run code_tags report --module demo.__main__ --module code_tags --src demo --src tests --format keep-a-changelog
echo "-------------------------------------"
uv run code_tags report --module demo.__main__ --module code_tags --src demo --src tests --format todo.md
