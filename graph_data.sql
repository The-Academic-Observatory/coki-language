WITH
  languages AS (
    SELECT * FROM `academic-observatory.mockup.doi_language` as l JOIN `academic-observatory.mockup.iso_language` as n on l.language = n.code
  ),
  mapped_dois AS (
    SELECT
      d.doi,
      languages.code,
      languages.name,
      languages.score,
      apc,
      crossref.published_year,
      unpaywall.* EXCEPT(doi),
      open_citations.* EXCEPT(doi)

    FROM
      languages
      LEFT JOIN `academic-observatory.observatory.doi20220528` as d ON d.doi = languages.doi
      LEFT JOIN `utrecht-university.doaj.apc_issnl_20220427` as a on a.journal_issn_l = d.unpaywall.journal_issn_l

    WHERE crossref.published_year > 1999 and crossref.published_year < 2022
  )

SELECT
  published_year,
  code,
  name,
  COUNT(DISTINCT doi) as total,
  AVG(score) as avg_score,
  COUNT(DISTINCT(IF(is_oa, doi, null))) as count_oa,
  COUNT(DISTINCT(IF(gold, doi, null))) as count_gold,
  COUNT(DISTINCT(IF(green, doi, null))) as count_green,
  COUNT(DISTINCT(IF(bronze, doi, null))) as count_bronze,
  COUNT(DISTINCT(IF(hybrid, doi, null))) as count_hybrid,
  COUNT(DISTINCT(IF(gold_just_doaj, doi, null))) as count_doaj,
  COUNT(DISTINCT IF(gold_just_doaj and (apc=false), doi, null)) as count_diamond,
  COUNT(DISTINCT(IF(green_only, doi, null))) as count_green_only,
  COUNT(DISTINCT(IF(green_only_ignoring_bronze, doi, null))) as count_green_only_ignoring_bronze,
  COUNT(DISTINCT(IF(is_cclicensed, doi, null))) as count_cc_licensed,
  AVG(citations_total) as mean_citations,
  AVG(citations_two_years) as mean_citations2y

  FROM mapped_dois
  GROUP BY published_year, code, name
  ORDER BY published_year DESC, name ASC
