SELECT id, grad_year, campus, role, calendar
FROM groups
WHERE role in %(roles)s
