import socket
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz

#valid queries
VALID_QUERIES = [
    "What is the average moisture inside my kitchen fridge in the past three hours?",
    "What is the average water consumption per cycle in my smart dishwasher?",
    "Which device consumed more electricity among my three IoT devices (two refrigerators and a dishwasher)?"
]

#making the bst
class TreeNode:
    def __init__(self, data):
        # Store metadata
        self.data = data 
        self.left = None       
        self.right = None

class BinarySearchTree:
    def __init__(self):
        self.root = None

    #nsert a new node into the binary tree done recursively
    def insert(self, data, key="payload.timestamp"):
        if not self.root:
            self.root = TreeNode(data)
        else:
            self._insert_recursive(self.root, data, key)

    def _insert_recursive(self, node, data, key):
        if data[key] < node.data[key]:
            if node.left is None:
                node.left = TreeNode(data)
            else:
                self._insert_recursive(node.left, data, key)
        else:
            if node.right is None:
                node.right = TreeNode(data)
            else:
                self._insert_recursive(node.right, data, key)

    #Search for a node with a specific key done recursively
    def search(self, key_value, key="payload.timestamp"):
        return self._search_recursive(self.root, key_value, key)

    def _search_recursive(self, node, key_value, key):
        if node is None or node.data[key] == key_value:
            return node
        elif key_value < node.data[key]:
            return self._search_recursive(node.left, key_value, key)
        else:
            return self._search_recursive(node.right, key_value, key)

    #in-order traversal to retrieve sorted data
    def inorder_traversal(self, node=None, results=None):
        if results is None:
            results = []
        if node is None:
            node = self.root
        if node.left:
            self.inorder_traversal(node.left, results)
        results.append(node.data)
        if node.right:
            self.inorder_traversal(node.right, results)
        return results


def populate_tree_from_db(db):
    tree = BinarySearchTree()
    three_days = datetime.now(pytz.utc) - timedelta(days=3)
    #fetch metadata from mongoDB
    all_data = db.readings.find({"payload.timestamp": {"$gte": three_days}})  
    for doc in all_data:
        doc["payload"]["timestamp"] = datetime.fromtimestamp(float(doc["payload"]["timestamp"]), pytz.utc)
        tree.insert(doc["payload"], key="timestamp")
    return tree


#connection to mongo
def connect_mongo():
    #fill in with my mongo database
    client = MongoClient('mongodb+srv://choharry888:j741z2FEdn05nnCA@cluster0.01gxb.mongodb.net/')
    db = client['test']
    return db

#get correct moisture reading to rh
def moisture_rh(moisture):
    return(moisture/1024) *100

#actually processing the metadata
def process_query(tree, query):
    if query == VALID_QUERIES[0]:
        three_hours = datetime.now(pytz.utc)  - timedelta(hours=3)

        #possibly edit this
        results = [
            node for node in tree.inorder_traversal()
            if node["timestamp"] >= three_hours
        ]
        
        if not results:
            return "No data available for the past 3 hours."
        #edit this
        avg_moisture = sum([moisture_rh(doc["Moisture Meter - moist"]) for doc in results]) / len(results)
        return f"Average moisture : {avg_moisture:.2f}% RH"

    elif query == VALID_QUERIES[1]:
        #change this based on db
        dishwasher_data = [
            node for node in tree.inorder_traversal()
            #i misnamed teh dishwasher as refrigerator
            if "new smart refrigerator" in node["board_name"].lower()
        ]

        if not dishwasher_data:
            return "No data available for the dishwasher."

        #edit this
        avg_water = sum([float(doc["watercon"]) for doc in dishwasher_data]) / len(dishwasher_data)
        return f"Average water consumption per cycle: {avg_water:.2f} gallons"
    
    elif query == VALID_QUERIES[2]:
        #change this based on db
        #sensor 3 08e06c94-246e-49f0-80fa-166efa1a8e8b
        #ammeter
        #dish ammeter

        ammeter_fields = {
            "Dishwasher": "dish ammeter",
            "Refrigerator": "ammeter",
            "Virtual Fridge": "sensor 3 08e06c94-246e-49f0-80fa-166efa1a8e8b"
        }

        totals = {}
        counts = {}
        for device in ammeter_fields.keys():
            totals[device] = 0
            counts[device] = 0
        
        for doc in tree.inorder_traversal():
            for device, field in ammeter_fields.items():
                if field in doc:
                    totals[device] += float(doc[field])
                    counts[device] += 1

        averages = {
            device: (totals[device] / counts[device]) if counts[device] > 0 else None
            for device in ammeter_fields.keys()
        }

        top_device = None
        highest_average = 0

        for device, average in averages.items():
            if average is not None and average > highest_average:
                top_device = device
                highest_average = average
        
        if top_device is not None:
            return f"Device {top_device} has the highest average consumption: {highest_average:.2f} kWh"
        else:
            return "No valid data available for any device."

#from previous assignment
def start_server():
    print("server control")
    db = connect_mongo()
    tree = populate_tree_from_db(db)
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
                
                if myData in VALID_QUERIES:
                    response = process_query(tree,myData)
                else:
                    response = "Invalid query"
                incomingSocket.send(bytearray(response, encoding='utf-8'))
        except Exception as e:
            print(f"Error during connection handling: {e}")

        finally:
            #ends connection
            incomingSocket.close()
            print("connection closed")

if __name__ == "__main__":
    start_server()
