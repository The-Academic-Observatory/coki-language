import plotly.express as px
import pandas as pd
import os
from pathlib import Path

QUERY_SQL = Path('graph_data.sql')
GRAPH_DIR = Path('output_graphs')
CSV_FILE = 'downloaded_data.csv'
CSV_PATH = GRAPH_DIR / CSV_FILE
PROJECT = 'coki-scratch-space'
COUNT_COLUMNS = [
    'oa',
    'gold',
    'green',
    'bronze',
    'hybrid',
    'doaj',
    'bronze',
    'diamond',
    'green_only',
    'green_only_ignoring_bronze',
    'cc_licensed'
]

LARGE_LANGUAGES = [
    'de',
    'fr',
    'es',
    'pt',
    'id',
    'ru',
    'tu',
    'ja',
    'ar'
]

if not GRAPH_DIR.is_dir():
    os.mkdir(GRAPH_DIR)


def download_data():
    with open(QUERY_SQL) as f:
        query = f.read()

    data = pd.read_gbq(query,
                       project_id=PROJECT)
    data.to_csv(CSV_PATH, index=False)


def graphs():
    downloaded = pd.read_csv(CSV_PATH)

    # Pie All Years
    graph_data = concatenate_others(downloaded)
    fig = px.pie(graph_data, values='total', names='index')
    # fig.show()

    # Pie All Years Non-English
    graph_data = concatenate_others(downloaded[downloaded.code != 'en'], slices=15)
    fig = px.pie(graph_data, values='total', names='index')
    # fig.show()

    # Pie 2020
    graph_data = concatenate_others(downloaded[downloaded.published_year == 2020], slices=7)
    fig = px.pie(graph_data, values='total', names='index')
    # fig.show()

    # Pie 2020 Non-English
    graph_data = concatenate_others(downloaded[(downloaded.code != 'en') &
                                               (downloaded.published_year == 2020)], slices=15)
    fig = px.pie(graph_data, values='total', names='index')
    # fig.show()

    # Pie by Crossref Type: English
    graph_data = concatenate_others(downloaded[downloaded.code == 'en'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index')
    fig.show()

    # Pie by Crossref Type: German
    graph_data = concatenate_others(downloaded[downloaded.code == 'de'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index')
    fig.show()

    # Pie by Crossref Type: French
    graph_data = concatenate_others(downloaded[downloaded.code == 'fr'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index')
    fig.show()

    # Languages Line Graph 2000 - 2020 - Totals
    filtered = downloaded[downloaded.code.isin(LARGE_LANGUAGES)]
    all_by_year = filtered.groupby(['name', 'published_year']).sum().reset_index()
    fig = px.line(all_by_year,
                  x='published_year',
                  y='total',
                  color='name')
    #fig.show()

    # Languages Line Graph 2000 - 2020 - Journal Articles Only
    filtered = downloaded[(downloaded.code.isin(LARGE_LANGUAGES)) &
                          (downloaded.crossref_type == 'journal-article')]
    all_by_year = filtered.groupby(['name', 'published_year']).sum().reset_index()
    fig = px.line(all_by_year,
                  x='published_year',
                  y='total',
                  color='name')
    #fig.show()

    # Set up percentages for each year and for all years
    combined_years = downloaded.groupby('name').sum().reset_index()
    for df in [downloaded, combined_years]:
        for col in COUNT_COLUMNS:
            df[f'pc_{col}'] = df[f'count_{col}'] / df.total


def concatenate_others(df: pd.DataFrame,
                       value_column: str = 'total',
                       group_column: str = 'name',
                       slices: int = 7) -> pd.DataFrame:
    temp = df.groupby(group_column).sum()
    temp.sort_values(value_column, ascending=False, inplace=True)
    others = pd.DataFrame({'total': [temp.iloc[slices:][value_column].sum()]}, index=['Others'])

    return temp.iloc[:slices][[value_column]].append(others).reset_index()


if __name__ == '__main__':
    if not CSV_PATH.is_file():
        download_data()
    graphs()
