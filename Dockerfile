# Pythonの公式イメージをベースにする
FROM python:3.9-slim-buster

# 作業ディレクトリを設定
WORKDIR /root

# requirements.txtをコンテナ内にコピー
COPY requirements.txt /root/

# requirements.txtに記載されたパッケージをインストール
RUN pip install -r requirements.txt

# アプリケーションのソースコードをコンテナ内にコピー
COPY . /root

# Streamlitのデフォルトポートを公開
EXPOSE 8501

# Streamlitアプリケーションを起動
CMD ["streamlit", "run", "app.py"]