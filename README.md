# Vimeo Downloader

Vimeoの動画を自動的にダウンロードするPythonスクリプト

## 機能
- 指定した期間の動画を一括ダウンロード
- カテゴリごとにフォルダ分け
- ダウンロード状態の管理

## セットアップ
1. リポジトリをクローン
2. 必要なパッケージをインストール：
   ```bash
   pip install python-vimeo python-dotenv
   ```
3. `.env.example`を`.env`にコピーしてVimeoのAPI情報を設定

## 使い方

### CSVファイルの更新のみ
```bash
python vimeo_download.py --update-csv
```

### 動画のダウンロード
```bash
python vimeo_download.py --download
```
実行すると：
1. 開始日と終了日を入力
2. 指定期間の動画を自動ダウンロード
3. カテゴリごとにフォルダに保存
```
