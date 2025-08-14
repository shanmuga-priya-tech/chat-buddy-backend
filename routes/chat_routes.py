from flask import Blueprint, request, jsonify
from pathlib import Path
from components.dataset_vectorstore import get_dataset_vectorstore
from components.userSpecific.user_vectorstore import get_user_vectorstore
from services.firebase import get_user_id_from_request
from langchain_google_genai import ChatGoogleGenerativeAI
import uuid
from components.memory_chain import get_chat_chain
from helpers.domain_classifier import is_loan_related
from helpers.generalTalkClassifier import is_small_talk
from helpers.user_upload import upload_pdf
from tools.tools import extract_and_calculate_emi
from services.mongo import uploads_collection
from langchain_core.messages import SystemMessage


chat_bp = Blueprint("chats", __name__)


# Vectorstore initialization
predefined_vectorstore = get_dataset_vectorstore()


#initialize llm
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")

@chat_bp.route("/chat", methods=["POST"])
def chat():
    user_id = get_user_id_from_request()
    print("file:",request.files.get("file"))

    # 1) Handle both multipart/form-data and JSON
    file = None
    if request.content_type and request.content_type.startswith("multipart/form-data"):
        # With PDF
        query = request.form.get("query", "").strip()
        chat_id = request.form.get("chatId") or str(uuid.uuid4())
        file = request.files.get("file")
    else:
        # Chat only
        data = request.get_json()
        query = (data.get("query") or "").strip()
        chat_id = data.get("chatId") or str(uuid.uuid4())

    if not query:
        return jsonify({"error": "No query provided"}), 400

    session_id = f"{user_id}:{chat_id}"
    


    # 3) if pdf exists process it first
    if file:
        print("pdf uploading:", file)
        already_pdf_uploaded = uploads_collection.find_one({"namespace": session_id})
        if already_pdf_uploaded:
            return jsonify({"response": "Only one pdf upload is allowed per session! Open new chat.", "chatId": chat_id}), 200

        upload_response, status_code = upload_pdf(file, session_id, user_id)
        if status_code != 200:
            return upload_response, status_code

    # After uploading (or if PDF already exists)
    user_vectorstore = get_user_vectorstore(session_id)
    uploaded_pdf = uploads_collection.find_one({"namespace": session_id})

    
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
        if "calculate emi" in query.lower():
            return jsonify({"response": extract_and_calculate_emi(query), "chatId": chat_id}), 200
        
        # 4) if pdf
        if uploaded_pdf:
             print("uploaded_pdf: ",uploaded_pdf)
             if uploaded_pdf.get("pdf_indexed"):
                print(uploaded_pdf.get("pdf_indexed"))
                namespace = uploaded_pdf["namespace"]
                print("namespace: ",namespace)
                docs = user_vectorstore.similarity_search("", k=10, namespace=namespace)
                # print("docs:", docs)

                # Initialize the chat chain
                chain = get_chat_chain(session_id, user_vectorstore)

                # Inject PDF content into memory
                if docs:
                    pdf_text = "\n".join([doc.page_content for doc in docs])
                    chain.memory.chat_memory.add_message(
                     SystemMessage(content=f"The uploaded PDF is available for reference:\n{pdf_text}")
                    )
                else:
                    # PDF uploaded but not indexed yet
                    return jsonify({
                        "response": "Your PDF is still being processed. Please try again in a few seconds.",
                        "chatId": chat_id
                    }), 200

                # 5) Handle user query with chain
                pdf_answer = chain.invoke({"question": query}).get("answer", "").strip()
                print("PDF answer:", pdf_answer)
                if pdf_answer:
                    response_text = pdf_answer

        # 5) If no PDF or low score → fallback to loan DB 
        if not response_text:
            print("no pdf")
            print("response:", response_text)
            chain = get_chat_chain(session_id, predefined_vectorstore)
            db_answer = chain.invoke({"question": query}).get("answer", "").strip()
            if db_answer:
                response_text = db_answer

        # 6) Final fallback: web search
        # if not response_text:
        #     response_text = web_search(query)

        return jsonify({"response": response_text, "chatId": chat_id}), 200
            
    except Exception as e:
        print("Chat error:", str(e))
        return jsonify({"error": "Failed to process query"}), 500
    