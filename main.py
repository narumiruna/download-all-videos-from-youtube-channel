import os
from itertools import count

import click
import googleapiclient.discovery
import yt_dlp
from googleapiclient.http import HttpRequest
from loguru import logger
from tqdm import tqdm

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'


class YouTubeService:

    def __init__(self, api_key):
        self.service = googleapiclient.discovery.build('youtube', 'v3', developerKey=api_key)

    def list_items(self, channel_id: str):
        page_token = None
        for _ in tqdm(count()):
            req: HttpRequest = self.service.search().list(part='snippet,id',
                                                          channelId=channel_id,
                                                          order='date',
                                                          maxResults=50,
                                                          pageToken=page_token)
            resp: dict = req.execute()

            for item in resp['items']:
                yield item

            page_token = resp.get('nextPageToken')
            if page_token is None:
                break


@click.command()
@click.argument('channel-id')
@click.option('-o', '--output-dir', type=click.STRING, default='outputs')
@click.option('-c', '--cookies-from-browser', type=click.STRING, default='chrome')
@click.option('-f', '--format', type=click.STRING, default='bv*+ba/b')
@click.option('-d', '--download', is_flag=True)
def main(channel_id, output_dir, cookies_from_browser, format, download):
    api_key = os.environ.get('YOUTUBE_API_KEY')
    service = YouTubeService(api_key)

    videos = []
    for item in service.list_items(channel_id):
        video_id = item['id'].get('videoId')
        if video_id is None:
            continue
        videos.append(video_id)
    logger.info('found {} videos', len(videos))

    f = os.path.join(output_dir, 'videos.txt')
    with open(f, 'w') as fp:
        logger.info('save video IDs to {}', f)
        fp.write('\n'.join(videos))

    ydl_opts = {
        'cookiesfrombrowser': (cookies_from_browser,),
        'outtmpl': f'{output_dir}/%(title)s.f%(format_id)s.%(ext)s',
        'format': format,
    }

    if download:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            for video in tqdm(videos):
                ydl.download(video)


if __name__ == '__main__':
    main()
