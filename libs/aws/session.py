from boto3.session import Session

from libs.env import get_env

env = get_env()

def get_boto3_session():
    return Session(
        aws_access_key_id=env["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=env["AWS_SECRET_ACCESS_KEY"],
        region_name=env["AWS_REGION"]
    )

