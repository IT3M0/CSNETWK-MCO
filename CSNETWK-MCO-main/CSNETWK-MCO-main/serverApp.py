'''
    Server Application
    This is the server application that would function as the server
    for the File Exchange System. This application will be able to
    accept multiple clients and will be able to handle multiple
    requests from the clients.

    CSNETWK S16 Group 
    Name:
        - ABENOJA, Amelia Joyce L.
        - HALLAR, Francine Marie F.
        - SANG, Nathan Immanuel C.
'''

# Imports
import socket                       # For socket programming
import sys                          # For command-line arguments
import threading                    # For multi-threading
import os                           # For file-related operations
import time
from datetime import datetime


# Global Variables
BUFFER_SIZE         = 1024      
console_width       = 80
server_directory    = "Server Directory"
clients_socket_list = []
clients_alias_list  = []


# Function Definitions
def displayWelcomeMessage():
    welcome_message = "Welcome to the File Exchange System!"
    print("=" * console_width)
    print(welcome_message.center(console_width))
    print("=" * console_width)


def getCurrentDateTime():
    current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return current_date_time




def getClientAlias(client_socket):
    try:
        index = clients_socket_list.index(client_socket)
        client_alias = clients_alias_list[index]

        return client_alias
    except:
        return False
    


def receiveFile(client_socket, file, save_dir):
    if save_dir:
        client_socket.send("Storing File to Server".encode())
        
        file_data = client_socket.recv(os.path.getsize(file) + 1)

        dir_path = os.path.join(save_dir, file)
        
        current_file = open(dir_path, "wb")

        print(dir_path)
        
        if current_file:
            current_file.write(file_data)
            current_file.close()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            print(f"Server: File {file} stored successfully.")

            file_message = f"{getClientAlias(client_socket)}<{timestamp}>: Uploaded {file}"
            client_socket.send(file_message.encode())
            print(file_message)
            
        else:
            print("Error")
                
    else:
        err_message = f"{save_dir} does not exist."
        print(f"Server: {err_message}")
        client_socket.send(err_message)


def fetchFile(client_socket, file):
    if getClientAlias(client_socket):
        if (os.path.exists('Server Directory/' + file )):
            client_socket.send("Sending File to Client".encode())
            user_dir = getClientAlias(client_socket)
            time.sleep(0.01)
            
            client_socket.send(user_dir.encode())
            time.sleep(0.01)
            
            client_socket.send(file.encode())
            with open("Server Directory/" + file, 'rb') as current_file:
                file_data = current_file.read()
                print(file_data)
                time.sleep(0.05)
                client_socket.sendall(file_data)
        else:
            client_socket.send("Error: File not found in the server.".encode())
    else:
        client_socket.send("Error: User not registered!".encode())
      
def toString(files):

    dir_list = ''

    for x in files:
        dir_list += x + '\n'
    
    return dir_list
    


def startServer(IP, PORT):
    global server_socket  # Declare server_socket as a global variable
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((IP, PORT))
    server_socket.listen(5)

    print(f"Server: Listening on {IP}:{PORT}")

    while True:
        # Accept a new connection
        client_socket, client_address = server_socket.accept()

        # If the input is valid, send a success message to the client
        success_message = "Connection to the File Exchange Server is successful!"
        client_socket.send(success_message.encode())

        # Print the connection details
        print(f"Server: Connection from {client_address} has been established!")

        # Start the client thread
        client_thread = threading.Thread(target=processClientCommands, args=(client_socket, client_address))

        # Start the thread
        client_thread.start()


