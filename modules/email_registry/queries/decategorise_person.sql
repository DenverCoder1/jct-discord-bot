DELETE FROM person_category
WHERE
	person = $1
	AND
    category = (SELECT id
	    FROM categories
		WHERE channel = $2)
