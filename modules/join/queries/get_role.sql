select role from classes
inner join campuses on classes.campus = campuses.id
where lower(campuses.name) = lower(%(campus)s)
and grad_year = %(grad_year)s