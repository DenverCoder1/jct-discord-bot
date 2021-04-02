SELECT classes.id, concat(campuses.name, ' ', grad_year), calendar
  FROM classes INNER JOIN campuses
  ON classes.campus = campuses.id
