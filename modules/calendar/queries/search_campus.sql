SELECT name
FROM campuses
WHERE %(text)s ~* name
