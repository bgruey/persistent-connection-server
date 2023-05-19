# Persistent Connection Server/Client Project

This is a persistent-connection server and client written in Python3. The use-case for the server is
many small requests made over the same connection, such as a collection of pipeline workers
connecting to a name normalizer model deployed on the server.

The server implements no security/login functionality and should not be exposed to the open internet.

## Message Protocol

All requests and responses will follow:
1. Dump message into bytes, get length
2. Send a single integer that is the length of the message
3. Send the message as bytes

When reading a request, read the size (4 bytes), then read the message.

### Message Type

Messages are defined as Python classes implementing a `name: str` member
as well as a `data: typing.Any` member. Data serialization is done via the
[jsonpickle](https://pypi.org/project/jsonpickle/) library. This allows for
human readability in serialized messages for debugging, and arbitrary 
structures within the `data` member.

Ideally the messages would move to something like Google's
[protocol buffers](https://protobuf.dev/), but the lack of support for
Javascript and C (at least officially) makes for a poor choice.

The performance tests comparing a JSON serialized dictionary compared to a
JSONPickle protocol message indicates JSONPickle is 3 times slower to dump
and 16 times slower to load.
```
            Dump         |   Load         | Serialized Size in Bytes
    JP:   (2.973, 0.127) | (7.886, 0.153) | 295203
    JSON: (0.974, 0.096) | (0.519, 0.027) | 295100
```

### Base Messages

The base client/server implements the following messages in request/response format:
* `open`: Used to open a connection to the server.
  * This must be the first message sent to the server.
* `ping`: Primarily used by the `BaseClient` in its ping thread routine to keep connections alive.
* `close`: Used to end a connection to the server from the client.
  * If the server times out a connection, it will send a `close` response.
* `shutdown`: Used to shut down the server.

## Examples

See the `example_protocol` library for examples of client, server worker, and
messages based of the base classes. The `main.py` files in `client/` and `server/`
give examples of running the client and server.