select role from classes
where lower(campus) = lower(%(campus)s)
and grad_year = %(grad_year)s