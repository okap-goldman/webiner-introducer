from boto3.session import Session

def get_aws_session():
    return Session(profile_name="aicamp")