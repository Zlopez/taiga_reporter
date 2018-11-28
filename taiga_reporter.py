#!/usr/bin/env python3
"""
This script is generating readable report from taiga.io CSV report.
"""
import requests
import os
import csv
import re

REPORT_URL = "https://api.taiga.io/api/v1/userstories/csv?uuid=b62e5a3fae554b479e6d56d5e50690f6"
SUBJECT_FIELD = "subject"
DESCRIPTION_FIELD = "description"
STATUS_FIELD = "status"
TAGS_FIELD = "tags"

STATUS_TODO = "TODO"
STATUS_BLOCKED = "BLOCKED"
STATUS_PLANNED = "PLANNED"
STATUS_IN_PROGRESS = "IN PROGRESS"
STATUS_IN_REVIEW = "IN REVIEW"
STATUS_DONE = "DONE"

WATCHED_STATUSES = [
    STATUS_TODO, STATUS_BLOCKED, STATUS_PLANNED,
    STATUS_IN_PROGRESS, STATUS_IN_REVIEW, STATUS_DONE
]

counter = 0


def get_report():
    """
    Download the report and returns csv dictionary.
    """
    response = requests.get(REPORT_URL)
    return csv.DictReader(response.content.decode().split('\r\n'))


def get_rows_by_status(input_dict):
    """
    Splits the input_dict to several dictionaries.

    Args:
        input_dict (`Ordered_dict`): input dictionary containing parsed CSV rows

    Returns:
        (`dict`): Dictionary of `list` containing the split rows
    """
    output_dict = {}
    for status in WATCHED_STATUSES:
        output_dict[status] = []
    for row in input_dict:
        status = row[STATUS_FIELD].upper()
        if status in WATCHED_STATUSES:
            output_dict[status].append(row)

    return output_dict


def get_urls(text):
    """
    Get list of urls from text.

    Args:
        text (str): Text to parse.

    Returns:
        (`list`): List of urls in `str`.
    """
    return re.findall(r'http?s://[^\s]*', text)


def prepare_section(rows):
    """
    Prepare one section of report using input rows.

    Args:
        rows (`list`): List of CSV rows in `OrderedDict`

    Returns:
        (`tuple`): Returns `tuple` of `str`.
            First contains prepared section.
            Second contains parsed urls.
    """
    global counter
    tags_dict = {}
    section = ''
    urls = ''
    for row in rows:
        if row[TAGS_FIELD] not in tags_dict:
            tags_dict[row[TAGS_FIELD]] = []
        tags_dict[row[TAGS_FIELD]].append(row)

    for (key, val) in tags_dict.items():
        section += "{}:\n".format(key)
        for row in val:
            section += "* {}".format(row[SUBJECT_FIELD])
            for url in get_urls(row[DESCRIPTION_FIELD]):
                urls += "[{}] - {}\n".format(counter, url)
                section += " [{}]".format(counter)
                counter += 1
            section += "\n"
        section += "\n"

    return section, urls


def prepare_report(input_dict):
    """
    Prepare report from split dictionary.

    Args:
        input_dict (`dict`): Split CSV rows

    Returns:
        (str): String that contains prepared report
    """
    report = ''
    urls = ''
    for status in WATCHED_STATUSES:
        section, section_urls = prepare_section(input_dict[status])
        if section:
            report += "{}\n".format(status)
            report += "=" * len(status)
            report += "\n{}\n".format(section)
            urls += section_urls

    report += "\n"
    report += urls[:-1]

    return report


if __name__ == "__main__":
    csv_dict = get_report()

    csv_dicts = get_rows_by_status(csv_dict)

    output = prepare_report(csv_dicts)
    print(output)
