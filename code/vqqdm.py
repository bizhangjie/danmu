import requests
import json
import re
from bs4 import BeautifulSoup
import os

class VideoBarrageDownloader:
    def __init__(self, pid, interval=30):
        self.pid = pid
        self.interval = interval

    def get_url(self, start_time=0, end_time=None):
        if end_time is None:
            end_time = start_time + self.interval
        return f'https://dm.video.qq.com/barrage/segment/{self.pid}/t/v1/{start_time * 1000}/{end_time * 1000}'

    def get_content(self, url):
        resp = requests.get(url)
        return resp
    
    def get_filepath(self, url):
        data = self.get_content(url)
        soup = BeautifulSoup(data.text)
        return soup.title.text.split('_')[0]
        
    def parse_content(self, text):
        data = json.loads(text)
        contents = []
        for item in data.get('barrage_list'):
            contents.append(item.get('content'))
        return contents

    def download_barrage(self, start_time=0):
        end_time = start_time + self.interval
        url = self.get_url(start_time, end_time)
        response = self.get_content(url)
        if response.status_code == 200:
            return self.parse_content(response.text)
        else:
            return None

    def save_to_file(self, filepath, barrage_data, start_time, end_time):
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        filename = f'{filepath}/{self.pid}_{start_time}-{end_time}_弹幕数据.txt'
        with open(filename, 'w', encoding='utf-8') as file:
            for content in barrage_data:
                file.write(content + '\n')
        return filename

    @staticmethod
    def extract_video_id_from_url(url):
        video_id_match = re.search(r'\/(\w+)\.html', url)
        if video_id_match:
            video_id = video_id_match.group(1)
            return video_id
        else:
            return None

    @staticmethod
    def download_video_barrages(url, interval=30):
        video_id = VideoBarrageDownloader.extract_video_id_from_url(url)

        if video_id:
            barrage_downloader = VideoBarrageDownloader(video_id, interval)
            filepath = barrage_downloader.get_filepath(url)
            
            start_time = 0
            end_time = 30
            
            while True:
                barrage_data = barrage_downloader.download_barrage(start_time)
                if barrage_data:
                    saved_filename = barrage_downloader.save_to_file(filepath, barrage_data, start_time, end_time)
                    print(f"弹幕数据已保存至文件：{saved_filename}")
                    
                    start_time = end_time
                    end_time += interval
                else:
                    print("无法下载更多弹幕数据，可能已经没有弹幕或请求出错。")
                    break
        else:
            print("无法提取视频ID。")

if __name__ == "__main__":
    # 使用示例
    url = 'https://v.qq.com/x/cover/mzc00200q4ma7wx/s0046dv0qm3.html'
    VideoBarrageDownloader.download_video_barrages(url, interval=30)
