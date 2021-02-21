SELECT classes.grad_year, campuses.name
FROM classes
INNER JOIN campuses on classes.campus = campuses.id
WHERE role in %(roles)s