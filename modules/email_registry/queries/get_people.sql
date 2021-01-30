select
	people.id,
	concat(people.name, ' ', people.surname) as name,
	string_agg(emails.email, ' '),
	string_agg(categories.name, ', ') as categories
from people
left join person_category on people.id = person_category.person
left join categories on person_category.category = categories.id
left join emails on people.id = emails.person
where people.id in %(ids)s
group by people.id