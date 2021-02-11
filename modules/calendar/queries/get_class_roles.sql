SELECT grad_year, campus
FROM classes
WHERE role in %(roles)s
