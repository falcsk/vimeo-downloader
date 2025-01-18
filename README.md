# Vimeo Downloader

Vimeoの動画を自動的にダウンロードするPythonスクリプト

## 機能
- 指定した期間の動画を一括ダウンロード
- カテゴリごとにフォルダ分け
- ダウンロード状態の管理
- Vimeo動画一覧の取得とCSV出力

## セットアップ
1. リポジトリをクローン
2. 必要なパッケージをインストール：
   ```bash
   pip install python-vimeo python-dotenv
   ```
3. `.env.example`を`.env`にコピーしてVimeoのAPI情報を設定

## 使い方

### 動画タイトル一覧の取得
```bash
python vimeo_titles.py
```
- Vimeoアカウントの動画一覧を取得
- タイトル情報を表示

### CSVファイルの更新
```bash
python vimeo_download.py --update-csv
```
- 全動画の情報をCSVファイルに出力
- ダウンロード状態も記録

### 動画のダウンロード
```bash
python vimeo_download.py --download
```
実行すると：
1. 開始日と終了日を入力
2. 指定期間の動画を自動ダウンロード
3. カテゴリごとにフォルダに保存
4. ダウンロード完了後、Vimeo上のタイトルを更新（「SSD保存済」を追加）

## ファイル構成
- `vimeo_download.py`: メインのダウンロードスクリプト
- `vimeo_titles.py`: 動画一覧取得スクリプト
- `.env.example`: 環境変数のテンプレート
