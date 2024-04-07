from boto3.session import Session
from langchain.chat_models import BedrockChat
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)

session = Session(profile_name="aicamp")

bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")

llm = BedrockChat(
    client=bedrock_runtime,
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    model_kwargs={"max_tokens": 500},
)

memory = ConversationBufferMemory(return_messages=True)
prompt = ChatPromptTemplate.from_messages([
    MessagesPlaceholder(variable_name="history"),
    HumanMessagePromptTemplate.from_template("""{input}""")
])

llm_chain = ConversationChain(llm=llm, prompt=prompt, memory=memory)
result = llm_chain.run("オススメのお肉料理を一つ教えてください。")
print(result)


# import os
# import chainlit as cl
# import langchain
# from langchain.chat_models import BedrockChat
# from langchain.chains import ConversationalRetrievalChain
# from langchain.memory import ChatMessageHistory, ConversationBufferMemory
# from langchain.agents import Tool, AgentType, initialize_agent

# import openai
# openai.api_key = os.environ.get("OPENAI_API_KEY")
# langchain.verbose = True

# from llama_index.core import (
#     Settings,
#     StorageContext,
#     VectorStoreIndex,
#     SimpleDirectoryReader,
#     load_index_from_storage,
# )
# from llama_index.llms.openai import OpenAI
# from llama_index.embeddings.openai import OpenAIEmbedding
# from llama_index.core.query_engine.retriever_query_engine import RetrieverQueryEngine
# from llama_index.core.callbacks import CallbackManager
# from llama_index.core.service_context import ServiceContext
# from langchain.chat_models import BedrockChat

# from langchain import OpenAI, SerpAPIWrapper
# from langchain.chains.conversation.memory import ConversationBufferMemory

# aws_region = os.environ["AWS_REGION"]

# try:
#     # rebuild storage context
#     storage_context = StorageContext.from_defaults(persist_dir="./storage")
#     # load index
#     index = load_index_from_storage(storage_context)
# except:
#     documents = SimpleDirectoryReader("./data").load_data(show_progress=True)
#     index = VectorStoreIndex.from_documents(documents)
#     index.storage_context.persist()

# @cl.on_chat_start
# async def main():
#     llm = BedrockChat(
#         model_id="anthropic.claude-v2:1",
#         model_kwargs={
#             "temperature":0,
#             "max_tokens_to_sample":1024
#         }
#     )

#     message_history = ChatMessageHistory()

#     memory = ConversationBufferMemory(
#         memory_key="chat_history",
#         output_key="answer",
#         chat_memory=message_history,
#         return_messages=True,
#     )

#     search = SerpAPIWrapper(serpapi_api_key=os.environ.get("SERPAPI_KEY"))
#     tools = [
#         Tool(
#             name="RAG Search",
#             func=lambda q: str(index.as_query_engine().query(q)),
#             description="Useful for the generating the answers of RAG",
#             return_direct=True,
#         ),
#         Tool(
#             name="Web Search",
#             func=search.run,
#             description="useful for when you need to answer questions about current events",
#         ),
#     ]
    
#     # chain = initialize_agent(
#     #     llm,
#     #     tools,
#     #     chain_type="stuff",
#     #     memory=memory,
#     #     return_source_documents=True,
#     #     verbose=True
#     # )
#     prefix = """Anser the following questions as best you can, but speaking Japanese. You have access to the following tools:"""
#     suffix = """Begin! Remember to speak Japanese when giving your final answer."""

#     agent_chain = initialize_agent(
#         tools,
#         llm,
#         agent=AgentType.CONVERSATIONAL_REACT_DESCRIPTION,
#         memory=memory,
#         prefix=prefix,
#         suffix=suffix,
#         verbose=True,
#     )

#     # Store the chain in the user session
#     cl.user_session.set("chain", agent_chain)

# @cl.on_message
# async def main(message: cl.Message):
#     # Retrieve the chain from the user session
#     chain = cl.user_session.get("chain")

