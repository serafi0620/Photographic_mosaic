import photographic_mosaic as pm
import json
from datetime import datetime 
import os
from tqdm import tqdm 

channel = {
    "hane": "https://www.youtube.com/@하네다시보기",
    "onharu": "https://www.youtube.com/@off_haru",
    "kimate": "https://www.youtube.com/@김뒷태의이중생활",
    "otonosori": "https://www.youtube.com/@소리다시보기"
}

SOURCE_JSON_PATH = "dataset/source.json"
SOURCE_PATH = "dataset/origin"

####################################################################################################
# get youtube archive list
####################################################################################################
# load record
with open(SOURCE_JSON_PATH, 'r', encoding='utf-8') as f:
    source = json.load(f)

# get playlist
playlist = {}
for key, url in channel.items():
    lst = pm.getYoutubePlaylist(url)
    playlist[key] = lst
    #print(lst)

# filtering
playlist_filted = {}
for channel, entries in playlist.items():
    mask = [v["url"] for v in source[channel]]  
    playlist_filted[channel] = []
    
    for video in tqdm(entries):
        if video['url'] in mask: 
            continue
        
        print(channel + "  : " + video['url'])
        playlist_filted[channel].append(video) 

####################################################################################################
# download screenshot
####################################################################################################

skipped = 0
for i, (key, value) in enumerate(playlist_filted.items()):
    print(f"steamer: {key} ({i+1}/4) - {len(value)}")

    path = os.path.join(SOURCE_PATH, key)
    for j, video in tqdm(enumerate(value)):
        #print('\r' + f'(skipped: {skipped}) process {j/len(value)*100:.1f}% ({j}/{len(value)}) : {video['url']} : ', end='')
        
        if (pm.getYoutubeScreenshot(video['url'], path) == 1): 
            skipped += 1
            continue

        source[key].append({
            "url": video['url'],
            "title": video['title']
        })
        
        with open(SOURCE_JSON_PATH, 'w', encoding="utf-8") as f:
            json.dump(source, f, indent="\t", ensure_ascii=False)
            
    print(f"skipped: {skipped}")