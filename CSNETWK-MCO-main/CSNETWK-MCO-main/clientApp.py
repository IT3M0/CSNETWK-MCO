"""
Client Application
This script serves as the client application for the File Exchange System. It provides
a user interface for interacting with the system, connecting to a server, and performing
various file-related operations.

CSNETWK S16 Group
- ABENOJA, Amelia Joyce L.
- HALLAR, Francine Marie F.
- SANG, Nathan Immanuel C.
"""

# Imports
import socket                       # For socket programming
import os                           # For file-related operations
import tkinter as tk                # For GUI

# Global Variables
BUFFER_SIZE     = 4096      # Size of the message buffer
is_connected    = False     # Connection status default to False (not connected)
server_address  = None      # Initialize server address
server_port     = None      # Initialize server port
console_width   = 80        # Console width for formatting purposes
client_socket   = None      # Initialize client socket

# Function Definitions
def displayWelcomeMessage():
    welcome_message = "Welcome to the File Exchange System!"
    print("=" * console_width)
    print(welcome_message.center(console_width))
    print("=" * console_width)

def displayCommands():
    all_commands = [
        "Commands for the File Exchange System: ",
        "- To connect to the server application             : /join <server_ip_add> <port>",
        "- To disconnect to the server application          : /leave",
        "- To register a unique handle or alias             : /register <handle>",
        "- To send file to server                           : /store <filename>",
        "- To request directory file list from a server     : /dir",
        "- To fetch a file from the a server                : /get <filename>",
        "- To request command help to output all"
        "  Input Syntax commands for references             : /?"
    ]

    return all_commands

