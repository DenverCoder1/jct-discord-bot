DELETE FROM person_category
WHERE
	person = %(person_id)s
	AND
    category = (SELECT id
	    FROM categories
		WHERE channel_id = %(channel_id)s)
