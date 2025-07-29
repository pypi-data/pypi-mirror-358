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
# Don't export reports to same folder where you search for code tags!
code_tags report --module demo.__main__ --src demo>demo_reports/default.txt
echo "-------------------------------------"
code_tags report --module demo.__main__ --src demo --format text>demo_reports/todo.txt
echo "-------------------------------------"
code_tags report  --module demo.__main__ --src demo --format html
echo "-------------------------------------"
code_tags report  --module demo.__main__ --src demo --format json>demo_reports/todo.json
echo "-------------------------------------"
code_tags report  --module demo.__main__ --src demo --format keep-a-changelog>demo_reports/CHANGELOG.md
echo "-------------------------------------"
code_tags report  --module demo.__main__ --src demo --format todo.md>demo_reports/todo.md
