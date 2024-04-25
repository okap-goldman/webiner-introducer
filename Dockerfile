FROM python:3.9-slim-buster

# パッケージのインストール
WORKDIR /root
COPY requirements.txt /root/
RUN pip install -r requirements.txt

# ローカルマシンのアプリケーションソースをrootにコピー
COPY . /root

# Streamlitのデフォルトポートを開放し、アプリケーションを起動
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]