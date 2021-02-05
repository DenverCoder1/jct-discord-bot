DELETE FROM person_category
WHERE
	person = %(person_id)s
	AND
    category = (SELECT id
	    FROM categories
		WHERE channel = %(channel_id)s)
