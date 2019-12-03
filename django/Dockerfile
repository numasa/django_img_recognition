# python3.7 on alpine linuxイメージをpull
FROM python:3.7-alpine

# 作業ディレクトリを設定
WORKDIR /usr/src/app

# 環境変数を設定
# Pythonがpyc filesとdiscへ書き込むことを防ぐ
ENV PYTHONDONTWRITEBYTECODE 1
# Pythonが標準入出力をバッファリングすることを防ぐ
ENV PYTHONUNBUFFERED 1
# homeディレクトリを設定
ENV HOME /home/app

# Pipenv/python3-dev他をインストール
RUN pip install --upgrade pip setuptools \
&& pip install pipenv \
&& apk --update-cache add python3-dev gcc g++ libc-dev linux-headers postgresql-dev bash

# ホストのカレントディレクトリ（現在はappディレクトリ）を作業ディレクトリにコピー
COPY . /usr/src/app/

# pipfileからパッケージをインストールしてDjango環境を構築
RUN pipenv install --system
