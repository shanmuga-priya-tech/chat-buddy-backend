from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from pymongo import MongoClient
from datetime import datetime,timezone


class CustomMongoChatMessageHistory(BaseChatMessageHistory):
    def __init__(self, session_id, connection_string, database_name, collection_name):
        self.session_id = session_id
        self.client = MongoClient(connection_string)
        self.collection = self.client[database_name][collection_name]

    @property
    def messages(self):
        docs = self.collection.find({"sessionId": self.session_id}).sort("timestamp", 1)
        print("docs:", list(docs))
        messages = []
        for doc in docs:
            if doc["role"] == "user":
                messages.append(HumanMessage(content=doc["content"]))
            elif doc["role"] == "bot":
                messages.append(AIMessage(content=doc["content"]))
        return messages

    def add_message(self, message):
        role = "user" if isinstance(message, HumanMessage) else "bot"
        self.collection.insert_one({
            "sessionId": self.session_id,
            "role": role,
            "content": message.content,
            "createdAt": datetime.now(timezone.utc).isoformat()
        })

    def clear(self):
        self.collection.delete_many({"session_id": self.session_id})
