import asyncio
import websockets
from aiohttp import web
from pyngrok import ngrok

# Store active WebSocket connections in a set
connected = set()

# WebSocket server handler
async def websocket_handler(websocket, path):
    # Add the WebSocket connection to the set of connections
    connected.add(websocket)
    try:
        async for message in websocket:
            print(f"Received message: {message}")
            await websocket.send(f"Echo: {message}")
    except websockets.exceptions.ConnectionClosed:
        pass
    finally:
        # Remove connection from set when closed
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
    ws_server = await websockets.serve(websocket_handler, "localhost", 8765)
    # print("WebSocket server started at ws://localhost:8765")
    
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
