from langchain_aws import ChatBedrock
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever

from libs.aws.session import get_boto3_session
from libs.const import BEDROCK_MODEL_ID
from libs.env import get_env

env = get_env()

def get_llm():
    session = get_boto3_session()
    bedrock_runtime = session.client("bedrock-runtime")
    return ChatBedrock(
        client=bedrock_runtime,
        model_id=BEDROCK_MODEL_ID,
        model_kwargs={"max_tokens": 1000},
    )

def get_retriver():
    # Retriever(KnowledgeBase)の定義
    # Knowledge base ID、取得件数、検索方法（ハイブリッド）
    session = get_boto3_session()
    return AmazonKnowledgeBasesRetriever(
        client = session.client("bedrock-agent-runtime"),
        knowledge_base_id=env["KNOWLEDGE_BASE_ID"],
        retrieval_config={
            "vectorSearchConfiguration": {
                "numberOfResults": 10, 
                "overrideSearchType": "HYBRID"
            }
        }
    )


