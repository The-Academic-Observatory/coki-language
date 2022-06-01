select name, language, count, 100 * (count / total) as percent, avg_score, std_score
from (
  SELECT coalesce(MAX(iso.name),'Unknown: no title or abstract') as name, coalesce(language,'null') as language, COUNT(coalesce(language,'null')) as count, AVG(score) as avg_score, STDDEV(score) as std_score, sum(count(*)) OVER() AS total
  FROM `academic-observatory.mockup.doi_language` as doi
  LEFT JOIN `academic-observatory.mockup.iso_language` as iso
  ON doi.language = iso.code
  GROUP BY language
  ORDER BY count DESC
)
