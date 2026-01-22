# Computers_Networks_Project
TCP/IP Chat application with GUI and Wireshark analysis


## Overview
This project is a real-time messaging application based on the **Client-Server model** using the **TCP transport protocol**. It demonstrates core networking concepts such as encapsulation, multi-threading, and structured application-layer protocols using JSON.

## Figure 1: Application Login:
![alt text](/Data/AppLogin_image.png)

## Figure 2: Main Chat Interface and Real-time Messaging:
![alt text](/Data/MainChat_image.png)

## Technical Features
**Multi-threaded Server:** Efficiently manages multiple concurrent client connections without blocking.
**Application Protocol (JSON):** All messages are encapsulated as JSON objects, ensuring standardized communication between client and server.
**Modern GUI:** A user-friendly interface built with Tkinter, featuring a dedicated login screen for server parameters.
**Robust Error Handling:** Detects and handles abrupt disconnections (TCP RST) and keeps the client list synchronized.


## Project Structure
📁 **Code/**: Contains the core logic for `Server.py`, `Clients.py` and `clients_gui.py`.
📁 **Analysis/**: Includes the `Notebook.ipynb` and `.pcapng` files for packet capture and encapsulation analysis.
📁 **Data/**: Contains the `group100_http_input.csv` used for testing initial data flow.
📁 **Docs/**: Final project report. 
You can download the full final report here:
[Download Final Report](./Docs/דוח%20מסכם%20-%20פרויקט%20גמר%20ברשתות%20תקשורת%20מחשבים.pdf)

## How to Run
1. **Start the Server:** Execute `python Code/Server.py`. The server listens on `0.0.0.0:10000`.
2. **Launch Clients:** Run `python Code/Clients.py` for each user. Enter the Server IP and Port `10000` in the GUI login screen.
3. **Communication:** Follow the prompts to select a friend and start chatting.

## Chat Commands
Once connected, you can use the following special commands:
* **`list`**: Type this to view a real-time list of all currently online users.
* **`exit`**: Type this to disconnect from the server.

## Analysis & Packet Capture
As part of the project, we conducted a deep-dive analysis using Wireshark to verify:
**TCP 3-Way Handshake:** Establishing reliable connections.
**Data Segments:** Validating PSH and ACK flags during message exchange.
**Connection Resets:** Analyzing RST packets during unexpected terminations.