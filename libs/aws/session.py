from boto3.session import Session

from libs.env import get_env

env = get_env()

def get_boto3_session():
    return Session(profile_name=env["AWS_PROFILE_NAME"])

