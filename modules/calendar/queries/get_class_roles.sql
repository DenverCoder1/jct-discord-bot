SELECT groups.grad_year, campuses.name
FROM groups
INNER JOIN campuses on groups.campus = campuses.id
WHERE role in %(roles)s