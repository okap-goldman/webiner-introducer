from dotenv import dotenv_values

from libs.const import ENV_FILE_NAME

def get_env():
    """
    環境変数を取得する
    """
    return dotenv_values(ENV_FILE_NAME)

