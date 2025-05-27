import asyncio
import websockets
import json

async def chat():
    uri = 'ws://localhost:8100/airesponse'
    async with websockets.connect(uri) as websocket:
        while True:
            query = input('Tú: ')
            if query.lower() in ['salir', 'exit']:
                break
                
            # Send the query directly in JSON format
            await websocket.send(json.dumps({
                "type": "message",
                "content": query
            }))
            
            # Get the response
            response = await websocket.recv()
            try:
                result = json.loads(response)
                if 'data' in result:
                    # Handle the response data
                    data = result['data']
                    if isinstance(data, str):
                        try:
                            data = json.loads(data)
                        except json.JSONDecodeError:
                            data = {'answer': data}
                    
                    if isinstance(data, dict) and 'answer' in data:
                        print('\nDr. Simi:', data['answer'].strip())
                    else:
                        print('\nDr. Simi:', str(data).strip())
                elif 'error' in result:
                    print('\nError:', result['error'])
                else:
                    print('\nResponse:', result)
            except json.JSONDecodeError:
                print('\nResponse:', response)
            print()

if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\nChat terminated by user")
    except Exception as e:
        print(f"\nError: {str(e)}") 