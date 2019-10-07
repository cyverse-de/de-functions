# check-resource-access

Looks up the permissions that a subject has for a resource. By default, the subject type is 'user' and the resource type is 'analysis'.

# Requests

Accepts any HTTP method. Requires the following JSON structure in the body of the request:

```
{
    "subject" : "",
    "resource" : ""
}
```

Subject is usually a username, while the resource is usually an analysis UUID (a.k.a. job ID in the database.)