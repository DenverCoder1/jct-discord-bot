SELECT calendar
FROM classes
INNER JOIN campuses ON classes.campus = campuses.id
WHERE
  classes.grad_year = %(grad_year)s
  AND
  campuses.name = %(campus)s