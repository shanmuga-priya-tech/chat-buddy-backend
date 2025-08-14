from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from pymongo import MongoClient
from datetime import datetime, timezone


class CustomMongoChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, connection_string, database_name, collection_name):
        self.session_id = session_id
        self.client = MongoClient(connection_string)
        self.collection = self.client[database_name][collection_name]

    @property
    def messages(self):
        docs = self.collection.find({"sessionId": self.session_id}).sort("timestamp", 1)
        messages = []
        for doc in docs:
            role = doc.get("role")
            content = doc.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "bot":
                messages.append(AIMessage(content=content))
            elif role == "system":
                messages.append(SystemMessage(content=content))
        return messages

    def add_message(self, message):
        if isinstance(message, HumanMessage):
            role = "user"
        elif isinstance(message, AIMessage):
            role = "bot"
        elif isinstance(message, SystemMessage):
            role = "system"
        else:
            raise ValueError(f"Unknown message type: {type(message)}")

        self.collection.insert_one({
            "sessionId": self.session_id,
            "role": role,
            "content": message.content,
            "timestamp": datetime.now(timezone.utc)  # Use consistent timestamp field
        })

    def clear(self):
        self.collection.delete_many({"sessionId": self.session_id})  # Fixed key name
