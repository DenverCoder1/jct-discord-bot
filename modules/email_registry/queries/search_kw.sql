select distinct people.id
from people
left join person_category on people.id = person_category.person
left join categories on person_category.category = categories.id
left join labels on categories.id = labels.category
where people.name ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
or people.surname ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
or label ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')
or categories.name ~* concat('(^|\s|\m)', f_regexp_escape(%(kw)s), '(\M|\s|$)')