import os
import boto3

import logging
logger=logging.getLogger(__name__)

def rekognition(filename):
    '''
    画像認識
    '''
    # webpファイルはrekognition非対応なためjpgに変換
    if ".webp" in filename:
        # jpgパス生成
        convert_filename = filename.rstrip(".webp") + ".jpg"

        # 変換する
        im = Image.open(filename).convert("RGB")
        im.save(convert_filename,"jpeg")

        # filenameに変換済みファイルを指定
        filename = convert_filename

    #boto3のclient作成、rekognitio/translatenとリージョンを指定
    rekognition = boto3.client(
        'rekognition',
        region_name='us-east-2')
    translate   = boto3.client(
        'translate',
        region_name='us-east-2')

    # 画像ファイルを読み込んでバイト列を取得
    with open(filename, 'rb') as source_image:
        source_bytes = source_image.read()

    # rekognitionのdetect_labelsにバイト列を渡してラベル検出実行
    response = rekognition.detect_labels(
                   Image={
                       'Bytes': source_bytes
                   }
    )
    logger.info('rekognition response:' + str(response))

    # responseのName(名前)とConfidence(信頼性)のみに整形
    formatted_response = []
    for label in response['Labels']:
        # translateのtranslate_textにName(名前)を渡して翻訳
        translated_name = translate.translate_text(
                              Text=label['Name'],
                              SourceLanguageCode='en',
                              TargetLanguageCode='ja',
        )
        formatted_response.append([ label['Name'], translated_name['TranslatedText'], label['Confidence'] ])

    return formatted_response