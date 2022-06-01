SELECT
  UPPER(TRIM(doi)) as doi,
  NULLIF(REPLACE(TRIM(mag.OriginalTitle), chr(0x00), ""), "") as mag_title,
  NULLIF(REPLACE(REPLACE(TRIM(crossref_title), "[NO TITLE AVAILABLE]", ""), chr(0x00), ""), "") AS crossref_title,
  NULLIF(REPLACE(TRIM(mag.abstract), chr(0x00), ""), "") as mag_abstract,
  NULLIF(REPLACE(TRIM(crossref.abstract), chr(0x00), ""), "") as crossref_abstract,
FROM
  `academic-observatory.observatory.doi20220528`,
  UNNEST(crossref.title) AS crossref_title