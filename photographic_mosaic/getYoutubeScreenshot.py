import yt_dlp
from yt_dlp.utils import DownloadError
import cv2
import os
import time

def getYoutubeScreenshot(url, output_dir='', tag='youtube_screenshot', N=10):
    RETRY_ATTEMPTS = 3
    RETRY_DELAY = 0.1 # seconds
    
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]/best[ext=mp4]/best',
        'quiet': True,
        'js_architecture': 'subprocess', # Use subprocess for JS challenges
    }

    info_dict = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
    except DownloadError as e:
        print(f"[yt_dlp] Error processing video info: {url}. Error: {e}. Skipping.")
        return 1
    
    video_url = info_dict.get('url') if info_dict else None
    if not video_url:
         print(f"[yt_dlp] Failed to get video stream URL for: {url}. Skipping.")
         return 1

    duration = info_dict.get('duration')
    video_id = info_dict.get('id')

    if not duration or not video_id:
        print(f"Could not get duration or video ID for {url}. Skipping.")
        return 1

    interval = duration / (N + 1)
    
    cap = cv2.VideoCapture(video_url)

    if not cap.isOpened():
        print(f"Error: Could not open video stream: {url}")
        return 1

    try:
        if not os.path.exists(output_dir) and output_dir:
            os.makedirs(output_dir)

        for i in range(N):
            time_in_seconds = interval * (i + 1)
            cap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)
            
            success = False
            image = None
            for attempt in range(RETRY_ATTEMPTS):
                success, image = cap.read()
                if success:
                    break
                else:
                    time.sleep(RETRY_DELAY)
            
            if success:
                time_label = int(time_in_seconds)
                filename = os.path.join(output_dir, f"{video_id}&t={time_label}.jpg")
                cv2.imwrite(filename, image)
                #print(f"..{i+1}", end='')
            else:
                print(f"Failed to capture frame at {time_in_seconds:.2f}s for video ID {video_id} after {RETRY_ATTEMPTS} attempts.")
                return 1
        #print()
    finally:
        cap.release()
        
    return 0