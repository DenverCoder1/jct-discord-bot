SELECT id, grad_year, campus, role, calendar
FROM groups
WHERE id = %(group_id)s