insert into categories (name, channel)
values (%(course_name)s, %(channel_id)s)
RETURNING id