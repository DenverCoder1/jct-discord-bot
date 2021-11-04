INSERT INTO person_category (person, category)
VALUES ($1,
    (SELECT id
	    FROM categories
		WHERE channel = $2))