#     # Call the chain asynchronously
#     # res = await chain.acall(
#     #     message.content, 
#     #     callbacks=[cl.AsyncLangchainCallbackHandler()]
#     # )
#     res = chain.run(input= message.content)
#     answer = res["answer"]
#     source_documents = res["source_documents"]  # type: List[Document]

#     text_elements = []  # type: List[cl.Text]

#     if source_documents:
#         for source_idx, source_doc in enumerate(source_documents):
#             source_name = f"source_{source_idx}"
#             # Create the text element referenced in the message
#             text_elements.append(
#                 cl.Text(content=source_doc.page_content, name=source_name)
#             )
#         source_names = [text_el.name for text_el in text_elements]

#         if source_names:
#             answer += f"\nSources: {', '.join(source_names)}"
#         else:
#             answer += "\nNo sources found"

#     await cl.Message(content=answer, elements=text_elements).send()




# openai.api_key = os.environ.get("OPENAI_API_KEY")
# langchain.verbose = True

# agent = None



# @cl.set_chat_profiles
# async def chat_profile():
#     """
#     画面の上部に表示されるモデル一覧を設定する
#     """
    
#     return [
#         cl.ChatProfile(
#             name="gpt-3.5-turbo-16k",
#             markdown_description="The underlying LLM model is **gpt-35-turbo-16k**.",
#             icon="https://www.mlq.ai/content/images/2024/01/ChatGPT-Logo-2.jpg",
#         ),
#         cl.ChatProfile(
#             name="gpt-4-turbo-preview",
#             markdown_description="The underlying LLM model is **gpt-4-turbo-preview**.",
#             icon="https://www.mlq.ai/content/images/2024/01/ChatGPT-Logo-2.jpg",
#         ),
#         cl.ChatProfile(
#             name="bedrock-claude",
#             markdown_description="The underlying LLM model is **Bedrock Claude**.",
#             icon="https://example.com/path/to/bedrock-claude-icon.jpg",
#         ),
#     ]

# @cl.on_chat_start
# async def start():
#     model = cl.user_session.get("chat_profile")
    
#     if model.startswith("gpt"):
#         llm = OpenAI(
#             model=model, temperature=0.1, max_tokens=1024, streaming=True
#         )
#         Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small")
#     elif model == "bedrock-claude":
#         llm = BedrockChat(
#             model_id="anthropic.claude-3-haiku-20240307-v1:0",  # AWS Bedrock Model ID
#             model_kwargs={"temperature": 0.7, "max_tokens": 1024},  # AWS Bedrock Model arguments
#             streaming=True,  # enable response streaming
#             # callbacks=[StreamingStdOutCallbackHandler()],  # response streaming handler
#             verbose=False
#         )
#         # Bedrockに特有のembed_modelやcontext_windowの設定があればここに追加
#     else:
#         raise ValueError("Unsupported model selected.")
    
#     Settings.context_window = 4096

#     service_context = ServiceContext.from_defaults(callback_manager=CallbackManager([cl.LlamaIndexCallbackHandler()]))
#     query_engine = index.as_query_engine(streaming=True, similarity_top_k=2, service_context=service_context)
#     cl.user_session.set("query_engine", query_engine)

#     global agent
#     agent = initialize_agent(
#         llm=llm,
#         tools=tools,
#         gent="zero-shot-react-description",
#         verbose=True,
#     )

#     await cl.Message(
#         author="Assistant", content="Hello! Im an AI assistant. How may I help you?"
#     ).send()

# @cl.on_settings_update
# async def update_settings(settings):
#     cl.user_session.set("llm_parameters",settings)
#     print("on_settings_update", settings)


# @cl.on_message
# async def main(message: cl.Message):
#     msg = cl.Message(content="", author="Assistant")

#     res = await run_agent(message.content)

#     for token in res.response_gen:
#         await msg.stream_token(token)
#     await msg.send()

# def run_agent(input):
#     return agent.run(input=input, handle_parsing_errors=True)