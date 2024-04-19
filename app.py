from boto3.session import Session
from langchain.chat_models import BedrockChat
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import StrOutputParser
from langchain.schema.runnable import Runnable
from langchain.schema.runnable.config import RunnableConfig
import chainlit as cl

@cl.on_chat_start
async def on_chat_start():
    session = Session(profile_name="aicamp")

    bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")

    model = BedrockChat(
        client=bedrock_runtime,
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        model_kwargs={"max_tokens": 500},
    )

    memory = ConversationBufferMemory(return_messages=True)
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="history"),
        HumanMessagePromptTemplate.from_template("""{input}""")
    ])

    runnable = ConversationChain(llm=model, prompt=prompt, memory=memory)
    cl.user_session.set("runnable", runnable)

@cl.on_message
async def on_message(message: cl.Message):
    runnable = cl.user_session.get("runnable")  # type: Runnable


    result = runnable.run(message.content)
    msg = cl.Message(content=result)

    await msg.send()