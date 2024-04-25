import streamlit as st
import streamlit_authenticator as sa

def create_authentication():
    """
    認証情報を設定する
    """
    return sa.Authenticate(
        credentials={
            "usernames":{
                "user1":{"name":"user1","password":"pass"},
                "user2":{"name":"user2","password":"pass"},
                "user3":{"name":"user3","password":"pass"},
                "admin1":{"name":"admin1","password":"pass"}
            }
        },
        cookie_name="streamlit_cookie",
        cookie_key="signature_key",
        cookie_expiry_days=1
    )

def is_admin():
    """
    管理者か判定
    """
    return "admin" in st.session_state["username"]

def draw_login_page(authenticate):
    """
    認証情報を設定し、ログイン画面を表示する
    """
    authenticate.login()

def get_login_status():
    """
    ログインに成功したか判定する
    """
    return st.session_state["authentication_status"]

def is_just_login():
    """
    ログイン直後か判定する
    """
    return "FormSubmitter:Login-Login" in st.session_state

def draw_logout_button(authenticate):
    """
    ログアウトボタンを描画する
    """
    authenticate.logout(location="sidebar")

def show_warning(message):
    """
    警告を表示する
    """
    st.warning(message)

def show_error(message):
    """
    エラーを表示する
    """
    st.error(message)

def clear_messages_on_session():
    """
    セッション上の過去のメッセージをクリアする
    """
    if "messages" in st.session_state:
        st.session_state["messages"].clear()

def init_messages_on_session():
    """
    セッション上の過去のメッセージを初期化
    """
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

def draw_chat_history(message_history_db):
    """
    チャット履歴を描画する
    """
    for message in message_history_db.messages:
        with st.chat_message(message.type):
            st.markdown(message.content)

def draw_new_message(role, content):
    """
    新しいメッセージを描画

    role: "user" | "assistant"
    content: str
    """
    with st.chat_message(role):
        st.write(content)

def receive_user_input(default_text=""):
    """
    ユーザーの入力を受け付ける
    """
    return st.chat_input(default_text)



