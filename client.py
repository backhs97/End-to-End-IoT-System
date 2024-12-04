import socket 
import ipaddress # Import the ipaddress module for IP address validation

def run_client():
    server_ip = None
    server_port = None
    
    # Client main menu
    while True:
        print("\nClient Menu:")
        print("1. Enter the server IP address")
        print("2. Enter the server port number")
        print("3. Exit the program")

        try:
            option = input("Choose an option (1-3): ") # Option input

            if option == '1':
                # Correct IP address input
                server_ip = input("Enter the server IP address: ")

                try:
                    # IP address validation
                    ipaddress.ip_address(server_ip)
                    print(f"IP address {server_ip} is valid.")
                except ValueError:
                    print("Error: Invalid IP address. Please try again.") # Error message for invalid IP address input
                    server_ip = None

            elif option == '2':
                if not server_ip:
                    print("Please enter a valid IP address first (Option 1).") # Error message for missing IP address
                    continue # Return to the main menu

                # Correct port number input
                server_port = input("Enter the server port number: ")

                try:
                    # Port number validation
                    server_port = int(server_port)
                    if not (0 < server_port < 65536): # Port number range validation
                        raise ValueError
                    print(f"Port {server_port} is valid.")
                except ValueError:
                    print("Error: Invalid port number. Please enter a valid port number.") # Error message for invalid port number input
                    server_port = None

                if server_port:
                    # Client socket creation
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                        try:
                            # Connect to the server
                            client_socket.connect((server_ip, server_port))
                            print(f"Connected to the server at {server_ip}:{server_port}")

                            while True:
                                # Client message input
                                message = input("Enter message to send to the server (or type 'exit' to quit): ")

                                if message.lower() == 'exit': # Exit, if 'exit' is entered
                                    print("Exiting client...") # Exit message
                                    break # Exit the client

                                if message.strip() == '':
                                    print("Error: Empty message. Please enter a valid message.") # Error message for empty message
                                    continue

                                # Send message to the server
                                client_socket.sendall(message.encode())

                                # Server response
                                response = client_socket.recv(1024).decode()
                                print("Server response:", response)

                        except (socket.gaierror, socket.error) as e:
                            print(f"Connection error: {e}") # Connection error message
                            continue

            elif option == '3':
                print("Exiting program...") # Exit message for the program
                break

            else:
                print("Error: Invalid option. Please choose 1, 2, or 3.") # Error message for invalid option input

        except Exception as e:
            print(f"An unexpected error occurred: {e}") # Unexpected error message

if __name__ == "__main__":
    run_client()