def toServer(txtCommand, txtOutput):
    """
    Sends a command to the server

    Parameters:
    - command: Command to be sent to the server

    Returns:
    - None
    """
    global is_connected
    global server_address
    global server_port
    global client_socket

    # Get the command from the text widget
    command = txtCommand.get("1.0", tk.END).strip()
    
    # Check if the command is valid
    if not command.startswith('/'):
        print("Error: Command not found.")
        return

    input_list = command.split()
    command = input_list[0].strip()
    params = [param.strip() for param in input_list[1:] if param.strip()]


    print("Command: ", command)
    print("Parameters: ", params)

    if command == "/join":
        if is_connected:
            # print("Error: Connection to the server is already established.")
            update_output("Error: Connection to the server is already established.", txtOutput)
        elif not is_connected:
            if len(params) != 2:
                # print("Error: Command parameters do not match or are not allowed.")
                update_output("Error: Command parameters do not match or are not allowed.", txtOutput)
            else:
                try:
                    # Set-up the TCP socket
                    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                    # Get server address and port number
                    server_address = params[0]
                    server_port = int(params[1])

                    if server_port < 0 or server_port > 65535:
                        raise ValueError
                    
                    # Connect to the server
                    client_socket.connect((server_address, server_port))
                    server_response = client_socket.recv(BUFFER_SIZE).decode()

                    is_connected = True
                    # print(server_response)
                    update_output(server_response, txtOutput)
                    
                except (socket.error, ValueError) as e:
                    # print("Error: Connection to the Server has failed! Please check IP Address and Port Number")
                    update_output("Error: Connection to the Server has failed! Please check IP Address and Port Number", txtOutput)

    elif command == "/leave":
        if is_connected:
            if len(params) == 0:
                try:
                    # Send the '/leave' command to the server
                    client_socket.send(command.encode())

                    # Receive a message from the server
                    server_response = client_socket.recv(BUFFER_SIZE).decode()
                    # print(server_response)
                    update_output(server_response, txtOutput)

                    is_connected = False
                    client_socket.close()   # close the socket

                except Exception as e:
                    # print("Error: Disconnection failed. Please connect to the server first.")
                    update_output("Error: Disconnection failed. Please connect to the server first.", txtOutput)
            else:
                # print("Error: Command parameters do not match or are not allowed.")
                update_output("Error: Command parameters do not match or are not allowed.", txtOutput)
        elif not is_connected:
            # print("Error: Disconnection failed. Please connect to the server first.")
            update_output("Error: Disconnection failed. Please connect to the server first.", txtOutput)

    elif command == "/register":
        if is_connected:
            if len(params) != 1:
                # print("Error: Command parameters do not match or is not allowed.")
                update_output("Error: Command parameters do not match or is not allowed.", txtOutput)
            else:
                try:
                    # Get the handle or alias
                    alias = params[0]

                    # Send the command and handle (or alias) to the server
                    client_socket.send(command.encode())
                    client_socket.send(alias.encode())

                    # Receive a message from the server
                    server_response = client_socket.recv(BUFFER_SIZE).decode()
                    # print(server_response)
                    update_output(server_response, txtOutput)

                except Exception as e:
                    # print("Error: Registration Failed. Please enter a handle or alias!")
                    update_output("Error: Registration Failed. Please enter a handle or alias!", txtOutput)

        elif not is_connected:
            # print("Error: Disconnection failed. Please connect to the server first.")
            update_output("Error: Disconnection failed. Please connect to the server first.", txtOutput)

    elif command == "/store":
        if is_connected:
            if len(params) != 1:
                # print("Error: Command parameters do not match or is not allowed. /store cmd client")
                update_output("Error: Command parameters do not match or is not allowed. /store cmd client", txtOutput)
            else:
                try:
                    # Get the filename
                    filename = params[0]

                    # Check if file exists in local directory
                    if not os.path.exists(filename):
                        # print("Error: File does not exist.")
                        update_output("Error: File does not exist.", txtOutput)
                        # print("Client: ", os.getcwd())
                    else:
                        file_path = os.path.join(os.getcwd(), filename)
                        # print("Client File Path: ", file_path)

                        # open the file
                        f = open(file_path, 'rb')
                        file_data = f.read()
                        f.close()

                        # Send the command and filename to the server
                        client_socket.send(command.encode())
                        client_socket.send(filename.encode())

                        client_socket.sendall(file_data)

                        # Receive a message from the server
                        server_response = client_socket.recv(BUFFER_SIZE).decode()
                        # print(server_response)
                        update_output(server_response, txtOutput)

                except Exception as e:
                    # print("Error: Storing failed. Please enter a filename!")
                    update_output("Error: Storing failed. Please enter a filename!", txtOutput)

        elif not is_connected:
            # print("Error: Storing failed. Please connect to the server first.")
            update_output("Error: Storing failed. Please connect to the server first.", txtOutput)
    
    elif command == "/dir":
        if is_connected:
            if len(params) != 0:
                # print("Error: Command parameters do not match or are not allowed.")
                update_output("Error: Command parameters do not match or are not allowed.", txtOutput)
            else:
                try:
                    # Send the command to the server
                    client_socket.send(command.encode())

                    # Receive and print file names until "DONE" is received
                    # print("Server directory:")
                    update_output("Server directory:", txtOutput)
                    while True:
                        file_name = client_socket.recv(BUFFER_SIZE).decode()
                        if file_name == "DONE":
                            break

                        # Print each file name in the server directory
                        # print(file_name)
                        update_output(file_name, txtOutput)

                except Exception as e:
                    # print("Error: Directory request failed. Please connect to the server first.")
                    update_output("Error: Directory request failed. Please connect to the server first.", txtOutput)
        
        elif not is_connected:
            # print("Error: Directory request failed. Please connect to the server first.")
            update_output("Error: Directory request failed. Please connect to the server first.", txtOutput)

    elif command == "/get":
        if is_connected:
            if len(params) != 1:
                # print("Error: Command parameters do not match or is not allowed.")
                update_output("Error: Command parameters do not match or is not allowed.", txtOutput)
            else:
                try:
                    # Get the filename
                    filename = params[0]

                    # Send the command and filename to the server
                    client_socket.send(command.encode())
                    client_socket.send(filename.encode())

                    # Receive a message from the server
                    server_response = client_socket.recv(BUFFER_SIZE).decode()
                    # print(server_response)
                    update_output(server_response, txtOutput)

                    # Now, receive the file data from the server
                    file_data = client_socket.recv(BUFFER_SIZE)

                    # Save the received file data to a local file
                    file_path = os.path.join(os.getcwd(), filename)
                    with open(file_path, 'wb') as f:
                        f.write(file_data)

                    # print("File received from Server: " + filename)
                    update_output("File received from Server: " + filename, txtOutput)
                except Exception as e:
                        # print("Error: Getting file failed. Please enter a filename!")
                        update_output("Error: Getting file failed. Please enter a filename!", txtOutput)

        elif not is_connected:
            # print("Error: Getting file failed. Please connect to the server first.")
            update_output("Error: Getting file failed. Please connect to the server first.", txtOutput)

    elif command == "/?":
        # displayCommands()
        all_commands = displayCommands()
        for command in all_commands:
            # print(command)
            update_output(command, txtOutput)

    else:
        # Error Message
        # print("Error: Command not found.")
        update_output("Error: Command not found.", txtOutput)



