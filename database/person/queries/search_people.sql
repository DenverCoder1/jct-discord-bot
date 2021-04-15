SELECT *
FROM (
		SELECT people.id,
			concat(people.name, ' ', people.surname) AS name,
			string_agg(emails.email, ', ') AS emails,
			string_agg(categories.name, ', ') AS categories,
			GREATEST(
				similarity(people.name, %(name)s),
				similarity(people.name, %(name)s)
			) AS similarity
		FROM people
			LEFT JOIN person_category ON people.id = person_category.person
			LEFT JOIN categories ON person_category.category = categories.id
			LEFT JOIN emails ON people.id = emails.person
		GROUP BY people.id
		ORDER BY similarity DESC
	) as subquery
WHERE subquery.similarity >= 0.3