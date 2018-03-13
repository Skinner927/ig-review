

## Development

run `python wsgi.py` to start the server in debug mode.



I suggest you run the required rabbitmq server in a container.

`docker pull rabbitmq`

`docker run -d --hostname ig-rabbit --name ig-rabbit -p 5672:5672 -p 8080:15672 rabbitmq:3-management`
