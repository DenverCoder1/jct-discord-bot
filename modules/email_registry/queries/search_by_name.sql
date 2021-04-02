SELECT DISTINCT people.id
FROM people
WHERE name ~* concat('(^|\s|\m)', f_regexp_escape(%(word)s), '(\M|\s|$)')
OR surname ~* concat('(^|\s|\m)', f_regexp_escape(%(word)s), '(\M|\s|$)')