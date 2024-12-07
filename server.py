import socket
from pymongo import MongoClient
from datetime import datetime, timedelta
import pytz
import sys

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

    #insert a new node into the binary tree done recursively
    def insert(self, data, key="payload.timestamp"):
        if not self.root:
            self.root = TreeNode(data)
        else:
            self._insert_recursive(self.root, data, key)

    def _insert_recursive(self, node, data, key):
        if data.get(key) < node.data.get(key):
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
        if self.root is None:
            return []
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
    three_hours_ago = datetime.now(pytz.utc) - timedelta(hours=3)
    print("Three hours ago:", three_hours_ago)
    three_hours_timestamp = int(three_hours_ago.timestamp() / 1000)
    print("Three hours ago:", three_hours_timestamp)
    #fetch metadata from mongoDB
    
    total_docs = db.Table_virtual.count_documents({})
    print("Total documents in the collection:", total_docs)
    count = db.Table_virtual.count_documents({
        "payload.timestamp": {"$gte": three_hours_timestamp}
    })
    all_data = db.Table_virtual.find({
        "payload.timestamp": {"$gte": three_hours_timestamp}
    })
    print("Total documents in the collection:", count)
    for doc in all_data:
        try:
            # Ensure timestamp is correctly converted
            timestamp = int(doc["payload"]["timestamp"])
            doc["payload"]["timestamp"] = datetime.fromtimestamp(timestamp, pytz.utc)
            tree.insert(doc["payload"], key="timestamp")
        except (KeyError, ValueError, TypeError) as e:
            print(f"Skipping document due to error: {e}")

    return tree


#connection to mongo
def connect_mongo():
    #fill in with my mongo database
    client = MongoClient('URL')
    db = client['test']
    return db

#converts to RH assuming you have a linear mapping or readings
def moisture_rh(moisture):
    min_temp = 10 
    max_temp = 30  
    min_rh = 20     
    max_rh = 80
    if moisture < min_temp:
        return min_rh
    elif moisture > max_temp:
        return max_rh
    
    rh = ((moisture - min_temp) / (max_temp - min_temp)) * (max_rh - min_rh) + min_rh
    return(rh)

#actually processing the metadata
def process_query(tree, query):
    if query == VALID_QUERIES[0]:
        print("Query 0")
        #three_hours = datetime.now(pytz.utc)  - timedelta(hours=3)
        #three_hours_timestamp = (three_hours.timestamp() / 1000)

        #possibly edit this
        results = [
            node for node in tree.inorder_traversal()
            #if "timestamp" in node and node["timestamp"].isdigit() and int(node["timestamp"]) >= three_hours_timestamp
            #if int(node["timestamp"]) >= three_hours_timestamp
        ]
        
        if not results:
            return "No data available for the past 3 hours."
        
        avg_moisture = sum([float(doc["Moisture Meter - moist"]) for doc in results if "Moisture Meter - moist" in doc]) / len(results)        
        return f"Average moisture : {avg_moisture:.2f}% RH"

    elif query == VALID_QUERIES[1]:
        print("Query 1")
        #change this based on db
        dishwasher_data = [
            node for node in tree.inorder_traversal()
            #i misnamed teh dishwasher as refrigerator
            if "new smart refrigerator" in node["board_name"].lower()
        ]

        if not dishwasher_data:
            return "No data available for the dishwasher."

        #edit this
        avg_water = sum([float(doc["watercon"]) for doc in dishwasher_data if "watercon" in doc]) / len(dishwasher_data)
        return f"Average water consumption per cycle: {avg_water:.2f} gallons"
    
    elif query == VALID_QUERIES[2]:
        print("Query 2")
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
    print("=== IoT Query Server ===")
    db = connect_mongo()
    tree = populate_tree_from_db(db)
    myTCPSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while True:
        # Keep trying until a successful connection
        try:
            server_ip = input("Enter the server IP address: ")
            server_port = int(input("Enter the server port number: "))
            
            myTCPSocket.bind((server_ip, server_port))
            myTCPSocket.listen(5)
            print(f"\nServer is listening on {server_ip}:{server_port}")
            break
        except ValueError:
            print("Error: Port must be a number. Please try again.")
        except socket.gaierror:
            print("Error: Invalid IP address. Please try again.")
        except OSError as e:
            print(f"Error: {e}. The address might be in use or you may not have permission.")
        except Exception as e:
            print(f"Error: {e}")
        
        retry = input("\nWould you like to try again? (y/n): ")
        if retry.lower() != 'y':
            sys.exit(1)

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
                    response = "Invalid query please review the available queries"
                incomingSocket.send(bytearray(response, encoding='utf-8'))
        except Exception as e:
            print(f"Error during connection handling: {e}")

        finally:
            #ends connection
            incomingSocket.close()
            print("connection closed")
            
            #continues server
            continue_server = input("\nDo you want to continue running the server? (y/n): ")
            if continue_server.lower() != 'y':
                print("Shutting down server...")
                myTCPSocket.close()
                sys.exit(0)
            print("\nWaiting for new connection...")

if __name__ == "__main__":
    start_server()
