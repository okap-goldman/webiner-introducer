import boto3
import json

from libs.const import S3_BUCKET_NAME

def save_json_to_s3(movie_title, json_data):
    """
    指定したjsonファイルをS3に保存する
    """
    s3 = boto3.resource('s3')
    s3.Bucket(S3_BUCKET_NAME).put_object(Key=f"{movie_title}.json", Body=json.dumps(json_data))

