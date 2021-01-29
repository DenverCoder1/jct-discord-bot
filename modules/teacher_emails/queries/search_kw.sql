select distinct teachers.id
from teachers
inner join teach on teachers.id = teach.teacher
inner join courses on teach.course = courses.id
inner join course_abbr on courses.id = course_abbr.course
where teachers.name ~* concat('\m', f_regexp_escape(%(kw)s), '\M')
or teachers.surname ~* concat('\m', f_regexp_escape(%(kw)s), '\M')
or abbreviation ~* concat('\m', f_regexp_escape(%(kw)s), '\M')
or courses.name ~* concat('\m', f_regexp_escape(%(kw)s), '\M')