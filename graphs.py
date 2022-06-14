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
    'tr',
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
    fig.write_image(GRAPH_DIR / 'pie_all_years.png')

    # Pie All Years Non-English
    graph_data = concatenate_others(downloaded[downloaded.code != 'en'], slices=15)
    fig = px.pie(graph_data, values='total', names='index')
    fig.write_image(GRAPH_DIR / 'pie_allyears_nonenglish.png')

    # Pie 2020
    graph_data = concatenate_others(downloaded[downloaded.published_year == 2020], slices=7)
    fig = px.pie(graph_data, values='total', names='index')
    fig.write_image(GRAPH_DIR / 'pie_2020.png')

    # Pie 2020 Non-English
    graph_data = concatenate_others(downloaded[(downloaded.code != 'en') &
                                               (downloaded.published_year == 2020)], slices=15)
    fig = px.pie(graph_data, values='total', names='index')
    fig.write_image(GRAPH_DIR / 'pie_2020_nonenglish.png')

    # Pie by Crossref Type: English
    graph_data = concatenate_others(downloaded[downloaded.code == 'en'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index')
    fig.write_image(GRAPH_DIR / 'pie_crtype_en.png')

    # Pie by Crossref Type: German
    graph_data = concatenate_others(downloaded[downloaded.code == 'de'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index')
    fig.write_image(GRAPH_DIR / 'pie_crtype_de.png')

    # Pie by Crossref Type: French
    graph_data = concatenate_others(downloaded[downloaded.code == 'fr'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index')
    fig.write_image(GRAPH_DIR / 'pie_crtype_fr.png')

    # Sunburst of Crossref Type by Language (large languages plus english)
    graph_data = downloaded[downloaded.code.isin(LARGE_LANGUAGES + ['en'])].groupby(['name', 'crossref_type']).sum()
    graph_data.reset_index(inplace=True)
    fig = px.sunburst(graph_data,
                      path=['name', 'crossref_type'],
                      values='total')
    fig.write_image(GRAPH_DIR / 'sunburst_crtype_large+en.png')

    # Stacked Bar of Crossref Types by Langauge (large languages plus English)
    language_totals = downloaded[['name', 'total']].groupby('name').sum().to_dict()['total']
    graph_data['language_total'] = graph_data.name.map(language_totals)
    graph_data.sort_values(['language_total', 'total'], ascending=False, inplace=True)
    graph_data['pc_crossref_type'] = graph_data.total / graph_data.language_total * 100
    fig = px.bar(graph_data,
                 x='name',
                 y='pc_crossref_type',
                 color='crossref_type')
    fig.write_image(GRAPH_DIR / 'stackedbar_crtype_large+en.png')

    # Languages Line Graph 2000 - 2020 - Totals
    filtered = downloaded[downloaded.code.isin(LARGE_LANGUAGES)]
    all_by_year = filtered.groupby(['name', 'published_year']).sum().reset_index()
    fig = px.line(all_by_year,
                  x='published_year',
                  y='total',
                  color='name')
    fig.write_image(GRAPH_DIR / 'line_counts_overtime_largelang.png')

    # Languages Line Graph 2000 - 2020 - Journal Articles Only
    filtered = downloaded[(downloaded.code.isin(LARGE_LANGUAGES)) &
                          (downloaded.crossref_type == 'journal-article')]
    all_by_year = filtered.groupby(['name', 'published_year']).sum().reset_index()
    fig = px.line(all_by_year,
                  x='published_year',
                  y='total',
                  color='name')
    fig.write_image(GRAPH_DIR / 'line_counts_overtime_journal-articles_largelang.png')

    # Set up percentages for each year and for all years
    combined_years = downloaded.groupby(['code', 'name']).sum().reset_index()
    combined_years.sort_values('total', ascending=False, inplace=True)

    by_years = downloaded.groupby(['published_year', 'code', 'name']).sum().reset_index()
    by_years.sort_values('total', ascending=False, inplace=True)
    for df in [by_years, combined_years]:
        for col in COUNT_COLUMNS:
            df[f'pc_{col}'] = df[f'count_{col}'] / df.total * 100
        df['pc_doaj_apc'] = df.pc_doaj - df.pc_diamond
        df['pc_closed'] = 100 - df.pc_oa

    # OA Classes for all time, large languages
    fig = px.bar(combined_years[combined_years.code.isin(LARGE_LANGUAGES + ['en'])],
                 x='name',
                 y=['pc_diamond', 'pc_doaj_apc', 'pc_hybrid', 'pc_bronze', 'pc_green_only', 'pc_closed'])
    fig.write_image(GRAPH_DIR / 'stackedbar_oaclasses_alltime_largelang.png')

    # OA Classes for 2020, large languages
    fig = px.bar(by_years[(by_years.code.isin(LARGE_LANGUAGES + ['en'])) &
                          (by_years.published_year == 2020)],
                 x='name',
                 y=['pc_diamond', 'pc_doaj_apc', 'pc_hybrid', 'pc_bronze', 'pc_green_only', 'pc_closed'])
    fig.write_image(GRAPH_DIR / 'stackedbar_oaclasses_2020_largelang.png')


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
