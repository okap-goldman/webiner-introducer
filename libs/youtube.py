from langchain_community.document_loaders import YoutubeLoader

def fetch_movie_info(youtube_url):
    loader = YoutubeLoader.from_youtube_url(
        youtube_url,          # 取得したいYouTube URL
        add_video_info=True, # 動画情報を取得する場合はTrue
        language=["ja"],      # 取得する字幕の言語指定(複数指定は取得の優先順位づけ)
    )
    documents = loader.load()
    return {
        "url": youtube_url,
        "publish_date": documents[0].metadata["publish_date"],
        "title": documents[0].metadata["title"],
        "transcript": documents[0].page_content
    }

