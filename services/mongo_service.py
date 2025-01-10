from pymongo import MongoClient, ASCENDING
import datetime

# MongoDB connection string
connection_string = "mongodb://localhost:27017"

def save_chat(data: dict):
    """
    Saves a chat message to the MongoDB database.
    Automatically adds a timestamp to the data.
    
    Args:
        data (dict): The chat data to save.
    """
    data['timestamp'] = datetime.datetime.now()  # Add current timestamp to the data
    with MongoClient(connection_string) as client:
        client['chatbot_db']['chat'].insert_one(data)  # Insert the data into the 'chat' collection

def fetch_chat(user_id: str):
    """
    Fetches all chat messages for a specific user from the MongoDB database.
    The messages are sorted by timestamp in ascending order.

    Args:
        user_id (str): The user ID to fetch chat messages for.

    Returns:
        list: A list of chat messages for the user.
    """
    with MongoClient(connection_string) as client:
        # Query the 'chat' collection for the given user ID and sort by timestamp
        return list(client['chatbot_db']['chat']
                    .find({'user_id': user_id})
                    .sort('timestamp', ASCENDING))
