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



#connection to mongo
def connect_mongo():
    #fill in with my mongo database
    client = MongoClient('mongodb+srv://choharry888:j741z2FEdn05nnCA@cluster0.01gxb.mongodb.net/')
    db = client['test']
    return db

#get the correct time in pst
def time_pst(timestamp):
    utc_time = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    utc_time = pytz.utc.localize(utc_time)
    pst_time = utc_time.astimezone(pytz.timezone("US/Pacific"))
    return pst_time.strftime("%Y-%m-%d %I:%M:%S %p")

#get correct moisture reading to rh
def moisture_rh(moisture):
    return(moisture/1024) *100

#actually processing the metadata
def process_query(db, query):
    if query == VALID_QUERIES[0]:
        now = datetime.now(pytz.UTC)
        three_hours = now - timedelta(hours=3)
        fridge_data = db.readings.find({"device_type": "fridge", "timestamp": {"$gte": three_hours}})
        
        readings = list(fridge_data)
        if not readings:
            return "No data available for the past 3 hours."

        avg_moisture = sum([moisture_rh(doc["moisture"]) for doc in fridge_data]) / fridge_data.count()
        return f"Average moisture in the past 3 hours: {avg_moisture:.2f}% RH (PST)"

    elif query == VALID_QUERIES[1]:
        dishwasher_data = db.readings.find({"device_type": "dishwasher"})

        readings = list(dishwasher_data)
        if not readings:
            return "No data available for the dishwasher."    

        avg_water = sum([doc["water_usage"] for doc in dishwasher_data]) / dishwasher_data.count()
        return f"Average water consumption per cycle: {avg_water:.2f} gallons"
    
    elif query == VALID_QUERIES[2]:
        device_data = db.readings.aggregate([
            {"$group": {"_id": "$device_id", "total_electricity": {"$sum": "$electricity"}}},
            {"$sort": {"total_electricity": -1}},
            {"$limit": 1}
        ])

        top_device = list(device_data)
        if not top_device:
            return "No electricity data available."

        device = top_device[0]
        return f"Device {device['_id']} consumed the most electricity: {device['total_electricity']:.2f} kWh"

    return "Invalid query."


#from previous assignment
def start_server():
    print("server control")
    db = connect_mongo()
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

if __name__ == "__main__":
    start_server()
