# P2P MultiUser Chatting

This project is an implementation of a Peer-to-Peer (P2P) MultiUser Chatting application using TCP and UDP protocols. The application allows multiple users to communicate with each other in real-time through chat rooms. The communication with the server (registry) is done using TCP, while communication within the chat rooms utilizes UDP for efficiency.

## Features

1. **P2P Architecture:** The application is built on a peer-to-peer architecture, where each peer acts as both a client and a server. This decentralized approach allows direct communication between peers without relying on a central server.

2. **TCP Communication:** When communicating with the server and during one-to-one interactions, TCP (Transmission Control Protocol) is used. TCP ensures reliable and ordered delivery of messages, making it suitable for important and critical communication.

3. **UDP Communication:** Within chat rooms, UDP (User Datagram Protocol) is utilized for utility purposes. UDP provides fast and connectionless communication, which is ideal for real-time messaging in a chat room setting.

4. **MongoDB Registry:** The application employs MongoDB as the registry database. The registry database stores information about registered users, such as their usernames and network details. MongoDB offers scalability and flexibility, ensuring efficient management of user information.

5. **Color-Coded Terminal Chat:** The chat interface is designed to run in the terminal and supports color-coded messages. This feature enhances the user experience by visually distinguishing messages and making the chat more engaging.

## Usage

To run the application, follow these steps:

1. Run `registry.py` to start the server (registry) component. The server handles user registration, manages user information, and facilitates initial connections between peers.

2. For each peer who wants to join the chat, run `peer.py`. The `peer.py` script initializes a peer instance, connects to the server, and allows the peer to interact with other users in the chat rooms.

3. The chat rooms are created dynamically as users join and interact. Users can send messages, view incoming messages, and participate in group conversations.

4. To exit the application, simply close the terminal window or press `Ctrl + C` to stop the execution of the scripts.

## Requirements

Make sure you have the following dependencies installed before running the application:

- Python 3.x
- MongoDB

## Configuration

Before running the application, ensure that you configure the following settings:

- MongoDB connection details: Update the MongoDB connection string in the `registry.py` script to match your MongoDB server address and authentication credentials.

## Disclaimer

This application is provided as-is and without any warranties. Use it at your own risk. The developers are not responsible for any damage or loss caused by the usage of this application.
