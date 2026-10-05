import requests
import json
import os
from dotenv import load_dotenv
from datetime import date


load_dotenv(dotenv_path="./.env")
API_KEY = os.getenv("API_KEY")
CHANNEL_HENDLER = "MrBeast"
maxResult = 50



def get_playlist_id():
    try:
        url = f"https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HENDLER}&key={API_KEY}"
        respone = requests.get(url)
        respone.raise_for_status()
        data = respone.json()
        #print(json.dumps(data,indent=4))
        #print(type(data))
        #print(data["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"])
        channel_items  = data["items"][0]
        channel_playlistid = channel_items["contentDetails"]["relatedPlaylists"]["uploads"]
        #print(channel_playlistid)
        return channel_playlistid 
    except requests.exceptions.RequestException as e:
        raise e

#base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResult}&playlistId=UUX6OQ3DkcsbYNE6H8uQQuVA&key={API_KEY}"

#base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResult}&playlistId={playlistId}&key={API_KEY}"


def get_video_ids(playlistId):
    video_ids =[]
    pageToken = None
    base_url = f"https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={maxResult}&playlistId={playlistId}&key={API_KEY}"

    try:
        while True:
            url = base_url
            if pageToken:
                url+= f"&pageToken={pageToken}"
            
            respone = requests.get(url)
            respone.raise_for_status()
            data = respone.json()

            for item in data.get('items',[]):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)

            pageToken = data.get('nextPageToken')

            if not pageToken:
                break
        return video_ids

    except requests.exceptions.RequestException as e:
        raise e
        
def extract_video_data(video_ids):
    extracted_data = []
    def batch_list(video_id_list,batch_size):
        for video_id in range(0,len(video_id_list),batch_size):
            yield video_id_list[video_id : video_id+batch_size]
    try:
        for batch in batch_list(video_ids,maxResult):
            video_ids_str = ','.join(batch)
            url = f"https://youtube.googleapis.com/youtube/v3/videos?part=contentDetails&part=snippet&part=statistics&id={video_ids_str}&key={API_KEY}"  
            respone = requests.get(url)
            respone.raise_for_status()
            data = respone.json()

            for item in data.get('items',[]):
                video_id = item['id']
                snippet = item['snippet']
                contentDetails = item['contentDetails']
                statistics = item["statistics"]
                video_data = {
                    "video_id": video_id,
                    "title": snippet["title"],
                    "publishedAt": snippet["publishedAt"],
                    "duration": contentDetails["duration"],
                    "viewCount": statistics.get("viewCount", None),
                    "likeCount": statistics.get("likeCount", None),
                    "commentCount": statistics.get("commentCount", None),
                }
                extracted_data.append(video_data)
        return extracted_data

    except requests.exceptions.RequestException as e:
        raise e

def save_to_json(extracted_data):
    file_path = f"./data/YT_data_{date.today()}.json"

    with open(file_path,'w',encoding='utf-8') as json_outfile:
        json.dump(extracted_data,json_outfile,indent=4,ensure_ascii=False)


if __name__ == '__main__':
    playlistId = get_playlist_id()
    video_ids = get_video_ids(playlistId)
    extrct_data = extract_video_data(video_ids)
    save_to_json(extrct_data)