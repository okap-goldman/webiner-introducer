# RAG https://qiita.com/cyberBOSE/items/fd65de9f857d36180fa5#retriever%E3%82%B3%E3%83%B3%E3%83%9D%E3%83%BC%E3%83%8D%E3%83%B3%E3%83%88
# https://qiita.com/gudapys/items/62eda02bdb3de5530a23

from langchain.globals import set_debug
set_debug(True) # debug時はTrue
from operator import itemgetter

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_community.chat_message_histories import DynamoDBChatMessageHistory
import boto3
from boto3.session import Session
from langchain_community.chat_models import BedrockChat
import streamlit as st
import streamlit_authenticator as sa
from langchain_core.output_parsers import StrOutputParser
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)

from langchain.globals import set_debug
set_debug(False) # debug時はTrue

from langchain_core.prompts import PromptTemplate
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
from langchain_core.runnables import RunnablePassthrough
from langchain.memory import ConversationBufferMemory

# Get the service resource.
session = Session(profile_name="aicamp")
dynamodb = session.resource("dynamodb")
try:
    # 既存のテーブルを確認
    dynamodb.meta.client.describe_table(TableName="SessionTable")
except dynamodb.meta.client.exceptions.ResourceNotFoundException:
    # テーブルが存在しない場合、新しく作成
    table = dynamodb.create_table(
        TableName="SessionTable",
        KeySchema=[{"AttributeName": "SessionId", "KeyType": "HASH"}],
        AttributeDefinitions=[{"AttributeName": "SessionId", "AttributeType": "S"}],
        BillingMode="PAY_PER_REQUEST",
    )

# Retrieve用のプロンプトの定義
prompt_pre = PromptTemplate.from_template("""
あなたはquestionから、検索ツールへの入力となる検索キーワードを考えます。
questionに後続処理への指示（例：「説明して」「要約して」）が含まれる場合は取り除きます。
検索キーワードは文章では無く簡潔な単語で指定します。
検索キーワードは複数の単語を受け付ける事が出来ます。
検索キーワードは日本語が標準ですが、ユーザー問い合わせに含まれている英単語はそのまま使用してください。
回答形式は文字列です。
<question>{question}</question>
""")

# # プロンプトテンプレートを作成
prompt_main = ChatPromptTemplate.from_messages(
    [
        SystemMessage("あなたはAIアシスタントです。最後の質問に回答してください。"),
        MessagesPlaceholder(variable_name="messages") #ここにDynamoDBから取得した会話履歴を入れる
        # ("human", "<context>{context}</context>")
    ]
)
# prompt_main = PromptTemplate.from_template("""
# あなたはcontextを参考に、questionに回答します。
# <context>{context}</context>
# <question>{question}</question>
# """)

# LLMの定義
bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")
LLM = BedrockChat(
    client=bedrock_runtime,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    model_kwargs={"max_tokens": 1000},
)

# Retriever(KnowledgeBase)の定義
# Knowledge base ID、取得件数、検索方法（ハイブリッド）
retriever = AmazonKnowledgeBasesRetriever(
    credentials_profile_name="aicamp",
    knowledge_base_id="JTX4FB9NF7",
    retrieval_config={
        "vectorSearchConfiguration": {
            "numberOfResults": 10, 
            "overrideSearchType": "HYBRID"
        }
    }
)

# chainの定義
chain = (
    {"context": prompt_pre | LLM | StrOutputParser() | retriever, "question":  itemgetter("question"), "messages": itemgetter("messages")}
    | prompt_main 
    | LLM
)

# 認証情報を定義
authenticator = sa.Authenticate(
    credentials={"usernames":{
        "user1":{"name":"user1","password":"pass"},
        "user2":{"name":"user2","password":"pass"},
        "user3":{"name":"user3","password":"pass"}}},
    cookie_name="streamlit_cookie",
    cookie_key="signature_key",
    cookie_expiry_days=1
)

# ログイン画面描画
authenticator.login()

if st.session_state["authentication_status"] is False: #ログイン失敗
    st.error('Username/password is incorrect')
elif st.session_state["authentication_status"] is None: #未入力
    st.warning('Please enter your username and password')
else: #ログイン成功
   
    authenticator.logout(location="sidebar") #ログアウトボタンをサイドバーに表示

    # ログイン直後っぽい時はセッション上の過去のメッセージをクリアする
    if "FormSubmitter:Login-Login" in st.session_state:
        if "messages" in st.session_state:
            st.session_state["messages"].clear()

    # usernameをDynamoDBのKeyとする
    session_id = st.session_state["username"]

    # DynamoDBの会話履歴（テーブル名"SessionTable"、TTL=3600秒）
    message_history = DynamoDBChatMessageHistory(table_name="SessionTable", session_id=session_id, ttl=3600)

    # 画面描画用のセッション上のチャット履歴を初期化する
    if "messages" not in st.session_state:
        # 辞書形式で定義
        st.session_state["messages"] = []

    # セッションからこれまでのチャット履歴を全て画面に表示する 
    histories = []
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
        if message["role"] == "user":
            histories.append(HumanMessage(content=message["content"]))
        else:
            histories.append(AIMessage(content=message["content"]))
        

    # 入力を求める
    if input_text := st.chat_input("会話しましょう"):

        # 画面にユーザの入力を追加表示する
        with st.chat_message("user"):
            st.write(input_text)

        # chainの実行
        histories.append(HumanMessage(content=input_text))
        result = chain.invoke({"question": input_text, "messages": histories})
        
        # 画面にBedrockの返答を追加表示する 
        with st.chat_message("assistant"):
            st.write(result.content)

        # セッション上のチャット履歴の更新（画面の再描画用）
        st.session_state.messages.append({"role": "user", "content": input_text})
        st.session_state.messages.append({"role": "assistant", "content": result.content})

        # DynamoDBの更新（次回の入力用）
        message_history.add_user_message(input_text)
        message_history.add_ai_message(result.content)