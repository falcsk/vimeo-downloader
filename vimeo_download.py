import vimeo
import requests
import os
import re
import argparse
import csv
from datetime import datetime, timedelta, timezone
import time
import traceback
import sys

class VimeoDownloader:
    def __init__(self, token, key, secret):
        self.client = vimeo.VimeoClient(
            token=token,
            key=key,
            secret=secret,
            timeout=60  # タイムアウトを60秒に増やす
        )
        self.download_folder = "/Volumes/T7/VimeoDownloads"

    def get_video_category(self, video_id):
        try:
            response = self.client.get(f'/videos/{video_id}')
            video_data = response.json()
            if video_data is None:
                print(f"No data returned for video {video_id}")
                return 'Uncategorized'
            category = video_data.get('parent_folder', {}).get('name', 'Uncategorized')
            return category if category else 'Uncategorized'
        except Exception as e:
            print(f"Error getting category for video {video_id}: {str(e)}")
            return 'Uncategorized'

    def update_csv(self, csv_file):
        existing_data = {}
        if os.path.exists(csv_file):
            with open(csv_file, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    existing_data[row['id']] = row

        videos = self.get_all_videos()
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ['id', 'name', 'upload_date', 'duration', 'download_status', 'last_downloaded', 'category']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for video in videos:
                video_id = video['uri'].split('/')[-1]
                category = self.get_video_category(video_id)
                existing_entry = existing_data.get(video_id, {})
                writer.writerow({
                    'id': video_id,
                    'name': video['name'],
                    'upload_date': video['created_time'],
                    'duration': video['duration'],
                    'download_status': existing_entry.get('download_status', 'Not Downloaded'),
                    'last_downloaded': existing_entry.get('last_downloaded', ''),
                    'category': category
                })
        print(f"CSV file updated: {csv_file}")

    def get_all_videos(self):
        videos = []
        page = 1
        per_page = 100
        max_retries = 3
        retry_delay = 5

        while True:
            for attempt in range(max_retries):
                try:
                    response = self.client.get(f'/me/videos?page={page}&per_page={per_page}')
                    data = response.json()
                    if not data or 'data' not in data:
                        print(f"Unexpected API response structure on page {page}")
                        return videos
                    videos.extend(data['data'])
                    if 'paging' not in data or 'next' not in data['paging']:
                        print(f"Retrieved {len(videos)} videos in total")
                        return videos
                    page += 1
                    print(f"Retrieved page {page-1}")
                    time.sleep(1)  # APIリクエスト間に1秒の待機を追加
                    break
                except requests.exceptions.RequestException as e:
                    if attempt < max_retries - 1:
                        print(f"Error occurred on page {page}: {e}. Retrying in {retry_delay} seconds...")
                        time.sleep(retry_delay)
                    else:
                        print(f"Failed to retrieve videos after {max_retries} attempts on page {page}.")
                        return videos
                except Exception as e:
                    print(f"Unexpected error on page {page}: {str(e)}")
                    return videos

    def download_video(self, video_id, output_path, category):
        max_retries = 3
        retry_delay = 5
        for attempt in range(max_retries):
            try:
                video_info = self.client.get(f'/videos/{video_id}').json()
                download_link = self.get_download_link(video_info)
                if download_link:
                    filename = re.sub(r'[\\/*?:"<>|]', "", video_info['name'])
                    filename = filename.replace('/', '_').replace(' ', '_') + '.mp4'
                    
                    category_path = os.path.join(output_path, category)
                    os.makedirs(category_path, exist_ok=True)
                    
                    filepath = os.path.join(category_path, filename)
                    
                    print(f"Downloading: {video_info['name']} to {category_path}")
                    with requests.get(download_link, stream=True) as r:
                        r.raise_for_status()
                        with open(filepath, 'wb') as f:
                            for chunk in r.iter_content(chunk_size=8192):
                                f.write(chunk)
                    
                    print(f"Downloaded: {filename} to {category_path}")
                    return True
                else:
                    print(f"Error: No download link available for video ID {video_id}")
                    return False
            except requests.exceptions.ReadTimeout:
                if attempt < max_retries - 1:
                    print(f"Timeout occurred while downloading video {video_id}. Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"Failed to download video {video_id} after {max_retries} attempts.")
                    return False
            except Exception as e:
                print(f"Error downloading video {video_id}: {str(e)}")
                return False

    def get_download_link(self, video_info):
        if 'download' in video_info:
            download_options = video_info['download']
            if download_options:
                return max(download_options, key=lambda x: x['width'])['link']
        elif 'files' in video_info:
            files = video_info['files']
            if files:
                return max(files, key=lambda x: x.get('width', 0))['link']
        return None

    def rename_video_on_vimeo(self, video_id, new_name):
        try:
            response = self.client.patch(f'/videos/{video_id}', data={
                'name': new_name
            })
            if response.status_code == 200:
                print(f"Successfully renamed video {video_id} to '{new_name}' on Vimeo")
                return True
            else:
                print(f"Failed to rename video {video_id}. Status code: {response.status_code}")
                return False
        except Exception as e:
            print(f"Error renaming video {video_id}: {str(e)}")
            return False

def get_date_input(prompt):
    while True:
        date_str = input(prompt)
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        except ValueError:
            print("Invalid date format. Please use YYYY-MM-DD.")

def update_csv_entry(csv_file, video_id, download_status, last_downloaded, category):
    temp_file = csv_file + '.tmp'
    with open(csv_file, 'r', newline='', encoding='utf-8') as infile, \
         open(temp_file, 'w', newline='', encoding='utf-8') as outfile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames
        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()
        for row in reader:
            if row['id'] == video_id:
                row['download_status'] = download_status
                row['last_downloaded'] = last_downloaded
                row['category'] = category
            writer.writerow(row)
    os.replace(temp_file, csv_file)

def main():
    parser = argparse.ArgumentParser(description="Vimeo video downloader and CSV updater")
    parser.add_argument("--update-csv", action="store_true", help="Update CSV file only")
    parser.add_argument("--download", action="store_true", help="Download videos")
    args = parser.parse_args()

    if not (args.update_csv or args.download):
        parser.error("少なくとも --update-csv か --download のいずれかのオプションを指定してください")

    try:
        downloader = VimeoDownloader(
            token='048f0e6bdc65168e9d451ea8ccaa1fcc',
            key='411ff315d953e74016c8cd39de1dc6f3d17cfb2d',
            secret='o/d//2R2Z49iap5HNpBog5Uh0X8Ib/58MNcCFJCgllrNE0/8OtjykIySlaqt/pwGpDTOoe6Cn2eN0ZwuuBg+YF/QcMi9xavGcqlkEl/mDCIRl41Wu5ql23D+vR18TDOB'
        )
        
        csv_file = "vimeo_allvideos.csv"

        if args.update_csv or not os.path.exists(csv_file):
            downloader.update_csv(csv_file)

        if args.download:
            start_date = get_date_input("Enter start date (YYYY-MM-DD): ")
            end_date = get_date_input("Enter end date (YYYY-MM-DD): ")
            end_date = end_date.replace(hour=23, minute=59, second=59)

            videos_found = False
            download_count = 0
            error_count = 0

            with open(csv_file, "r") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    upload_date = datetime.strptime(row['upload_date'], "%Y-%m-%dT%H:%M:%S%z").replace(tzinfo=timezone.utc)
                    if start_date <= upload_date <= end_date:
                        videos_found = True
                        if row['download_status'] != 'Downloaded':
                            category = row['category'] if row['category'] else 'Uncategorized'
                            if downloader.download_video(row['id'], downloader.download_folder, category):
                                new_name = f"（SSD保存済）{row['name']}"
                                if downloader.rename_video_on_vimeo(row['id'], new_name):
                                    update_csv_entry(csv_file, row['id'], 'Downloaded', datetime.now(timezone.utc).isoformat(), category)
                                    download_count += 1
                            else:
                                error_count += 1
                            time.sleep(1)

            if not videos_found:
                print(f"\n指定された期間 ({start_date.date()} から {end_date.date()}) にビデオが見つかりませんでした。")
            else:
                print(f"\n処理完了:")
                print(f"成功したダウンロード: {download_count}")
                print(f"失敗したダウンロード: {error_count}")

    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()