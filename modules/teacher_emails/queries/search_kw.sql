select distinct teachers.id
from teachers
inner join teach on teachers.id = teach.teacher
inner join courses on teach.course = courses.id
inner join course_abbr on courses.id = course_abbr.course
where teachers.name ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
or teachers.surname ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
or abbreviation ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
or courses.name ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')