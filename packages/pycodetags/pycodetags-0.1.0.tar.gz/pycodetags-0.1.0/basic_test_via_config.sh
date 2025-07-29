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
# Don't export reports to same folder where you search for code tags!
export CODE_TAGS_NO_OPEN_BROWSER=1
formats=("text" "html" "json" "keep-a-changelog" "todo.md" "done")
labels=("text" "html" "json" "changelog" "todo.md" "done")

if [[ -z "$CI" ]]; then
  code_tags report
  for i in "${!formats[@]}"; do
    echo "----------${labels[$i]}---------------------------"
    code_tags report --format "${formats[$i]}"
  done
else
  code_tags report > code_tags_report_default.txt
  for i in "${!formats[@]}"; do
    echo "----------${labels[$i]}---------------------------" >> code_tags_report_all.txt
    code_tags report --format "${formats[$i]}" >> code_tags_report_all.txt
  done
fi