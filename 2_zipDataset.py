import cv2
import numpy as np
import h5py
import os
import json
from tqdm import tqdm

PATH = "dataset"
SOURCE_JSON_PATH = "dataset/source.json"
SCREENSHOT_PATH = "dataset/origin"

####################################################################################################
# load data
####################################################################################################
# playlist
with open(SOURCE_JSON_PATH, 'r', encoding="utf-8") as f:
    source = json.load(f)

playlist = {}
for key, entries in source.items():
    for video in entries:
        id = video["url"][32:]
        playlist[id] = video
        playlist[id]["key"] = key
        
# origin list
originlist = []
for key in source.keys():
    path = os.path.join(SCREENSHOT_PATH, key)
    for img in os.listdir(path):
        originlist.append({
            "path": os.path.join(path, img),
            "id": img.split("&t=")[0],
            "url": "https://www.youtube.com/watch?v=" + img.split(".jpg")[0]
        })

# configure    
with open("configure.json", 'r', encoding="utf-8") as f:
    config = json.load(f)

####################################################################################################
# reassemble data
####################################################################################################
origin = []
label = {"label": []}
embedding = []

embedding_size = tuple(config["embedding_size"])
source_size = tuple(config["screenshot_size"])

label["skipped"] = []
for video in tqdm(originlist):
    if (playlist.get(video.get("id")) is None): 
        label["skipped"].append(video)
        continue
    
    img = cv2.imread(video["path"])
    img_RGB = cv2.cvtColor(img, cv2.COLOR_BGR2Lab)
    img_resized = cv2.resize(img_RGB, source_size, interpolation=cv2.INTER_AREA)
    img_embedding_map = cv2.resize(img_RGB, embedding_size, interpolation=cv2.INTER_AREA)
    img_embedding_vector = img_embedding_map.flatten()
        
    origin.append(img_resized)
    embedding.append(img_embedding_vector)
    label["label"].append({
        "id": video["id"],
        "url": video["url"],
        "title": playlist[video["id"]]["title"],
        "key": playlist[video["id"]]["key"]
    })

print(f"Skipped: {len(label["skipped"])}")

####################################################################################################
# save
####################################################################################################
origin = np.asarray(origin)
embedding = np.asarray(embedding)
label["origin_shape"] = origin.shape
label["embedding_shape"] = embedding.shape
label["embedding_size"] = embedding_size

h5_path = os.path.join(PATH, "dataset.h5")
json_path = os.path.join(PATH, "dataset.json")

with h5py.File(h5_path, 'w') as f:
    f.create_dataset("origin", data=np.asarray(origin))
    f.create_dataset("embedding", data=np.asarray(embedding))
with open(json_path, 'w', encoding="utf-8") as f:
    json.dump(label, f, indent="\t", ensure_ascii=False)