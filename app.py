from langchain.globals import set_verbose

from libs.prompt import create_chain_for_answer_question, get_history_for_template
from libs.streamlit import clear_messages_on_session, draw_chat_history, draw_login_page, draw_logout_button, draw_new_message, create_authentication, get_login_status, init_messages_on_session, is_just_login, receive_user_input, show_error, show_warning
from libs.aws.dynamodb import fetch_chat_history_db, get_session_id, update_history

# LangChainのログ出力設定 デバッグ時はTrue
set_verbose(True)  

# Chainを定義
chain = create_chain_for_answer_question()

# ログイン画面描画
authenticate = create_authentication()
draw_login_page(authenticate)

logined = get_login_status()
if logined is False:
    show_error('Username/password is incorrect')
elif logined is None:
    show_warning('ログインしてください')
else:
    draw_logout_button(authenticate)

    # DynamoDBからメッセージ履歴を取得し、sessionにセット
    if is_just_login():
        clear_messages_on_session()
    session_id = get_session_id()
    message_history_db = fetch_chat_history_db(session_id)
    init_messages_on_session()

    # チャット履歴を画面に描画する
    draw_chat_history(message_history_db)

    # メッセージ履歴をプロンプト内で使える形に整形する
    history_for_template = get_history_for_template(message_history_db)

    # 入力を求める
    if input_text := receive_user_input("質問を入力してください"):
        # 画面にユーザの入力を追加表示する
        draw_new_message("human", input_text)

        # chainを実行し、結果を画面に追加表示する
        result = chain.invoke({"question": input_text, "messages": history_for_template})
        draw_new_message("assistant", result.content)

        # セッションとDBのメッセージ履歴を更新する
        update_history(message_history_db, input_text, result.content)

