# COKI Language Detection
This project contains a script to detect the language of academic papers
based on their titles and abstracts.

## Pre-requisites
* Python 3.8.

## Setup
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

## Running
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
gsutil -m cp -R . gs://your-bucket-name/coki-language
```