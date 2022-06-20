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

SCANDICS = [
    'da',
    'sv',
    'no',
    'fi'
]

LABELS = dict(
    published_year='Year of Publication',
    crossref_type='Crossref Type',
    pc_crossref_type='Proportion by Type (%)',
    value='Proportion by OA Category (%)',
    name='Language',
    total='Count of Outputs',
    variable='Category of  Open Access',
    pc_of_year='Proportion of Outputs (%)',
    pc_diamond='Non-APC DOAJ Journal (%)',
    pc_doaj_apc='DOAJ Journal with APCs (%)',
    pc_hybrid='Open in non-DOAJ Journal (%)',
    pc_bronze='Free to read (%)',
    pc_green_only='Only OA in repository (%)',
    pc_closed='Closed (%)'
)

OA_CLASS_YS = [
    'Non-APC DOAJ Journal (%)',
    'DOAJ Journal with APCs (%)',
    'Open in non-DOAJ Journal (%)',
    'Free to read (%)',
    'Only OA in repository (%)',
    'Closed (%)'
]

oatypes_palette = {
    'Non-APC DOAJ Journal (%)': 'lightgrey',
    'DOAJ Journal with APCs (%)': 'gold',
    'Only OA in repository (%)': 'darkgreen',
    'Open in non-DOAJ Journal (%)': 'orange',
    'Free to read (%)': 'brown',
    'Closed (%)': '#454545'
}

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
    fig = px.pie(graph_data, values='total', names='index', labels=LABELS)
    fig.write_image(GRAPH_DIR / 'pie_all_years.png')
    fig.write_html(GRAPH_DIR / 'pie_all_years.html')

    # Pie All Years Non-English
    graph_data = concatenate_others(downloaded[downloaded.code != 'en'], slices=15)
    fig = px.pie(graph_data, values='total', names='index', labels=LABELS)
    fig.write_image(GRAPH_DIR / 'pie_allyears_nonenglish.png')
    fig.write_html(GRAPH_DIR / 'pie_allyears_nonenglish.html')

    # Pie 2020
    graph_data = concatenate_others(downloaded[downloaded.published_year == 2020], slices=7)
    fig = px.pie(graph_data, values='total', names='index', labels=LABELS)
    fig.write_image(GRAPH_DIR / 'pie_2020.png')
    fig.write_html(GRAPH_DIR / 'pie_2020.html')

    # Pie 2020 Non-English
    graph_data = concatenate_others(downloaded[(downloaded.code != 'en') &
                                               (downloaded.published_year == 2020)], slices=15)
    fig = px.pie(graph_data, values='total', names='index', labels=LABELS)
    fig.write_image(GRAPH_DIR / 'pie_2020_nonenglish.png')
    fig.write_html(GRAPH_DIR / 'pie_2020_nonenglish.html')

    # Pie by Crossref Type: English
    graph_data = concatenate_others(downloaded[downloaded.code == 'en'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index', labels=LABELS)
    fig.write_image(GRAPH_DIR / 'pie_crtype_en.png')
    fig.write_html(GRAPH_DIR / 'pie_crtype_en.html')

    # Pie by Crossref Type: German
    graph_data = concatenate_others(downloaded[downloaded.code == 'de'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index', labels=LABELS)
    fig.write_image(GRAPH_DIR / 'pie_crtype_de.png')
    fig.write_html(GRAPH_DIR / 'pie_crtype_de.html')

    # Pie by Crossref Type: French
    graph_data = concatenate_others(downloaded[downloaded.code == 'fr'],
                                    value_column='total',
                                    group_column='crossref_type')
    fig = px.pie(graph_data, values='total', names='index', labels=LABELS)
    fig.write_image(GRAPH_DIR / 'pie_crtype_fr.png')
    fig.write_html(GRAPH_DIR / 'pie_crtype_fr.html')

    # Sunburst of Crossref Type by Language (large languages plus english)
    graph_data = downloaded[downloaded.code.isin(LARGE_LANGUAGES + ['en'])].groupby(['name', 'crossref_type']).sum()
    graph_data.reset_index(inplace=True)
    fig = px.sunburst(graph_data,
                      path=['name', 'crossref_type'],
                      values='total',
                      labels=LABELS)
    fig.write_image(GRAPH_DIR / 'sunburst_crtype_large+en.png')
    fig.write_html(GRAPH_DIR / 'sunburst_crtype_large+en.html')

    # Stacked Bar of Crossref Types by Langauge (large languages plus English)
    language_totals = downloaded[['name', 'total']].groupby('name').sum().to_dict()['total']
    graph_data['language_total'] = graph_data.name.map(language_totals)
    graph_data.sort_values(['language_total', 'total'], ascending=False, inplace=True)
    graph_data['pc_crossref_type'] = graph_data.total / graph_data.language_total * 100
    fig = px.bar(graph_data,
                 x='name',
                 y='pc_crossref_type',
                 color='crossref_type',
                 labels=LABELS,
                 range_y=[0, 100])
    fig.write_image(GRAPH_DIR / 'stackedbar_crtype_large+en.png')
    fig.write_html(GRAPH_DIR / 'stackedbar_crtype_large+en.html')

    # Languages Line Graph 2000 - 2020 - Totals
    filtered = downloaded[downloaded.code.isin(LARGE_LANGUAGES)]
    all_by_year = filtered.groupby(['name', 'published_year']).sum().reset_index()
    fig = px.line(all_by_year,
                  x='published_year',
                  y='total',
                  color='name',
                  labels=LABELS
                  )
    fig.write_image(GRAPH_DIR / 'line_counts_overtime_largelang.png')
    fig.write_html(GRAPH_DIR / 'line_counts_overtime_largelang.html')

    # Languages Line Graph 2000 - 2020 proportions of total
    filtered = downloaded[downloaded.code.isin(LARGE_LANGUAGES + ['en'])]
    all_by_year = filtered.groupby(['name', 'published_year']).sum().reset_index()
    year_totals = downloaded.groupby('published_year').sum().to_dict()['total']
    all_by_year['year_total'] = all_by_year['published_year'].map(year_totals)
    all_by_year['pc_of_year'] = all_by_year.total / all_by_year.year_total * 100
    all_by_year.sort_values(['published_year', 'pc_of_year'], ascending=False, inplace=True)
    fig = px.area(all_by_year,
                  x='published_year',
                  y='pc_of_year',
                  color='name',
                  labels=LABELS,
                  range_y=[0, 100])
    fig.write_image(GRAPH_DIR / 'area_pc_overtime_largelang.png')
    fig.write_html(GRAPH_DIR / 'area_pc_overtime_largelang.html')

    # Languages Line Graph 2000 - 2020 - Journal Articles Only
    filtered = downloaded[(downloaded.code.isin(LARGE_LANGUAGES + ['en'])) &
                          (downloaded.crossref_type == 'journal-article')]

    all_by_year = filtered.groupby(['name', 'published_year']).sum().reset_index()
    fig = px.line(all_by_year,
                  x='published_year',
                  y='total',
                  color='name',
                  labels=LABELS)
    fig.write_image(GRAPH_DIR / 'line_counts_overtime_journal-articles_largelang.png')
    fig.write_html(GRAPH_DIR / 'line_counts_overtime_journal-articles_largelang.html')

    # Set up percentages for each year and for all years
    combined_years = downloaded.groupby(['code', 'name']).sum().reset_index()
    combined_years.sort_values('total', ascending=False, inplace=True)

    by_years = downloaded.groupby(['published_year', 'code', 'name']).sum().reset_index()
    by_years.sort_values('total', ascending=False, inplace=True)
    for df in [by_years, combined_years]:
        for col in COUNT_COLUMNS:
            colname = f'pc_{col}'
            df[colname] = df[f'count_{col}'] / df.total * 100
            if LABELS.get(colname):
                df[LABELS.get(colname)] = df[colname]
        df['pc_doaj_apc'] = df.pc_doaj - df.pc_diamond
        df['DOAJ Journal with APCs (%)'] = df['pc_doaj_apc']
        df['pc_closed'] = 100 - df.pc_oa
        df['Closed (%)'] = df['pc_closed']

    # OA Classes for all time, large languages
    fig = px.bar(combined_years[combined_years.code.isin(LARGE_LANGUAGES + ['en'])],
                 x='name',
                 y=OA_CLASS_YS,
                 labels=LABELS,
                 color_discrete_map=oatypes_palette,
                 range_y=[0, 100])
    fig.write_image(GRAPH_DIR / 'stackedbar_oaclasses_alltime_largelang.png')
    fig.write_html(GRAPH_DIR / 'stackedbar_oaclasses_alltime_largelang.html')

    # OA Classes for 2020, large languages
    fig = px.bar(by_years[(by_years.code.isin(LARGE_LANGUAGES + ['en'])) &
                          (by_years.published_year == 2020)],
                 x='name',
                 y=OA_CLASS_YS,
                 labels=LABELS,
                 color_discrete_map=oatypes_palette,
                 range_y=[0, 100])
    fig.write_image(GRAPH_DIR / 'stackedbar_oaclasses_2020_largelang.png')
    fig.write_html(GRAPH_DIR / 'stackedbar_oaclasses_2020_largelang.html')

    # OA Classes for all time, Scandics
    fig = px.bar(combined_years[combined_years.code.isin(SCANDICS + ['en'])],
                 x='name',
                 y=OA_CLASS_YS,
                 labels=LABELS,
                 color_discrete_map=oatypes_palette,
                 range_y=[0, 100])
    fig.write_image(GRAPH_DIR / 'stackedbar_oaclasses_alltime_scandics.png')
    fig.write_html(GRAPH_DIR / 'stackedbar_oaclasses_alltime_scandics.html')

    # OA Classes for 2020, Scandics
    fig = px.bar(by_years[(by_years.code.isin(SCANDICS + ['en'])) &
                          (by_years.published_year == 2020)],
                 x='name',
                 y=OA_CLASS_YS,
                 labels=LABELS,
                 color_discrete_map=oatypes_palette,
                 range_y=[0, 100])
    fig.write_image(GRAPH_DIR / 'stackedbar_oaclasses_2020_scandics.png')
    fig.write_html(GRAPH_DIR / 'stackedbar_oaclasses_2020_scandics.html')

    # OA Classes for 2020, Scandics
    fig = px.bar(by_years[(by_years.code.isin(['en', 'de', 'fr', 'nl', 'no', 'da', 'hu', 'pl', 'bg'])) &
                          (by_years.published_year == 2020)],
                 x='name',
                 y=OA_CLASS_YS,
                 labels=LABELS,
                 color_discrete_map=oatypes_palette,
                 range_y=[0, 100])
    fig.write_image(GRAPH_DIR / 'stackedbar_oaclasses_2020_northeuropecompare.png')
    fig.write_html(GRAPH_DIR / 'stackedbar_oaclasses_2020_northeuropecompare.html')

    # Mean citations for journal articles by language for 2020
    graph_data = downloaded[(downloaded.published_year == 2020) &
                            (downloaded.crossref_type == 'journal-article') &
                            (downloaded.code.isin(LARGE_LANGUAGES + ['en']))]
    graph_data.sort_values('total', ascending=False, inplace=True)
    fig = px.bar(graph_data,
                 x='name',
                 y='mean_citations')
    fig.write_image(GRAPH_DIR / 'bar_meancites_2020_large.png')
    fig.write_html(GRAPH_DIR / 'bar_meancites_2020_large.html')

    # Mean citations at 2years for journal articles by language for 2000-2019
    graph_data = downloaded[(downloaded.published_year.isin(range(2000, 2020))) &
                            (downloaded.crossref_type == 'journal-article') &
                            (downloaded.code.isin(LARGE_LANGUAGES + ['en']))]
    graph_data.sort_values(['published_year', 'total'], ascending=False, inplace=True)
    fig = px.line(graph_data,
                  x='published_year',
                  y='mean_citations2y',
                  color='name')
    fig.write_image(GRAPH_DIR / 'line_meancites2y_2000-2019_large.png')
    fig.write_html(GRAPH_DIR / 'line_meancites2y_2000-2019_large.html')


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
