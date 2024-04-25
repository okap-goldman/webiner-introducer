import sys

from libs.prompt import create_chain_for_summarize_transcript
from libs.youtube import fetch_movie_info

def main(url):
    try:
        movie_info = fetch_movie_info(url)
        print(movie_info)
        chain = create_chain_for_summarize_transcript()
        result = chain.invoke({
            # "url": movie_info["url"],
            # "title": movie_info["title"],
            # "publish_date": movie_info["publish_date"],
            "transcript": movie_info["transcript"]
        })
        print(result)
    except Exception as e:
        print(f"エラーが発生しました: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("URLをコマンドライン引数として提供してください。")
    else:
        main(sys.argv[1])
