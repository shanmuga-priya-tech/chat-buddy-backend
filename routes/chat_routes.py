from flask import Blueprint, request, jsonify
from pathlib import Path
from components.vectorstore import get_vectorstore
from services.firebase import get_user_id_from_request
from langchain_google_genai import ChatGoogleGenerativeAI
import uuid
from components.memory_chain import get_chat_chain
from helpers.domain_classifier import is_loan_related
from helpers.generalTalkClassifier import is_small_talk
from tools.tools import extract_and_calculate_emi,summarise_pdf,web_search
from services.mongo import uploads_collection


chat_bp = Blueprint("chats", __name__)


# Vectorstore initialization
vectorstore = get_vectorstore()
# predefined_vectorstore = get_vectorstore()  #yet to implement

#initialize llm
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

@chat_bp.route("/chat", methods=["POST"])
def chat():
    user_id = get_user_id_from_request()
    data = request.get_json()
    query = data.get("query")
    chat_id = data.get("chatId") or str(uuid.uuid4())

    if not query or len(query.strip())<=0:
        return jsonify({"error": "No query provided"}), 400

    session_id = f"{user_id}:{chat_id}"

    #TODO: logic issue find a way to select which pdf user is querying for
    uploaded_pdfs = uploads_collection.find_one({"user_id": user_id})
    SIMILARITY_THRESHOLD = 0.75
    best_score = 0
    response_text = None

    try:
        # 1)general msgs
        if is_small_talk(query):
            return jsonify({
                "response": "Hello! I can help you with loan-related queries and also guide you through your uploaded documents.",
                "chatId": chat_id
            }), 200
        
        # 2) check domain relevance
        if not is_loan_related(query):
            return jsonify({
                "response": "Sorry, I can only assist with loan-related queries at the moment.",
                "chatId": chat_id
            }), 200
        
        # 3) Tool-first intent detection
        if "emi" in query.lower():
            return jsonify({"response": extract_and_calculate_emi(query), "chatId": chat_id}), 200
        
        #TODO: updation needs to made for logic to select the latest pdf
        if "summarise" in query.lower():
            if uploaded_pdfs:
                return jsonify({"response": summarise_pdf(uploaded_pdfs["namespace"]), "chatId": chat_id}), 200
            else:
                return jsonify({"response": "No PDF found to summarise."}), 200

        # 4) if pdf
        if uploaded_pdfs:
            namespace = uploaded_pdfs["namespace"]
            results = vectorstore.similarity_search_with_score(query, k=3, namespace=namespace)
            print(results)

            if results:
                score = results[0][1]  # tuple: (doc, score)
                best_score = max(best_score, score)
                chain = get_chat_chain(session_id, vectorstore.as_retriever(search_kwargs={"k": 3, "namespace": namespace}))
                pdf_answer = chain.invoke({"question": query}).get("answer", "").strip()
                if pdf_answer:
                    response_text = pdf_answer

        # 5) If no PDF or low score → fallback to loan DB 
        #TODO:yet to implement
        if not response_text or best_score < SIMILARITY_THRESHOLD:
            predefined_vs = get_vectorstore("loan_dataset")
            results = predefined_vs.similarity_search_with_score(query, k=3)

            if results:
                score = results[0][1]
                best_score = max(best_score, score)
                chain = get_chat_chain(session_id, predefined_vs.as_retriever(search_kwargs={"k": 3}))
                db_answer = chain.invoke({"question": query}).get("answer", "").strip()
                if db_answer:
                    response_text = db_answer

        # 6) Final fallback: web search
        if not response_text or best_score < SIMILARITY_THRESHOLD:
            response_text = web_search(query)

            return jsonify({"response": response_text, "chatId": chat_id}), 200
            
    except Exception as e:
        print("Chat error:", str(e))
        return jsonify({"error": "Failed to process query"}), 500
    