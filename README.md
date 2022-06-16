# COKI Language Detection
This project contains scripts to detect the language of academic papers based on their titles and abstracts and to
analyse them.

The data produced by these scripts is available on Zenodo as the [COKI Language Dataset](https://zenodo.org/record/6636625) and also publicly accessible in [BigQuery](https://cloud.google.com/bigquery):
* [coki-data-share.language.doi_language](https://console.cloud.google.com/bigquery?referrer=search&project=coki-data-share&ws=!1m5!1m4!4m3!1scoki-data-share!2slanguage!3sdoi_language)
* [coki-data-share.language.iso_language](https://console.cloud.google.com/bigquery?referrer=search&project=coki-data-share&ws=!1m5!1m4!4m3!1scoki-data-share!2slanguage!3siso_language)

See the `output_graphs` folder for charts and aggregated data.

## 1. Pre-requisites
* Python 3.8
* gsutil: https://cloud.google.com/storage/docs/gsutil_install
* bq: https://cloud.google.com/bigquery/docs/bq-command-line-tool

## 2. Loading Data into BigQuery
The following are instructions for manually downloading and loading this data into BigQuery for analysis.

### 2.1. Setup
Install zenodo-get, which is used to fetch the URLs for the Zenodo archive:
```bash
pip install zenodo-get
```

Install aria2c which is used to download the files from Zenodo in parallel:
* Ubuntu: `sudo snap install aria2c`
* Windows: https://github.com/aria2/aria2/releases/tag/release-1.36.0
* Mac: https://formulae.brew.sh/formula/aria2

### 2.2. Download Data
Make a folder to work from:
```bash
mkdir coki-language
cd coki-language
```

Download the data:
```bash
zenodo_get 10.5281/zenodo.6636624 -w urls.txt
aria2c -i urls.txt --max-concurrent-downloads=12
```

Downloading data with zenodo-get, as a fallback, it is slow though: 
```bash
zenodo_get 10.5281/zenodo.6636624
```

### 2.2. Upload to Google Cloud Storage Bucket
```bash
gsutil -m cp -R . gs://my-bucket/coki-language
```

### 2.3. Loading into BigQuery
Make sure you are in the root of this repository.

Make a dataset:
```bash
bq mk --dataset_id my-gcp-project-id:coki_language --location us
```

Create the iso_language table:
```bash
bq load --skip_leading_rows=1 my-gcp-project-id:coki_language.iso_language gs://my-bucket/coki-language/iso_language.csv ./iso_language_schema.json
```

Create the doi_language table:
```bash
bq load --skip_leading_rows=1 my-gcp-project-id:coki_language.doi_language gs://my-bucket/coki-language/*.csv.gz ./doi_language_schema.json
```

## 3. Detecting Language from Scratch

### 3.1. Setup
Install system dependencies:
```bash
sudo apt install build-essential python3-dev
```

Create virtual env:
```bash
python3 -m venv venv
```

Source virtual env:
```bash
source venv/bin/activate
```

Install Python dependencies:
```bash
pip install -r requirements.txt
```

Download fasttext lid.176.bin model:
```bash
mkdir -p ~/.fasttext
curl -o ~/.fasttext/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
```

Run the SQL query from `create_dataset.sql` in BigQuery, saving the results in a table and then export the files
to .csv.gz format, saving them on a Google Cloud Storage bucket.

Download the files and save them to the `data/input` folder.

### 3.2. Running
To run the program:
```bash
python3 predict_language.py predict-language ./data/input ./data/output
```

Running with nohup:
```bash
nohup python3 predict_language.py ./data/input ./data/output &> predict-language.log &
```

Upload data to cloud storage bucket:
```bash
gsutil -m cp -R . gs://my-bucket/coki-language
```

Go to [section 2.3](#23-loading-into-bigquery) for instructions on how to load the data into BigQuery.
