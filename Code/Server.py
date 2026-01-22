import socket
import threading
import json

# Server configuration
HOST = "0.0.0.0"   # Listen on all available network interfaces
PORT = 10000      # Port number for incoming connections

clients = {}  # Dictionary to map usernames to their socket connections

def create_JsonMsg(sender, to, msg, extraObj = {}): #Creates a JSON-formatted string to be sent over the socket.
    res={
        "from": sender if sender != None else "",
        "to": to if to != None else "", 
        "msg": msg
        }
      # Merge base message with any extra metadata
    merged = {**res, **extraObj}
    toSend = json.dumps(merged)   
    return toSend

    

def connect_friend(conn,name):
 while True:
        try:
           # Ask the client to enter the friend's name
            msg = "enter your friend's name:"
            res = create_JsonMsg(None, None, msg)
            conn.sendall(res.encode('utf-8'))

            friend_name = conn.recv(1024).decode("utf-8").strip().lower()
            print(f"{name} wants to talk to {friend_name}")
        
            # Check if requested friend is connected
            if friend_name in clients:
                msg = f"Connection successful! You can now chat with {friend_name}.\n"
                res=create_JsonMsg(None, None, msg)
                conn.sendall(res.encode('utf-8'))
                # conn.sendall(msg.encode('utf-8'))
                return friend_name
           
            else:
                 # Friend not found – allow retry or disconnect 
                msg = f"Error: User '{friend_name}' is not connected. You cannot send messages.\nif you want to chat with diffrent friend enter yes:"
                res = create_JsonMsg(None, None, msg)
                conn.sendall(res.encode('utf-8'))
                answer = conn.recv(1024).decode("utf-8").strip().lower()

                if answer != 'yes':
                      # Client chose to disconnect
                    print(f"{name} chose to disconnect.")
                    return # This will jump to 'finally' block in handle_client and close the connection

                # If answered 'yes', the loop restarts and waits for a new name
        except Exception as e:
        #except Exception as e:
            # Any unexpected socket or decoding error
            print(f"error occured {e}")
            return None

def chat_friend(conn,friend_name,name):
    while True:
        data = conn.recv(1024)
        if not data:
            # Client disconnected
            break
    

        data_d = data.decode("utf-8").strip()

        # Special command: list all connected users
        if data_d.lower() == "list":
            users = ", ".join(sorted(clients.keys()))
            msg = f"System: Connected users: {users}\n"
            res = create_JsonMsg(None, None, msg)
            conn.sendall(res.encode('utf-8'))
            continue

       # Send message only if the friend is currently in the clients list
        if friend_name in clients:
            friend_socket = clients[friend_name]
            msg_to_send = f"\n{name}: {data_d}\n"
            res = create_JsonMsg(name, friend_name, msg_to_send)
            friend_socket.sendall(res.encode('utf-8'))
        else:
           # If trying to send a message when the friend is not connected
            msg = "System: Message not sent. Friend is not connected.\n if you want to chat with diffrent friend enter yes: "
            res = create_JsonMsg(None, None, msg)
            conn.sendall(res.encode('utf-8'))
            answer = conn.recv(1024).decode("utf-8").strip().lower()

            if answer == 'yes':
                friend_name = connect_friend(conn, name)
                if friend_name is None:
                    return
            else:
                msg = f"{name} is disconnected"
                res = create_JsonMsg(None, None, msg, {"disconnected": True})
                conn.sendall(res.encode('utf-8'))
                clients[name].close()
                del clients[name] 
                break

def handle_client(conn, addr): # Handles a single client connection.
    print(f"Client connected from: {addr}")
    name = None 
    try: # Ask client for username
        msg = "Welcome!\n Please enter your name:"
        res = create_JsonMsg(None, None, msg)
        conn.sendall(res.encode('utf-8'))
        
        name = conn.recv(1024).decode("utf-8").strip().lower()
        clients[name] = conn
        print(f"Added {name} to client list")
        msg = f"Hello {name}, you are now connected!\n"
        res = create_JsonMsg(None, None, msg)
        conn.sendall(res.encode('utf-8'))

        friend_name = connect_friend(conn,name)
        if friend_name is None:
            return
        # Start chat loop
        chat_friend(conn,friend_name,name)

    except ConnectionResetError:  # Client disconnected unexpectedly
        print(f"Client disconnected abruptly: {addr}")
        
    finally: # Cleanup client data
        if name and name in clients:
            del clients[name]
            print(f"Removed {name} from client list")
        
        conn.close()
        print(f"Socket closed for {addr}")

def start_server(): # Initializes and starts the TCP server.
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server.bind((HOST, PORT))
        server.listen()
        print(f"Server is listening on {HOST}:{PORT}")
        
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()

    except Exception as e:
        print(f"Server failed to start: {e}")

    finally:
        server.close()

if __name__ == "__main__":
    start_server()