from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain_core.output_parsers import StrOutputParser
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from operator import itemgetter

from libs.aws.bedrock import get_llm, get_retriver

def get_prompt_for_summarize_transcript():
    """
    ウェビナーの文字起こしを要約してJSONにするプロンプト
    """
    return PromptTemplate.from_template(
"""次の文章はウェビナーの文字起こしです。
要点をまとめて、下記のフォーマットで出力してください。

# 出力形式                        
{
    "title":{title},
    "url":{url},
    "publish_date":{publish_date},
    "summary": {
    - [1つめの要約]
    - [2つめの要約]                                              
    }
}
                                
# 文字起こし文章
<transcript>{transcript}</transcript>
    """
)

def generate_output_parser_for_summarize_transcript():
    """
    文字起こし要約用のParserを生成
    """
    # 応答の型を定義する
    response_schemas = [
        ResponseSchema(name="title", description="動画タイトル"),
        ResponseSchema(name="url", description="動画URL"),
        ResponseSchema(name="publish_date", description="動画公開日"),
        ResponseSchema(name="summary", description="要約")
    ]
    return StructuredOutputParser.from_response_schemas(response_schemas)

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
            SystemMessage("あなたはAIアシスタントです。最後の質問に回答してください。回答には参照元の動画のタイトルとURLも記述してください"),
            MessagesPlaceholder(variable_name="messages"),
            ("human", "{question} <retrived_context>{retrived_context}</retrived_context>")
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

def create_chain_for_summarize_transcript():
    """
    文字起こし要約用のChainを定義する
    """
    llm = get_llm()
    prompt_for_summarize_transcript = get_prompt_for_summarize_transcript()
    # json_parser = generate_output_parser_for_summarize_transcript()
    json_parser = StrOutputParser()
    
    return prompt_for_summarize_transcript.format() | llm | json_parser

def create_chain_for_answer_question():
    """
    ユーザー質問回答用のChainを定義する
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
