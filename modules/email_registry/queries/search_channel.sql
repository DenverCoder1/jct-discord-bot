select distinct people.id
from people
inner join person_category on people.id = person_category.person
inner join categories on person_category.category = categories.id
where categories.channel_id = %(channel_id)s