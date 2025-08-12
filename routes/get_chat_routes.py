from flask import Blueprint, jsonify
from pymongo import ASCENDING
from services.mongo import chat_collection

get_chat_bp = Blueprint("get_chat", __name__)



@get_chat_bp.route("/chat/<sessionId>", methods=["GET"])
def get_chat(sessionId):
    try:
        chats = chat_collection.find({"sessionId": sessionId}).sort("createdAt", ASCENDING)
        chat_list = list(chats)
        for chat in chat_list:
            chat["_id"] = str(chat["_id"])  # Convert ObjectId for JSON
        return jsonify(chat_list), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
