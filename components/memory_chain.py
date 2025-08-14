from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.conversation.memory import ConversationBufferMemory
# from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from components.memory import CustomMongoChatMessageHistory
from components.config import MONGO_URI
from components.prompt import loan_prompt

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash")



def get_chat_chain(session_id, vectorstore):
    chat_memory = CustomMongoChatMessageHistory(
        session_id=session_id,
        connection_string=MONGO_URI,
        database_name="assistant",
        collection_name="chats"
    )

    memory = ConversationBufferMemory(
        memory_key="chat_history",
        chat_memory=chat_memory,
        return_messages=True
    )


    return ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vectorstore.as_retriever(
                    search_kwargs={"k": 3},
                    ),
        memory=memory,
        combine_docs_chain_kwargs={"prompt": loan_prompt}
    )
