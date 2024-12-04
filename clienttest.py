import socket

VALID_QUERIES = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
]
print("Client control")
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    # Keep trying until a successful connection
    try:
        #user inputs ip and port
        #serverIP = input("Enter the server IP address: ")
        #serverPort = int(input("Enter the server port number: "))
        #connects
        #myTCPSocket.connect((serverIP, serverPort))
        myTCPSocket.connect(("127.0.0.1", 8080))
        #print(f"Connected to server at {serverIP}:{serverPort}")
        print(f"Connected to server at 127.0.0.1:8080")
        break
# Exit the loop when connection is successful
    except (socket.gaierror, ConnectionRefusedError):
        print("Error: check IP or port addresses. Please try again.")
    except Exception as e:
        print(f"Error: {e}. Please try again.")
try:
    while True:
        someData = input("Enter the message (type 'exit' to quit): ")
        if someData.lower() == "exit":
            # Allow user to exit
            break
        elif someData == "1":
            myTCPSocket.send(bytearray((VALID_QUERIES[0]), encoding='utf-8'))
            serverResponse = myTCPSocket.recv(1024).decode('utf-8')
            print(f"Server response: {serverResponse}")
        elif someData == "2":
            myTCPSocket.send(bytearray((VALID_QUERIES[1]), encoding='utf-8'))
            serverResponse = myTCPSocket.recv(1024).decode('utf-8')
            print(f"Server response: {serverResponse}")
        elif someData == "3":
            myTCPSocket.send(bytearray((VALID_QUERIES[2]), encoding='utf-8'))
            serverResponse = myTCPSocket.recv(1024).decode('utf-8')
            print(f"Server response: {serverResponse}")
        else:
        #sending message
            myTCPSocket.send(bytearray((someData), encoding='utf-8'))
        #get server response
            serverResponse = myTCPSocket.recv(1024).decode('utf-8')
            print(f"Server response: {serverResponse}")
except Exception as e:
    print(f"Error: {e}")
finally:
    #close socket
    myTCPSocket.close()
    print("Connection closed")
