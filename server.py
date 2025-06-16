
import threading
import socket

host = "127.0.0.1" #localhost
port = 55556 #anything above 1024

server= socket.socket(socket.AF_INET,socket.SOCK_STREAM) #internet ipv4 and tcp

server.bind((host, port)) #bind server to host and ip address
server.listen() #server listens for new incoming connections

clients =[]
nicknames =[] #client's nickname

#broadcast, sends msg to all clients that are currently connected to server
def broadcast(message):
    for client in clients:
        client.send(message)

#handle clients's connections. send msgs and send back msg to other clients in broadcast
def handle(client):
    while True:
        try:
            msg = message = client.recv(1024)
            if msg.decode('ascii').startswith('KICK'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_kick = msg.decode('ascii')[5:]
                    kick_user(name_to_kick)
                else:
                    client.send('Command was refused as you are not admin!'.encode('ascii'))

            elif msg.decode('ascii').startswith('BAN'):
                if nicknames[clients.index(client)] == 'admin':
                    name_to_ban = msg.decode('ascii')[4:]
                    kick_user(name_to_ban)
                    with open('bans.txt', 'a') as f:
                        f.write(f'{name_to_ban}\n')
                    print(f'{name_to_ban} was banned!')
                else:
                    client.send('Command was refused as you are not admin!'.encode('ascii'))

            else:
                broadcast(message)

        except: #if there is error while receiving msg or broadcasting
            if client in clients:
                index= clients.index(client) #need client's index in order to remove them
                clients.remove(client)
                client.close()
                nickname = nicknames[index]
                broadcast('{} left!'.format(nickname).encode('ascii'))
                #tell everyone that this client has left
                nicknames.remove(nickname)
                break

#combines all the functions

def receive():
    while True: #accept clients all the time
        # Accept Connection
        client, address = server.accept()
        print("Connected with {}".format(str(address)))
        # if client connects, print on server console

        # Request And Store Nickname
        client.send('NICK'.encode('ascii')) #ask client for nickname

        nickname = client.recv(1024).decode('ascii') #the msg recieved is the nickname

        with open('bans.txt','r') as f:
            bans = f.readlines()  #every ban was in a separate line due to /n

        if nickname+'\n' in bans:
            client.send('BAN'.encode('ascii'))
            client.close()
            continue

        if nickname.lower() == 'admin':
            client.send('PASS'.encode('ascii'))
            password = client.recv(1024).decode('ascii')

            if password != "adminpass":
                client.send('REFUSE'.encode('ascii'))
                client.close()
                # not break as there is only one while loop
                continue

        nicknames.append(nickname) #we save the values in the list
        clients.append(client)

        # Print And Broadcast Nickname
        print("Nickname is of the client is {}".format(nickname))
        broadcast("{} joined!".format(nickname).encode('ascii')) #tell all the clients that this new client joined
        client.send('Connected to the server!'.encode('ascii'))  #tell the client that they are connected so they can start chatting

        # Start Handling Thread For Client
        thread = threading.Thread(target=handle, args=(client,)) #run one thread for each client
        thread.start()

def kick_user(name):
    if name in nicknames:
        name_index = nicknames.index(name)
        client_to_kick = clients[name_index]
        clients.remove(client_to_kick)
        client_to_kick.send('You were removed by an admin!'.encode('ascii'))
        client_to_kick.close()
        nicknames.remove(name)
        broadcast(f'{name} was removed by an admin!'.encode('ascii'))

print("Server is listening...")
receive()