def update_output(message, txtOutput):
    txtOutput.configure(state=tk.NORMAL)        # Enable editing of the widget
    txtOutput.insert(tk.END, message + '\n')    # Insert the string at the end
    txtOutput.configure(state=tk.DISABLED)      # Disable editing of the widget
    txtOutput.see(tk.END)                       # Scroll to the end of the widget


def main():

    # Create the main window
    ROOT = tk.Tk()
    ROOT.geometry("500x500")
    ROOT.title("File Exchange System")

    # Make the window non-resizable
    ROOT.resizable(False, False)

    # Label for Title
    lblTitle = tk.Label(ROOT, text="File Exchange System", font=("Arial", 20))
    lblTitle.pack(pady=10, padx=100, anchor="center")

    # Label for Input Command
    lblCommand = tk.Label(ROOT, text="Input Command (Type '/?' for help):", font=("Arial", 12))
    lblCommand.pack(pady=10, padx=10, anchor="w")
    
    
    # Entry widget for Input Command
    txtCommand = tk.Text(ROOT, height=1.3, width=43, font=("Arial", 15))
    txtCommand.pack(pady=0, padx=10, anchor="w")

    # Add temporary text to the textbox in a grey color
    txtCommand.insert(tk.END, "Enter a command here.")
    txtCommand.config(fg="grey")

    # When the user clicks on the textbox, the text will be cleared
    def clearText(event):
        txtCommand.delete(1.0, tk.END)
        txtCommand.config(fg="black")

    txtCommand.bind("<Button-1>", clearText)

    # Button for Enter beside the textbox
    btnEnter = tk.Button(ROOT, width=10, text="Enter", font=("Arial", 12), command=lambda: toServer(txtCommand, txtOutput))
    btnEnter.pack(pady=5, padx=10, anchor="center")  # Pack on the right side

    # Everytime the user presses the Enter key, the command will be sent to the server and the text will be cleared
    def enterKey(event):
        toServer(txtCommand, txtOutput)
        txtCommand.delete(1.0, tk.END)
        txtCommand.config(fg="black")

    ROOT.bind("<Return>", enterKey)


    # Label for Output Area
    lblOutput = tk.Label(ROOT, text="Output Area:", font=("Arial", 12))
    lblOutput.pack(pady=10, padx=10, anchor="w")

    # Textbox for Output Area, get the output from the server
    txtOutput = tk.Text(ROOT, height=15, width=80, font=("Arial", 10))
    txtOutput.pack(pady=0, padx=10, anchor="w")

    # User cannot edit the textbox
    txtOutput.config(state=tk.DISABLED)

    # Run the main loop
    ROOT.mainloop()


if __name__ == "__main__":
    main()