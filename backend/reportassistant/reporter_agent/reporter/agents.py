from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

from common.ai.model import get_llm_model


def create_history_summarizer():
    contextualize_q_system_prompt = """
        Given a chat history and the latest user question which might reference context in the chat history, 
        formulate a standalone question which can be understood without the chat history. Do NOT answer the question, 
        just reformulate it if needed and otherwise return it as is."""

    contextualize_q_human_prompt = """ 
    Question: {question}
    
    (Reminder Do NOT answer the question, just reformulate it if needed and otherwise return it as is.)
    
    """
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", contextualize_q_human_prompt),
        ]
    )

    return contextualize_q_prompt | get_llm_model() | StrOutputParser()