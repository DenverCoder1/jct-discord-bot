INSERT INTO person_category (person, category)
VALUES (%(person_id)s,
    (SELECT id
	    FROM categories
		WHERE channel = %(channel_id)s))
