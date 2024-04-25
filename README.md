#Websocket testing server

Gives a simple web ui and ngrok interface for a websocket server.

You will need a configured ngrok account.

## To run

1. `python3.11 -m venv venv`
1. `source venv/bin/activate`
1. `python run.py`

## To use
1. Connect a WS client to whatever ngrok endpoint the CLI outputs
1. Open http://localhost:8080 in a web browser
1. Send messages from the server to the client.