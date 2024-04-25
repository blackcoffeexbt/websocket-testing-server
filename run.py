import asyncio
import websockets
from aiohttp import web
from pyngrok import ngrok

# Store active WebSocket connections in a set
connected = set()

async def handler(websocket, path):
    # Add the new client to the set of connected clients
    connected.add(websocket)
    try:
        # Send a greeting message to the client
        await websocket.send("hello")
        # Keep the connection open
        async for message in websocket:
            print(f"Received message from client: {message}")
            # Echo back received messages (optional)
            await websocket.send(f"Echo: {message}")
    except websockets.ConnectionClosed:
        print("Connection with client closed")
    finally:
        # Remove client from the set when connection is closed
        connected.remove(websocket)

# HTTP server handler to send messages from the web UI
async def handle_send(request):
    data = await request.post()
    message = data['message']
    # Broadcast the message to all connected WebSocket clients
    for ws in connected:
        await ws.send(message)
    # return "message sent and html from index.html"
    return web.FileResponse('index.html')

# Set up the aiohttp web app
app = web.Application()
app.add_routes([web.post('/send', handle_send)])

async def handle_index(request):
    return web.FileResponse('index.html')

app.add_routes([web.get('/', handle_index)])


async def main():
    
    # Start the aiohttp web server
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)
    await site.start()
    print("WebUI started at:\nhttp://localhost:8080")

    # Start WebSocket server
    ws_server = await websockets.serve(handler, "0.0.0.0", 8765)
    print("WebSocket server started at:\nws://localhost:8765")
    
    # Start ngrok tunnel for the WS app
    http_tunnel = ngrok.connect(8765, bind_tls=True)
    public_url = http_tunnel.public_url.replace("https", "wss")
    print()
    print(f"ngrok tunnel for WS at {public_url}")
    print()
    print("Connect with websocat using:")
    print(f"websocat {public_url}")
    print()
    
    # Keep the servers running
    await asyncio.Future()  # Run forever

asyncio.run(main())
