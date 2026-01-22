import socket
import threading
import json
import tkinter as tk
from tkinter import scrolledtext, messagebox

# Color settings - Modern palette (WhatsApp Style)
COLOR_BG = "#E1C2F8"
COLOR_HEADER = "#460670"
COLOR_TEXT_AREA = "#FFFFFF"
COLOR_BUTTON = "#BA71F5"
COLOR_MY_MSG = "#3043D7"
COLOR_FRIEND_MSG = "#C433B3"
COLOR_SYSTEM = "#555555"

class Client_GUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Messenger Group 100")
        self.root.geometry("450x650")
        self.root.configure(bg=COLOR_BG)

        self.client_socket = None
        self.username = ""
        
        # Main container to hold different pages (Login/Chat)
        self.main_container = tk.Frame(self.root, bg=COLOR_BG)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.show_login_page()
        
    def get_auto_ip(self):
        """Function for finding the real IP of the computer"""
        try:
            local_hostname = socket.gethostname()
            # Retrieve a list of IP addresses
            ip_addresses = socket.gethostbyname_ex(local_hostname)[2]
            # Loopback address filtering
            filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]
            
            # If we found a real address, we will return the first one
            if filtered_ips:
                return filtered_ips[0]
        except:
            pass
        
        # If we didn't find it or there was an error, we will return the default
        return "127.0.0.1"

    def show_login_page(self):
        """Creates the login screen"""
        self.login_frame = tk.Frame(self.main_container, bg=COLOR_BG)
        self.login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # Central white card
        card = tk.Frame(self.login_frame, bg="white", padx=30, pady=30, highlightthickness=1, highlightbackground="#CCCCCC")
        card.pack()

        tk.Label(card, text="Welcome", font=("Segoe UI", 20, "bold"), bg="white", fg=COLOR_HEADER).pack(pady=(0, 20))

        # Input fields
        self.entry_ip = self.create_input(card, "SERVER IPV4:", self.get_auto_ip())
        self.entry_port = self.create_input(card, "SERVER PORT:", "10000")
        self.entry_user = self.create_input(card, "USER NAME:", "Student")

        # Action buttons
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(pady=20, fill=tk.X)

        tk.Button(btn_frame, text="CONNECT", bg=COLOR_BUTTON, fg="white", font=("Segoe UI", 10, "bold"), 
                  command=self.attempt_connection, bd=0, pady=10).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        tk.Button(btn_frame, text="EXIT", bg="#F674B5", fg="white", font=("Segoe UI", 10, "bold"), 
                  command=self.root.destroy, bd=0, pady=10).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

    def create_input(self, parent, label_text, default_val):
        tk.Label(parent, text=label_text, bg="white", font=("Segoe UI", 8, "bold"), fg=COLOR_SYSTEM).pack(anchor=tk.W)
        entry = tk.Entry(parent, font=("Segoe UI", 12), bd=0, bg="#F1F2F6", highlightthickness=1, highlightbackground="#DFE1E6")
        entry.pack(pady=(0, 15), ipady=8, fill=tk.X)
        entry.insert(0, default_val)
        return entry

    def attempt_connection(self):
        """Attempts to connect to the server with the provided credentials"""
        ip = self.entry_ip.get()
        port = int(self.entry_port.get())
        self.username = self.entry_user.get().strip().lower()

        if not self.username:
            messagebox.showwarning("Warning", "Please enter a username!")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            
            # Transition to the chat screen
            self.login_frame.destroy()
            self.show_chat_page()
            
            # Start the background thread to listen for messages
            threading.Thread(target=self.receive_messages, daemon=True).start()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def show_chat_page(self):
        """Creates the chat interface"""
        # Header
        self.header = tk.Label(self.main_container, text=f"💬 Chatting as: {self.username}", 
                              bg=COLOR_HEADER, fg="white", font=("Segoe UI", 14, "bold"), pady=15)
        self.header.pack(fill=tk.X)

        # Message display area
        self.chat_display = scrolledtext.ScrolledText(self.main_container, state='disabled', 
                                                     font=("Segoe UI", 11), bg=COLOR_TEXT_AREA,
                                                     padx=10, pady=10, bd=0)
        self.chat_display.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)
        
        # Tags for styling messages (Me/Friend/System)
        self.chat_display.tag_config("system", foreground=COLOR_SYSTEM, font=("Segoe UI", 10, "italic"))
        self.chat_display.tag_config("user", foreground=COLOR_MY_MSG, font=("Segoe UI", 11, "bold"))
        self.chat_display.tag_config("friend", foreground=COLOR_FRIEND_MSG, font=("Segoe UI", 11, "bold"))

        # Input frame for typing messages
        bottom_frame = tk.Frame(self.main_container, bg=COLOR_BG)
        bottom_frame.pack(fill=tk.X, padx=15, pady=(0, 20))

        self.entry_field = tk.Entry(bottom_frame, font=("Segoe UI", 12), bd=0, highlightthickness=1, highlightbackground="#CCCCCC")
        self.entry_field.bind("<Return>", lambda event: self.send_message())
        self.entry_field.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=8, padx=(0, 10))

        tk.Button(bottom_frame, text="Send", command=self.send_message, bg=COLOR_BUTTON, fg="white", 
                  font=("Segoe UI", 10, "bold"), bd=0, padx=20).pack(side=tk.RIGHT)

    def receive_messages(self):
        while True:
            try:
                raw_msg = self.client_socket.recv(4096).decode('utf-8')
                if not raw_msg: break
                
                # Server might send multiple JSON objects; parse the response
                obj = json.loads(raw_msg)
                content = obj.get("msg", "")
                sender = obj.get("from", "")

                # Auto-response to server prompts (e.g., identity verification)
                if "enter your name" in content.lower():
                    self.client_socket.sendall(self.username.encode('utf-8'))
                else:
                    self.display_message(sender, content)
            except:
                break

    def display_message(self, sender, msg):
        self.chat_display.config(state='normal')
        if not sender:
            # System message
            self.chat_display.insert(tk.END, f"📢 {msg}\n", "system")
        elif sender == self.username:
            # My message
            self.chat_display.insert(tk.END, f"✔ Me: {msg}\n", "user")
        else:
            # Friend's message
            self.chat_display.insert(tk.END, f"👤 {sender}: {msg}\n", "friend")
        self.chat_display.config(state='disabled')
        self.chat_display.yview(tk.END)

    def send_message(self):
        message = self.entry_field.get()
        if message.strip().lower() == 'exit':
            if self.client_socket:
                self.client_socket.close() # Closing the connection
            self.root.destroy() # Closing the window
            return
        if message:
            try:
                self.client_socket.sendall(message.encode('utf-8'))
                # Display message locally if the server does not echo back
                self.display_message(self.username, message)
                self.entry_field.delete(0, tk.END)
            except:
                self.display_message("", "⚠️ Error sending message")

if __name__ == "__main__":
    root = tk.Tk()
    app = Client_GUI(root)
    root.mainloop()