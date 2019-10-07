# get-user-info

Returns information about a user contained in Grouper. 

## Requests

Accepts HTTP requests (method doesn't matter) with a request body that looks like the following:

```json
{
    "username" : ""
}
```

## Responses

Returns JSON in the response body that looks like the following:

```json
{
    "id" : "<username>",
    "name" : "<full name>",
    "first_name" : "<first name>",
    "last_name" : "<last name>",
    "email" : "<email address>",
    "institution" : "<institution>",
    "source_id" : "<probably 'ldap'>"
}
```