
import socket
import threading

# Choosing Nickname
nickname = input("Choose your nickname: ")
if nickname.lower()== 'admin':
    password = input("Enter the password for admin:")

stop_thread = False
# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55556))  #client connects to localhost. Here server will trigger it's except method

# Listening to Server and Sending Nickname
def receive():  #runs constantly to receive data from server
    while True:
        global stop_thread
        if stop_thread:
            break
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')

            if message == 'NICK':   #keyword for sending nickname
                client.send(nickname.encode('ascii'))
                next_message = client.recv(1024).decode('ascii')

                if next_message == 'PASS':
                    client.send(password.encode('ascii'))
                    if client.recv(1024).decode('ascii') =='REFUSE':
                        print("Connection was refused! Wrong Password.")
                        stop_thread = True

                elif next_message == 'BAN':
                    print('Connection was refused because of Ban!')
                    client.close()
                    stop_thread = True
            else:
                print(message)

        except:
            # Close Connection When Error
            print("An error occurred!")
            client.close()
            stop_thread = True
            break

def write():
    while True:
        if stop_thread:
            break
        message = '{}: {}'.format(nickname, input(''))  #defines a new msg, what user inputs
        if message[len(nickname)+2:].startswith('/'):
            if nickname.lower()== 'admin':
                if message[len(nickname)+2:].startswith('/kick'):
                    client.send(f'KICK {message[len(nickname)+8:]}'.encode('ascii'))
                elif message[len(nickname)+2:].startswith('/ban'):
                    client.send(f'BAN {message[len(nickname)+7:]}'.encode('ascii'))
            else:
                print('Commands can only be executed by the admin!')
        else:
            client.send(message.encode('ascii')) #after the message is sent

# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()

