#!/usr/bin/env python3
from socket import AF_INET, socket, SOCK_STREAM
from threading import Thread
import tkinter as tkt


#function to broadcast messages to all clients, excluding some if needed
def broadcast(msg, prefix='', exclusions=[]):
    complete_msg = prefix + ": " + msg
    print_on_console(complete_msg)
    for client_socket in clients:
        if client_socket not in exclusions:
            client_socket.send(bytes(complete_msg, "utf8"))


#function to close a client connection and inform all other clients
def close_client(client_socket):
    broadcast(f"{clients[client_socket]} has left the chat.", exclusions=[client_socket])
    client_socket.close()
    del clients[client_socket]
    del addresses[client_socket]


#function to handle a client connection, client threads cicles here
def handle_client(client_socket):
    client_name = client_socket.recv(buffersize).decode("utf8")
    clients[client_socket] = client_name

    welcome_message = "Welcome " +  client_name + r"! If you want to leave the chat, type  {quit}  to exit."
    client_socket.send(bytes(welcome_message, "utf8"))

    broadcast_message = f"{client_name} has joined the chat!"
    broadcast(broadcast_message, exclusions=[client_socket])

    while True:
        try:
            msg = client_socket.recv(buffersize)
            if msg != bytes("{quit}", "utf8"):
                broadcast(msg.decode("utf8"), prefix=client_name)
            else:
                close_client(client_socket)
                break
        except ConnectionResetError: #in case the client closed the connection
            close_client(client_socket)
            break
        except ConnectionAbortedError: #in case the server was closed
            break   
 

#function to handle the server main thread, the one who accepts new connections           
def main_loop():
    while True:
        try:
            client_socket, client_ip = server_socket.accept()
            print_on_console(f"Connection from {client_ip}")
            addresses[client_socket] = client_ip
            Thread(target=handle_client, args=(client_socket,)).start()
        except OSError as e:
            break

#function to close the server and all client connections
def on_closing():
    for client_socket in clients:
        client_socket.send(bytes(r"{quit}", "utf8"))
        client_socket.close()
    server_socket.close()
    window.quit()


#function to print messages on the GUI console    
def print_on_console(msg):
    msg_list.insert(tkt.END, msg)
    msg_list.yview(tkt.END)
    print(msg) #prints the message on the console as a backup in case GUI doesn't work


clients = {}
addresses = {}

server_ip = "127.0.0.1"
server_port = 25565
server_address = (server_ip, server_port)
buffersize = 1024

server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(server_address)

msg_list = None

if __name__ == "__main__":
    server_socket.listen(5)
    server_thread = Thread(target=main_loop)
    server_thread.start()
    
    #tkt window
    window = tkt.Tk()
    window.title("Server console")
    window.protocol("WM_DELETE_WINDOW", on_closing)
    frame = tkt.Frame(window)
    scrollbar = tkt.Scrollbar(frame)
    scrollbar.pack(side=tkt.RIGHT, fill=tkt.Y)
    msg_list = tkt.Listbox(frame, height=15, width=80, yscrollcommand=scrollbar.set)
    msg_list.pack(side=tkt.LEFT, fill=tkt.BOTH)
    frame.pack()
    print_on_console("Server is open at " + server_ip + ":" + str(server_port) + " waiting for connections...")
    tkt.mainloop()
    server_thread.join()
    server_socket.close()
    