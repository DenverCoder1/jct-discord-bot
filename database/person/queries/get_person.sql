SELECT people.id,
	concat(people.name, ' ', people.surname) AS name,
	string_agg(emails.email, ', ') AS emails,
	string_agg(categories.name, ', ') AS categories
FROM people
LEFT JOIN person_category ON people.id = person_category.person
LEFT JOIN categories ON person_category.category = categories.id
LEFT JOIN emails ON people.id = emails.person
WHERE people.id = %(person_id)s
GROUP BY people.id