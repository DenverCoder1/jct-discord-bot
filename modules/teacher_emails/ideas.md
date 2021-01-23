# Interface

- ++getemail _query_
- ++setemail _email_, _name_, _subject list_
- ++removeemail _email_ (admin required)

# Table

Emails(email, name, subjects)

# Search algorithm

- split query on spaces
- search each word in CONCAT(name, " ", subjects)
- return list of results with maximal matches
