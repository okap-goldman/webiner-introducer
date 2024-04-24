from langchain_community.chat_models import BedrockChat
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever

from libs.aws.session import get_aws_session

def get_llm():
    session = get_aws_session()
    bedrock_runtime = session.client("bedrock-runtime", region_name="us-east-1")
    return BedrockChat(
        client=bedrock_runtime,
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        model_kwargs={"max_tokens": 1000},
    )

def get_retriver():
    # Retriever(KnowledgeBase)の定義
    # Knowledge base ID、取得件数、検索方法（ハイブリッド）
    return AmazonKnowledgeBasesRetriever(
        credentials_profile_name="aicamp",
        knowledge_base_id="JTX4FB9NF7",
        retrieval_config={
            "vectorSearchConfiguration": {
                "numberOfResults": 10, 
                "overrideSearchType": "HYBRID"
            }
        }
    )


