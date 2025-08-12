from flask import Blueprint, jsonify
from services.mongo import chat_collection

chat_titles_bp = Blueprint("chat_titles", __name__)


@chat_titles_bp.route("/chat-titles", methods=["GET"])
def get_chat_titles():
    try:
        chat_titles_cursor = chat_collection.aggregate([
            {"$sort": {"createdAt": 1}},
            {
                "$group": {
                    "_id": "$sessionId",
                    "firstMessage": {"$first": "$content"},
                    "createdAt": {"$first": "$createdAt"}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "sessionId": "$_id",
                    "title": "$firstMessage",
                    "createdAt": 1
                }
            },
            {"$sort": {"createdAt": -1}}
        ])

        chat_titles = []
        for doc in chat_titles_cursor:
            words = doc["title"].split()
            truncated = " ".join(words[:10]) + ("..." if len(words) > 10 else "")
            chat_titles.append({
                "sessionId": doc["sessionId"],
                "title": truncated,
                "createdAt": doc["createdAt"]
            })

        return jsonify(chat_titles), 200
    except Exception as e:
        print("Error fetching chat titles:", str(e))
        return jsonify({"error": "Failed to load chat titles"}), 500


