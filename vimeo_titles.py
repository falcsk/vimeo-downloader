import vimeo

   # Vimeo APIの認証情報を設定
client = vimeo.VimeoClient(
	token='3a150e48364a599ba2f9a5f948eb1f2f',
	key='411ff315d953e74016c8cd39de1dc6f3d17cfb2d',
	secret='o/d//2R2Z49iap5HNpBog5Uh0X8Ib/58MNcCFJCgllrNE0/8OtjykIySlaqt/pwGpDTOoe6Cn2eN0ZwuuBg+YF/QcMi9xavGcqlkEl/mDCIRl41Wu5ql23D+vR18TDOB'
   )

   # ユーザーのビデオを取得（最大10個）
response = client.get('/me/videos', params={'per_page': 10})

   # 各ビデオのタイトルを表示
for video in response.json()['data']:
	print(video['name'])