import yt_dlp
from datetime import datetime 


def getYoutubePlaylist(channel_url):
    ydl_opts = {
        'quiet': True,
        'extract_flat': True
    }

    video_list = []

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(channel_url, download=False)
        except Exception as e:
            print(f"Error fetching channel info: {e}")
            return []

        # 채널 내 모든 항목 탐색
        if 'entries' not in info:
            print("No videos found in channel.")
            return []
        
        videos = []
        for ctg in info['entries']:
            if (ctg.get("entries") is None):
                videos.append(ctg)
            else:
                if ("short" in ctg.get("webpage_url")): continue
                videos.extend(ctg.get("entries"))
        
        pass
        for video in videos:
            video_list.append({
                'url': video.get('url'),
                'title': video.get('title')
            })

    return video_list
