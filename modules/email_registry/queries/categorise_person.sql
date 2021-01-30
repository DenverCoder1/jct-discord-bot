INSERT INTO person_category (person, category)
VALUES (%(person_id)s,
    (SELECT id
	    FROM categories
		WHERE channel_id = %(channel_id)s))
