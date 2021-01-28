select distinct teachers.id
from teachers
inner join teach on teachers.id = teach.teacher
inner join courses on teach.course = courses.channel_id
inner join course_abbr on courses.channel_id = course_abbr.course
where teachers.name ~* concat('\m', %(kw), '\m')
or teachers.surname ~* concat('\m', %(kw), '\m')
or abbreviation ~* concat('\m', %(kw), '\m')
or course.name ~* concat('\m', %(kw), '\m');