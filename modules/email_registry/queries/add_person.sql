INSERT INTO people (name, surname, member_id)
VALUES (%(name)s, %(surname)s, %(member_id)s)
RETURNING id
