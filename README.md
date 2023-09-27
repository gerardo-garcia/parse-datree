# parse-datree

This program takes as input a report from [datree](https://hub.datree.io/) in yaml format and generates an enhanced report with the detected issues in table, CSV or Excel format.

Based on the datree issue mapping configured in file `datree_issue_mapping.yaml`, the program adds two columns with respect to the default datree report:

- Relevance: "01-HIGH", "02-MEDIUM" or "03-LOW"
- Impact: a summary of the impact of the issue

## Getting started

```bash
./parse_datree.py  -h
 
helm repo add apache-airflow https://airflow.apache.org
helm repo update
helm pull apache-airflow/airflow --version 1.6.0

helm -n airflow-ns datree test -o yaml --verbose ./airflow-1.6.0.tgz -- --release-name airflow | ./parse_datree.py
helm -n airflow-ns datree test -o yaml --verbose ./airflow-1.6.0.tgz -- --release-name airflow -f values.yaml | ./parse_datree.py
```

If you want the output in csv or markdown formats:

```bash
helm -n airflow-ns datree test -o yaml --verbose ./airflow-1.6.0.tgz -- --release-name airflow -f values.yaml | ./parse_datree.py -o csv
helm -n airflow-ns datree test -o yaml --verbose ./airflow-1.6.0.tgz -- --release-name airflow -f values.yaml | ./parse_datree.py -o markdown
```

It is also possible to export to Excel. A file named "output.xlsx" will be generated.

```bash
helm -n airflow-ns datree test -o yaml --verbose ./airflow-1.6.0.tgz -- --release-name airflow -f values.yaml | ./parse_datree.py -o excel
```

Finally it is also possible to use a customized datree issue mapping file with the option `--config`:

```bash
helm -n airflow-ns datree test -o yaml --verbose ./airflow-1.6.0.tgz -- --release-name airflow -f values.yaml | ./parse_datree.py --config new_mapping.yaml
```

## Requirements

- Python3
- [Datree](https://hub.datree.io/) ([Datree in Github](https://github.com/datreeio/datree))
