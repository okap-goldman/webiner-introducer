from youtube_transcript_api import YouTubeTranscriptApi
from sentence_transformers import SentenceTransformer
import requests
import json
import os

def get_youtube_transcript(video_id):
    # YouTubeのトランスクリプトを取得
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['ja']).fetch()
        full_text = " ".join([t['text'] for t in transcript])
        return full_text
    except Exception as e:
        print(f"Error fetching transcript: {e}")
        return None

def summarize_text_with_haiku(text):
    # Claude3 Haiku APIを使用してテキストを要約
    # この部分はClaude3 Haiku APIの仕様に基づいて適宜調整してください
    api_url = "https://api.claude3.com/haiku"
    headers = {"Authorization": "Bearer YOUR_API_TOKEN"}
    data = {"text": text}
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()['summary']
    else:
        print(f"Error summarizing text: {response.text}")
        return None

def vectorize_and_save(text, save_path):
    # テキストをベクトル化して保存
    model = SentenceTransformer('all-MiniLM-L6-v2')
    vector = model.encode(text)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    with open(save_path, 'wb') as f:
        f.write(vector.tobytes())

# 使用例
video_id = "YOUR_VIDEO_ID"
transcript = get_youtube_transcript(video_id)
if transcript:
    summary = summarize_text_with_haiku(transcript)
    if summary:
        save_path = "/storage/vectorized_summary.bin"
        vectorize_and_save(summary, save_path)
        print(f"Summary vectorized and saved to {save_path}")