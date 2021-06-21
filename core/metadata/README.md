# Metadata

[CRUD](https://en.wikipedia.org/wiki/Create,_read,_update_and_delete) endpoint for metadata

## Examples

### Reading metadata

Requesting metadata identified by an object ID.

HTTP GET request example

`$ curl https://${endpoint_url}/metadata?id=812d5c483acb33ce049c6146dd4bead2`

### Updating metadata

Updating metadata identified by an object ID and data to be updated.

You can add new metadata attributes or update existing attributes.

HTTP PUT request example

```
$ curl -X PUT https://${endpoint_url}/metadata?id=812d5c483acb33ce049c6146dd4bead2 \
-d '{ "headline": "Lamb on hills in Abergavenny, Wales" }' \
-H "Content-Type: application/json"
```

When request is successful, a response is returned with the content of the request payload (data) and time of the update in EPOCH (update_epoch) and datetime (update_datetime) formats.

Example response
```
{
  "headline": "Lamb on hills in Abergavenny, Wales",
  "update_epoch": "1624269655410",
  "update_datetime": "21/Jun/2021:10:00:55 +0000"
}
```

# Credits & ThankU's
* [DILLINGER](https://dillinger.io/) markdown editor used to create this very README