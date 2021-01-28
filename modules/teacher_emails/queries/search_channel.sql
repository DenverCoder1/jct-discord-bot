select distinct teachers.id
from teachers
inner join teach on teachers.id = teach.teacher
inner join courses on teach.course = courses.id
where courses.channel_id = %(channel_id)s