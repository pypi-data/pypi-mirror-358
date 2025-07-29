# README

This is a library to interact with [Denodo RESTful Web Services](https://community.denodo.com/docs/html/browse/8.0/en/vdp/administration/restful_architecture/restful_web_service/restful_web_service)

```python
client = Client(host, username, password)
view = client.database(dbname).view(viewname)
elements: list[dict] = view.get(
    select=[
        "name",
        "age",
    ],
    filter="job ='developer'",
)
```
