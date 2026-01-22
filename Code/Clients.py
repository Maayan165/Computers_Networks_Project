import socket
import threading
import sys
import json

# Server configuration: Localhost IP and Port 10000
HOST = "127.0.0.1" 
PORT = 10000

# Threading Event: Used to synchronize the main input loop with the receiving thread.
# This flag is set when the server asks a specific question (like "enter yes") 
# requiring a specific response from the user.
waiting_system_answer = threading.Event()

# Helper function to safely parse JSON messages from the server.
# Returns an empty dictionary if parsing fails to prevent crashes.
def decode_json_message(msg):
    try:
        return json.loads(msg)
    except:
        return {}

# This function runs in a separate background thread.
# It continuously listens for incoming messages from the server while the user types.
def receive_messages(sock):
    while True:
        try:
            # Receive data from the server (blocking call) and decode it.
            msg = sock.recv(1024).decode('utf-8')

            # If msg is empty, the server closed the connection.
            if not msg:
                break

            # Parse the JSON message        
            obj = decode_json_message(msg)

            # Check if the server sent a "disconnected" signal.
            # If true, break the loop to stop receiving.
            if (obj.get("disconnected", False) == True):
                break

            # Print the message content to the screen.
            sys.stdout.write(obj["msg"])
            sys.stdout.flush()

            # Logic to handle specific server prompts:
            # If the server asks "enter yes", we signal the main thread
            # that the next input is a system answer, not a chat message.
            if "enter yes" in obj["msg"].lower():
                waiting_system_answer.set()

        except:
            break

# Create a TCP/IP socket
def start_client():
    client_socket = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    try:
        # Connect to the server defined in HOST and PORT
        client_socket.connect((HOST , PORT))
        
        # Step 1: Receive initial Welcome message
        msg = client_socket.recv(1024).decode('utf-8')
        obj = decode_json_message(msg)
        print(obj["msg"], end="") 

        # Step 2: User inputs their name and sends it to the server
        my_name = input("") # ה-input ריק כי השרת כבר הדפיס את הבקשה
        client_socket.sendall(my_name.encode('utf-8'))

       # Step 3: Wait for server confirmation that we are logged in
        msg = client_socket.recv(1024).decode('utf-8')
        obj = decode_json_message(msg)
        print(obj["msg"], end="") 
        # Call helper function to handle the logic of finding a friend to chat with
        friend_connection(client_socket)

        # Start the background thread to listen for incoming messages
        # daemon=True ensures this thread dies when the main program exits
        threading.Thread(target=receive_messages, args=(client_socket,), daemon=True).start()

        # Main loop: Handles user input
        while True:
            # Check if we are waiting for a specific system answer (triggered by the receive thread)
            if waiting_system_answer.is_set():
                answer = input("")
                client_socket.sendall(answer.encode('utf-8'))
                waiting_system_answer.clear()

            # Normal chat mode: Get input and send to server
            msg = input("")
            # If user types 'exit', break the loop to close connection
            if msg.lower() == 'exit':
                break
            client_socket.sendall(msg.encode('utf-8'))

    except ConnectionRefusedError:
        print("Connection failed.")
    except Exception as e:
        print(f"Error: {e}")
    # Close the socket cleanly when the loop ends
    finally:
        client_socket.close()

# Helper function to handle the specific "Who do you want to talk to?" logic
def friend_connection(client_socket):
        # Step 4: Receive prompt from server asking for friend's name
        msg = client_socket.recv(1024).decode('utf-8')
        obj = decode_json_message(msg)
        print(obj["msg"], end="") 
        # Send the requested friend's name
        friend = input("")
        client_socket.sendall(friend.encode('utf-8'))

        # Step 5: Receive success or error message regarding the friend connection
        status_msg = client_socket.recv(1024).decode('utf-8')
        jMsg = json.loads(status_msg)
        print(jMsg["msg"], end="")
if __name__ == "__main__":
    start_client()