DELETE FROM emails
WHERE
	person = %(person_id)s
	AND
	email = %(email)s