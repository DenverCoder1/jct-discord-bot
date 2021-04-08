INSERT INTO emails (person, email)
VALUES (%(person_id)s, %(email)s)
ON CONFLICT (person, email) DO NOTHING