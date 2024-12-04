import socket

def run_server():
    server_ip = None
    server_port = None

    # Server main menu
    while True:
        print("\nServer Menu:")
        print("1. Enter the server IP address")
        print("2. Enter the server port number")
        print("3. Exit the program")

        try:
            option = input("Choose an option (1-3): ")
            if option == '1':
                # ip address input
                server_ip = input("Enter the server IP address: ")

                try:
                    # ip address validation
                    socket.inet_aton(server_ip)
                    print(f"IP address {server_ip} is valid.") # IP address validation message
                except socket.error:
                    print("Error: Invalid IP address. Please enter a valid IP address.") # Error message for invalid IP address input
                    server_ip = None
            
            # Correct port number input
            elif option == '2':
                if not server_ip:
                    print("Please enter a valid IP address first (Option 1).")
                    continue

                # Port number input
                server_port = input("Enter the port number: ")

                try:
                    # Port number validation
                    server_port = int(server_port)
                    if not (0 < server_port < 65536): # Port number range validation
                        raise ValueError
                    print(f"Port {server_port} is valid.") # Port number validation message
                except ValueError:
                    print("Error: Invalid port number. Please enter a valid port number.") # Error message for invalid port number input
                    server_port = None

                if server_port:
                    # TCP server socket creation
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                        server_socket.bind((server_ip, server_port))
                        server_socket.listen(5)
                        print(f"Server is running and listening on {server_ip}:{server_port}...") # Server running message

                        while True: # Server loop
                            client_socket, client_address = server_socket.accept()
                            with client_socket:
                                print(f"Connected by {client_address}") # Client connection message
                                while True: # Client loop
                                    try:
                                        message = client_socket.recv(1024).decode() # Message received from the client

                                        if not message: # Empty message
                                            print(f"Connection closed by {client_address}.") # Connection closed message
                                            break
 
                                        print(f"Message from {client_address}: {message}") # Message from client

                                        response = message.upper() # Message to be sent to the client (converted to uppercase)
                                        client_socket.sendall(response.encode()) # Send response to the client

                                    except ConnectionResetError: # Connection forcibly closed by the client
                                        print(f"Client {client_address} forcibly closed the connection.")
                                        break

                            print("Returning to the main menu...") # Return to the main menu message
                            break

            elif option == '3': # Exit the server
                print("Exiting server...") # Exit message
                break

            else:
                print("Error: Invalid option. Please choose 1, 2, or 3.") # Error message for invalid option input

        except Exception as e: # Unexpected error
            print(f"An unexpected error occurred: {e}") # Unexpected error message

if __name__ == "__main__":
    run_server()
