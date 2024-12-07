# End-to-End-IoT-System

When prompted:
1. Enter the same IP address used for the server
2. Enter the same port number used for the server

## Available Queries

The system supports three types of queries:

1. Average moisture inside kitchen fridge (past 3 hours)
2. Average water consumption per cycle in smart dishwasher
3. Electricity consumption comparison among IoT devices

## Usage Instructions

1. **Start the Server First**:
   - Run server.py
   - Enter IP address and port
   - Server will start listening for connections

2. **Start the Client**:
   - Run client.py
   - Enter the same IP and port as the server
   - Select queries from the menu (1-3)
   - Type 'exit' to quit

3. **Database Connection**:
   - The server automatically connects to MongoDB ( you need to add MongoDB URL in server.py )
   - No additional configuration needed for database connection

## Error Handling

The system includes robust error handling for:
- Invalid IP addresses
- Incorrect port numbers
- Lost connections
- Invalid queries
- Database connection issues

## Troubleshooting

- If connection fails, ensure:
  - Server is running before starting client
  - IP address and port numbers match
  - Port is not in use by another application
  - MongoDB connection string is valid
