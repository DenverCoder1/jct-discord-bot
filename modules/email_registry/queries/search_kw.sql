SELECT DISTINCT people.id
FROM people
LEFT JOIN person_category ON people.id = person_category.person
LEFT JOIN categories ON person_category.category = categories.id
LEFT JOIN labels ON categories.id = labels.category
WHERE people.name ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
				OR people.surname ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
				OR label ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
				OR categories.name ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')