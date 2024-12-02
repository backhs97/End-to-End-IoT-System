import socket
from pymongo import MongoClient
from datetime import datetime, timedelta

#connection to mongo
def connect_mongo():
    #fill in with mine mongo database
    client = MongoClient()
    db = client[]
    return db

print("server control")
myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

while True:
    # Keep trying until a successful connection
    try:
        serverIP = input("Enter the server IP address: ")
        serverPort = int(input("Enter the server port number: "))

        #uses the server
        myTCPSocket.bind((serverIP , serverPort))
        myTCPSocket.listen(5)
        print(f"Server is listening on port {serverPort}")
        break 
    except (socket.gaierror, ConnectionRefusedError):
        print("Error: check ip or port addresses")
    except Exception as e:
        print(f"Error: {e}")
while True:
    #gets message and confirms
    try:
        incomingSocket, incomingAddress = myTCPSocket.accept()
        print(f"connected by {incomingAddress}")

        while True:
            myData = incomingSocket.recv(1024).decode()
            if not myData:
                break
            print(f"recieved message: {myData}")
            incomingSocket.send(bytearray(str(myData.upper()), encoding='utf-8'))

    except Exception as e:
        print(f"Error during connection handling: {e}")

    finally:
        #ends connection
        incomingSocket.close()
        print("connection closed")

