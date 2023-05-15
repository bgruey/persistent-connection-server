# Persistent Connection Server/Client Project

Goal is to play with creating a single server that accepts many persistent
connections.

## Messages

All requests and responses will follow:
1. Dump message into bytes, get length
2. Send a single integer that is the length of the message
3. Send the message as bytes

When reading a request, read the size (4 bytes), then read the message.

Messages are expected to be in the simple format of
```json
{
  "name": "<value>-<req/res>",
  "data": {}
}
```
where the value of `nama` can be:
* ping
* close
* uuid
  * data will be a string
  * response data will be the given string, prepended with a uuid4.

The difference between request/response messages in `name` is the suffix: `-req` or `-res`.