def processClientCommands(client_socket, client_address):
    try:
        while True:
            command = client_socket.recv(BUFFER_SIZE).decode()

            # Leave the server
            if command == '/leave':
                current_client = getClientAlias(client_socket)

                if current_client is False:
                    server_response = "Connection closed. Thank you!"
                    client_socket.send(server_response.encode())
                    client_socket.close()
                    print(f"Server: Client {client_address} has disconnected.")
                    print(f"Current clients: {clients_alias_list}: {clients_socket_list}")
                else:
                    print(f"Server: Command {command} received from {current_client}")

                    # Remove the client from the list of clients
                    indexSocket = clients_socket_list.index(client_socket)
                    clients_socket_list.pop(indexSocket)

                    indexAlias = clients_alias_list.index(current_client)
                    clients_alias_list.pop(indexAlias)

                    # Check the list of sockets
                    print(f"Current clients: {clients_alias_list}: {clients_socket_list}")

                    server_response = "Connection closed. Thank you!"
                    client_socket.send(server_response.encode())
                    client_socket.close()

                    print(f"Server: Client {current_client} has disconnected.")
                    print(f"Current clients: {clients_alias_list}: {clients_socket_list}")

                # Break the loop to exit the thread
                break

            # Register a unique alias (or handle) for the client
            if command == '/register':
                print(f"Server: Command {command} received from {client_address}")
                current_client = None

                alias = client_socket.recv(BUFFER_SIZE).decode()

                try:
                    # Check if the client is already registered
                    if alias in clients_alias_list:
                        server_response = "Error: Registration failed. Handle or alias already exists."
                        client_socket.send(server_response.encode())
                    else:
                        print(f"Server: Alias {alias} received from {client_address}")

                        # os.mkdir(alias)
                        clients_alias_list.append(alias)
                        clients_socket_list.append(client_socket)

                        # For debugging
                        print(f"Current clients: {clients_alias_list}: {clients_socket_list}")

                        server_response = f"Welcome {alias}!"
                        client_socket.send(server_response.encode())
                except Exception as e:
                    print(f"Server: Error: {str(e)}")
                    server_response = f"Error: {str(e)}"
                    client_socket.send(server_response.encode())

            
            # Store a file in the server
            if command == '/store':
                client = getClientAlias(client_socket)
                
                if client:
                    try:
                        filename = client_socket.recv(BUFFER_SIZE).decode()

                        # Create Server Directory if it does not exist
                        try:
                            os.mkdir(server_directory)
                        except:
                            pass

                        save_dir = server_directory
                        receiveFile(client_socket, filename, save_dir)


                    except:
                        client_socket.send("Error: Command parameters do not match or is not allowed.".encode())
                else:
                    client_socket.send("User not registered".encode())

            if command == '/dir':
                client = getClientAlias(client_socket)
                
                if client:
                    directory = "Server Directory"
                    isExist = os.path.exists(directory)
                    
                    if(isExist):
                        files = os.listdir(directory)
                        client_socket.send((directory + ": \n" + toString(files)).encode())
                else:
                    client_socket.send("User not registered".encode())

            if command == '/get':
                if getClientAlias(client_socket):
                    _, file = command.split()
                    fetchFile(client_socket, file)
                
                else:
                    client_socket.send("User not registered".encode())
            
    except Exception as e:
        print(f"Server: Error: {str(e)}")




if __name__ == "__main__":
    try:
        # Check if at least two command-line arguments are provided
        if len(sys.argv) < 3:
            print("Error: Please provide an IP address and a port number.")
            sys.exit(1)

        # Get the IP address and port number from the command-line arguments
        IP = sys.argv[1]
        PORT = int(sys.argv[2])

        # Validate IP address
        try:
            socket.inet_aton(IP)
        except socket.error:
            print("Error: Invalid IP address.")
            sys.exit(1)

        # Validate port number
        if not 0 <= PORT <= 65535:
            print("Error: Port number should be between 0 and 65535.")
            sys.exit(1)

        # Display welcome message
        displayWelcomeMessage()
        startServer(IP, PORT)
    
    except socket.error as se:
        print(f"Server: Socket error: {se}")
    except ValueError as ve:
        print(f"Server: Invalid port number: {ve}")
    except Exception as e:
        print(f"Server: Error: {str(e)}")
