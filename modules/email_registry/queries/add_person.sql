INSERT INTO people (name, surname)
VALUES (%(name)s, %(surname)s)
RETURNING id
