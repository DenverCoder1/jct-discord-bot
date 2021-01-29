select
	concat(teachers.name, ' ', teachers.surname) as name,
	string_agg(emails.email, ' '),
	string_agg(courses.name, ', ') as courses
from teachers
left join teach on teachers.id = teach.teacher
left join courses on teach.course = courses.id
inner join emails on teachers.id = emails.teacher
where teachers.id in %(ids)s
group by teachers.id