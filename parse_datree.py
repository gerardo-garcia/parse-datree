#!/usr/bin/python3

# parse_datree <yaml_file>

import yaml
import json
import sys
import argparse

# from prettytable import PrettyTable
import logging
import pandas as pd
from tabulate import tabulate


####################################
# Global functions
####################################
def print_yaml_json(headers, rows, to_json=False):
    output = []
    for row in rows:
        item = {}
        for i in range(len(row)):
            item[headers[i]] = row[i]
        output.append(item)
    if to_json:
        print(json.dumps(output, indent=4))
    else:
        print(yaml.safe_dump(output, indent=4, default_flow_style=False, sort_keys=False))


# def print_pretty_table(headers, rows):
#     table = PrettyTable(headers)
#     for row in rows:
#         table.add_row(row)
#     table.align = "l"
#     print(table)


# def print_csv(headers, rows):
#     print(",".join(headers))
#     for row in rows:
#         str_row = list(map(str, row))
#         print(",".join(str_row))


def print_formatted_table(headers, rows, output_format):
    df = pd.DataFrame(rows, columns=headers)
    if output_format == "table":
        # print_pretty_table(headers, rows)
        print(tabulate(df, headers="keys", tablefmt="pretty", disable_numparse=True, showindex=False, stralign="left"))
    elif output_format == "csv":
        # print_csv(headers, rows)
        print(df.to_csv(index=False))
    elif output_format == "markdown":
        print(df.to_markdown(index=False))
    elif output_format == "excel":
        df.to_excel("output.xlsx", index=False)


def print_table(headers, rows, output_format):
    if output_format in ["table", "csv", "excel", "markdown"]:
        print_formatted_table(headers, rows, output_format)
    else:
        to_json = True if output_format == "json" else True
        print_yaml_json(headers, rows, to_json)


def set_logger(verbose):
    global logger
    log_format_simple = "%(levelname)s %(message)s"
    log_format_complete = "%(asctime)s %(levelname)s %(name)s %(filename)s:%(lineno)s %(funcName)s(): %(message)s"
    log_formatter_simple = logging.Formatter(log_format_simple, datefmt="%Y-%m-%dT%H:%M:%S")
    handler = logging.StreamHandler()
    handler.setFormatter(log_formatter_simple)
    logger = logging.getLogger("parse-datree")
    logger.setLevel(level=logging.WARNING)
    logger.addHandler(handler)
    if verbose == 1:
        logger.setLevel(level=logging.INFO)
    elif verbose > 1:
        log_formatter = logging.Formatter(log_format_complete, datefmt="%Y-%m-%dT%H:%M:%S")
        handler.setFormatter(log_formatter)
        logger.setLevel(level=logging.DEBUG)


####################################
# Main
####################################
if __name__ == "__main__":
    # Argument parse
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        choices=["table", "csv", "yaml", "json", "excel", "markdown"],
        default="table",
        help="output format",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="datree_issue_mapping.yaml",
        help="config file to map the datree issues with an impact and relevance",
    )
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase output verbosity")
    args = parser.parse_args()

    # Initialize logger
    set_logger(args.verbose)

    # Load configuration file
    with open(args.config, "r") as cf:
        MAP_ISSUES = yaml.safe_load(cf.read())
        logger.debug(f"MAP_ISSUES: ${MAP_ISSUES}")

    # Initialize variables
    headers = [
        "INTERNAL ID #",
        "NF",
        "ISSUE ID",
        "ISSUE",
        "RELEVANCE",
        "IMPACT",
        "DESCRIPTION",
        "DETAILS",
        "RESOLUTION",
    ]
    rows = []

    # Read Manifests and get container params
    manifest_generator = yaml.safe_load_all(sys.stdin)
    internal_id = 0
    for manifest in manifest_generator:
        if not manifest:
            logger.info("Empty manifest")
            continue
        datree_results = manifest.get("policyValidationResults", [])
        rules_failed = manifest["policySummary"]["totalRulesFailed"]
        for file in datree_results:
            filename = file.get("fileName")
            rule_results = file.get("ruleResults", [])
            logger.info(f"Expected failed rules: {rules_failed}. Found: {len(rule_results)}")
            for rule in rule_results:
                internal_id += 1
                issue_id = rule["identifier"]
                issue = rule["name"]
                try:
                    relevance = MAP_ISSUES[issue_id]["relevance"]
                except KeyError:
                    relevance = "UNKNOW"
                try:
                    impact = MAP_ISSUES[issue_id]["impact"]
                description = rule["messageOnFailure"]
                details = rule["occurrencesDetails"]
                details_list = []
                for oc in details:
                    metadataName = oc["metadataName"]
                    kind = oc["kind"]
                    failureLocations = oc["failureLocations"]
                    details_list.append(f"- metadata.name: {metadataName} (kind: {kind})")
                    for fl in failureLocations:
                        point = fl["schemapath"].replace("/", ".")
                        line = fl["failederrorline"]
                        column = fl["failederrorcolumn"]
                        details_list.append(f"  > key: {point} (line: {line}:{column})")
                details_text = "TBD"
                if details_list:
                    details_text = "\n".join(details_list)
                    details_text = f"'{details_text}"
                resolution = rule["documentationUrl"]
                row_to_be_added = [
                    f"{internal_id}",
                    filename,
                    issue_id,
                    issue,
                    relevance,
                    impact,
                    description,
                    details_text,
                    resolution,
                ]
                logger.info(row_to_be_added)
                rows.append(row_to_be_added)
    print_table(headers, rows, args.output)
