SELECT calendar
FROM groups
INNER JOIN campuses ON groups.campus = campuses.id
WHERE
  groups.grad_year = %(grad_year)s
  AND
  campuses.name = %(campus)s
