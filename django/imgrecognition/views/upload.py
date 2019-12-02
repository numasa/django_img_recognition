from django.shortcuts import render
from django.shortcuts import redirect

from imgrecognition.forms import ImageUploadForm
from imgrecognition.views.rekognition import rekognition

def upload(request):
    '''
    画像アップロード
    '''
    display = None
    result = None
    form = ImageUploadForm()

    if request.method == 'POST':
        # formにリクエストを設定
        form = ImageUploadForm(request.POST, request.FILES)

        # formを保存
        url = form.upload()

        # 「?id=XX」をつけてリダイレクト
        response = redirect('imgrecognition:upload')
        response['location'] += '?url=' + str(url)
    else:
        # 「?id=XX」がある場合
        if 'url' in request.GET:
            # imageファイルパスを取得
            display = request.GET['url']
            origin = display.lstrip('/')

            # 画像認識
            result = rekognition(origin)

        context = {
            'display': display,
            'result': result,
            'form': form,
        }
        response = render(request, 'imgrecognition/upload.html', context)

    return response