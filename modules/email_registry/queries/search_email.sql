SELECT DISTINCT people.id
FROM people
INNER JOIN emails ON people.id = emails.person
WHERE emails.email = %(param)s