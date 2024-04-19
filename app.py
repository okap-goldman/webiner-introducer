# -*- coding: utf-8 -*-
import os
import openai
import chainlit as cl

from llama_index.core import (
    Settings,
    StorageContext,
    VectorStoreIndex,
    SimpleDirectoryReader,
    load_index_from_storage,
)
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
from llama_index.core.callbacks import CallbackManager
from llama_index.core.service_context import ServiceContext

import langchain
from langchain import OpenAI, SerpAPIWrapper
from langchain.agents import Tool, initialize_agent
from langchain.chains.conversation.memory import ConversationBufferMemory

langchain.verbose = True
from dotenv import load_dotenv
load_dotenv('.env')

openai.api_key = os.getenv('OPENAI_API_KEY')


@cl.on_chat_start
async def start():
    try:
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir="./storage")
        # load index
        index = load_index_from_storage(storage_context)
    except:
        documents = SimpleDirectoryReader("./data").load_data(show_progress=True)
        index = VectorStoreIndex.from_documents(documents)
        index.storage_context.persist()

    tools = [
        Tool(
            name="Kanmon Tunnel",
            func=lambda q: str(index.as_query_engine().query(q)),
            description="Useful for the generating the answers of Kanmon Tunnel",
            return_direct=True,
        )
    ]

    agent = initialize_agent(
        tools,
        llm=OpenAI(temperature=0),
        gent="zero-shot-react-description",
        verbose=True,
    )
    cl.user_session.set("query_engine", agent)

    await cl.Message(
        author="Assistant", content="Hello! Im an AI assistant. How may I help you?"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    query_engine = cl.user_session.get("query_engine") # type: RetrieverQueryEngine

    res = query_engine.run(input=message.content)
    msg = cl.Message(content=res, author="Assistant")

    await msg.send()
