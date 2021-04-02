SELECT DISTINCT people.id
FROM people
INNER JOIN person_category ON people.id = person_category.person
INNER JOIN categories ON person_category.category = categories.id
WHERE categories.channel = %(param)s