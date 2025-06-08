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
            
            # Get responses until we receive the final answer
            while True:
                response = await websocket.recv()
                try:
                    result = json.loads(response)
                    
                    # Handle thinking messages
                    if result.get('type') == 'thinking':
                        # Clear the current line and print thinking message
                        print('\r' + ' ' * 50 + '\r', end='', flush=True)  # Clear line
                        print('\rThinking:', result['data']['message'], end='', flush=True)
                        continue
                    
                    # Clear the thinking message line
                    print('\r' + ' ' * 50 + '\r', end='', flush=True)
                    
                    # Handle the final response
                    if result.get('type') == 'answer' and 'data' in result:
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
                        break
                    elif result.get('type') == 'error':
                        print('\nError:', result['data']['message'])
                        break
                    else:
                        print('\nResponse:', result)
                        break
                except json.JSONDecodeError:
                    print('\nResponse:', response)
                    break
            print()

if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\nChat terminated by user")
    except Exception as e:
        print(f"\nError: {str(e)}") 