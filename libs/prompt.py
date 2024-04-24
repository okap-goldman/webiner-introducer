import streamlit as st
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter

from libs.aws.bedrock import get_llm, get_retriver

def get_prompt_for_extract_keyword():
    """
    ユーザーの入力から、RAGの検索キーワードを考えるためのプロンプトを返す
    """
    return PromptTemplate.from_template("""
        あなたはquestionから、検索ツールへの入力となる検索キーワードを考えます。
        questionに後続処理への指示（例：「説明して」「要約して」）が含まれる場合は取り除きます。
        検索キーワードは文章では無く簡潔な単語で指定します。
        検索キーワードは複数の単語を受け付ける事が出来ます。
        検索キーワードは日本語が標準ですが、ユーザー問い合わせに含まれている英単語はそのまま使用してください。
        回答形式は文字列です。
        <question>{question}</question>
    """)

def get_prompt_for_answer_question():
    """
    ragとメッセージ履歴を元に、チャットに返答する時に使用するプロンプトを返す

    messages: メッセージ履歴
    retrived_context: ragの検索結果
    """
    return ChatPromptTemplate.from_messages(
        [
            SystemMessage("あなたはAIアシスタントです。最後の質問に回答してください。"),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "<retrived_context>{retrived_context}</retrived_context>")
        ]
    )

def get_history_for_template(message_history_db):
    """
    メッセージ履歴をプロンプトに埋め込む形式で取得する
    """
    histories = []
    for message in message_history_db.messages:
        if message.type == "human":
            histories.append(HumanMessage(content=message.content))
        else:
            histories.append(AIMessage(content=message.content))
    return histories

def create_chain():
    """
    Chainを定義する
    """
    llm = get_llm()
    prompt_for_extract_keyword = get_prompt_for_extract_keyword()
    prompt_for_answer_question = get_prompt_for_answer_question()
    retriever = get_retriver()

    return (
        {
            "retrived_context": prompt_for_extract_keyword | llm | StrOutputParser() | retriever,
            "question":  itemgetter("question"),
            "messages": itemgetter("messages")
        }
        | prompt_for_answer_question 
        | llm
    )
