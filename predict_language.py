# Copyright 2022 Curtin University
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import csv
import glob
import gzip
import html
import io
import logging
import os
import os.path
import re
import sys

import click
import fasttext
import ray
import validators
from bs4 import BeautifulSoup


def list_files(path: str, pattern: str):
    """List files in a directory.

    :param path: the path to the directory.
    :param pattern: the file pattern to list.
    :return: yield the file paths.
    """

    return glob.glob(os.path.join(path, pattern))


def read_csv_gz(path: str, skip_header: bool = True):
    """Read a gzipped CSV file.

    :param path: the path to the csv.gz file.
    :param skip_header: whether to skip the header or not.
    :return: yield each row to conserve memory.
    """

    with gzip.open(path, "r") as f:
        reader = csv.reader(io.TextIOWrapper(f, newline=""))
        if skip_header:
            next(reader, None)
        for row in reader:
            yield row


def is_doi(text: str):
    """Returns whether the text is a Crossref DOI or not.

    See here for explanation: https://www.crossref.org/blog/dois-and-matching-regular-expressions/

    :param text: the text.
    :return: whether the text is a Crossref DOI or not.
    """

    return re.match(r"^10.\d{4,9}/[-._;()/:A-Z0-9]+$", text, re.IGNORECASE) is not None


def preprocess_text(text: str):
    """Pre-process the text.

    :param text: the text.
    :return: return the pre-processed text.
    """

    if text is None:
        return ""

    # Strip
    text = text.strip()

    # If text is empty
    if text == "":
        return ""

    # If text is only [NO TITLE AVAILABLE]
    if text == "[NO TITLE AVAILABLE]":
        return ""

    # If DOI return None
    if is_doi(text):
        return ""

    # If URL return None
    if validators.url(text):
        return ""

    # Unescape HTML tags
    text = html.unescape(text)

    # Strip HTML
    soup = BeautifulSoup(text, features="html.parser")
    text = soup.get_text()

    # Remove latext
    # text = latex2text(text)

    # Remove redundant spaces
    text = " ".join(text.split())

    # Remove newlines
    text = text.replace("\n", "")

    # Strip non utf-8 characters
    text = text.encode("utf-8", "ignore").decode("utf-8")

    return text


@ray.remote
def process_archive(
    csv_path: str, output_path: str, model_path: str = os.path.join(os.path.expanduser("~"), ".fasttext/lid.176.bin")
):
    """A remote ray function that predicts language for a single .csv.gz archive.

    :param csv_path: the path to the .csv.gz file.
    :param output_path: the output directory where the results should be saved.
    :param model_path: the path to the fasttext model.
    :return: return the results.
    """

    # Prevent this error: _csv.Error: field larger than field limit (131072)
    csv.field_size_limit(sys.maxsize)

    print(f"Running task: {csv_path}")
    model = fasttext.load_model(model_path)
    output_file_path = os.path.join(output_path, os.path.basename(csv_path))
    with gzip.open(output_file_path, "w") as f:
        # Make CSV writer and write header
        writer = csv.writer(io.TextIOWrapper(f, newline=""))
        writer.writerow(["doi", "title", "language", "score"])

        # Process each row of the CSV file
        for row in read_csv_gz(csv_path):
            # Read data
            doi = row[0]
            mag_title = row[1]
            crossref_title = row[2]
            mag_abstract = row[3]
            crossref_abstract = row[4]

            # Pre-process text
            pre_mag_title = preprocess_text(mag_title)
            pre_crossref_title = preprocess_text(crossref_title)
            pre_mag_abstract = preprocess_text(mag_abstract)
            pre_crossref_abstract = preprocess_text(crossref_abstract)

            # Select longest of titles if both exist and combine not None
            title = max([pre_crossref_title, pre_mag_title], key=len)
            abstract = max([pre_crossref_abstract, pre_mag_abstract], key=len)
            text = " ".join(list(filter(None, [title, abstract]))).strip()

            # Predict
            label, score = None, None
            if text != "":
                top = model.predict(text, k=1)
                label = top[0][0][9:]
                score = top[1][0]

            # Set title to None if empty string for final dataset
            if title == "":
                title = None

            # Write results
            writer.writerow([doi, title, label, score])

    return csv_path


@click.command("predict-language")
@click.argument("input-path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.argument("output-path", type=click.Path(exists=True, file_okay=False, dir_okay=True))
@click.option(
    "--file-pattern", type=click.STRING, default="*.csv.gz", help="The file pattern to use when search for files"
)
def predict_language_cmd(input_path: str, output_path: str, file_pattern: str):
    # Create tasks
    task_ids = []
    for csv_path in list_files(input_path, file_pattern):
        print(f"Creating task: {csv_path}")
        task_id = process_archive.remote(csv_path, output_path)
        task_ids.append(task_id)

    # Join tasks
    count = 0
    while True:
        finished, not_finished = ray.wait(task_ids, num_returns=len(task_ids), timeout=10.0)

        # Add the results that have completed
        for task_id in finished:
            csv_path = ray.get(task_id)
            count += 1
            print(f"Finished task: {csv_path}")
        task_ids = not_finished

        print(f"Tasks finished: {count}, tasks waiting: {len(task_ids)}.")

        # Break when no tasks
        if len(task_ids) == 0:
            break

    print("Complete")


if __name__ == "__main__":
    predict_language_cmd()
