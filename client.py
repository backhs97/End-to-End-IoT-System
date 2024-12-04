import socket
import sys

VALID_QUERIES = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
]

def display_menu():
    """Display numbered menu options"""
    print("\n=== Available Queries ===")
    print("1. What is the average moisture inside my kitchen fridge in the past three hours?")
    print("2. What is the average water consumption per cycle in my smart dishwasher?")
    print("3. Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?")
    print("Type 'exit' to quit\n")

def connect_to_server():
    """Establish connection to server with user input"""
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        try:
            # Get server details from user
            server_ip = input("Enter the server IP address: ")
            server_port = int(input("Enter the server port number: "))
            
            # Attempt connection
            client_socket.connect((server_ip, server_port))
            print(f"\nSuccessfully connected to server at {server_ip}:{server_port}")
            return client_socket
            
        except ValueError:
            print("Error: Port must be a number. Please try again.")
        except socket.gaierror:
            print("Error: Invalid IP address. Please try again.")
        except ConnectionRefusedError:
            print("Error: Connection refused. Please check if server is running.")
        except Exception as e:
            print(f"Error: {e}. Please try again.")
        
        retry = input("\nWould you like to try connecting again? (y/n): ")
        if retry.lower() != 'y':
            sys.exit(1)

def main():
    print("=== IoT Query Client ===")
    
    # Connect to server
    client_socket = connect_to_server()
    
    try:
        while True:
            display_menu()
            user_input = input("Enter your choice: ").strip()
            
            # Handle exit condition
            if user_input.lower() == 'exit':
                print("Exiting program...")
                break
            
            # Handle menu choices
            if user_input in ['1', '2', '3']:
                query_index = int(user_input) - 1
                query = VALID_QUERIES[query_index]
                
                try:
                    # Send query to server
                    client_socket.send(query.encode('utf-8'))
                    
                    # Get and display server response
                    server_response = client_socket.recv(1024).decode('utf-8')
                    print("\nServer Response:")
                    print("=" * 50)
                    print(server_response)
                    print("=" * 50)
                    
                except ConnectionResetError:
                    print("Error: Connection lost with server.")
                    break
                except Exception as e:
                    print(f"Error communicating with server: {e}")
                    break
            else:
                print("Invalid choice. Please enter 1, 2, 3, or 'exit'")
                
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        client_socket.close()
        print("\nConnection closed")

if __name__ == "__main__":
    main()
