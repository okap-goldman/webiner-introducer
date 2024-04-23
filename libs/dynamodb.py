from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
import streamlit as st

def get_session_id():
    """
    セッションIDを取得
    セッションIDをDynamoDBのキーとして使用する
    """
    return st.session_state["username"]

def fetch_chat_history_db(session_id):
    """
    DynamoDBからメッセージ履歴を取得する

    session_id: セッションID(DBのキーとして使用している)
    """
    return DynamoDBChatMessageHistory(table_name="SessionTable", session_id=session_id, ttl=3600)

def update_history(message_history_db, user_message, ai_message):
    """
    セッション及びDynamoDBのメッセージ履歴を更新する
    """

    # セッション上のチャット履歴の更新（画面の再描画用）
    st.session_state.messages.append({"role": "user", "content": user_message})
    st.session_state.messages.append({"role": "assistant", "content": ai_message})

    # DynamoDBの更新（次回の入力用）
    message_history_db.add_user_message(user_message)
    message_history_db.add_ai_message(ai_message)

