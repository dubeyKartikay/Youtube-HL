from pprint import pprint
from flask import Flask
from flask import render_template
from flask import request
import requests
import random
import json


def getChannels():
    file = open("channels.txt","r")
    channels = [ line.strip() for line in file.readlines() ] 
    file.close()
    return channels


def fetchVideosByChannelID(Id):
    params = {"order":"viewCount","part":"snippet","channelId":Id,"maxResults":"50","key":API_KEY}
    res = requests.get("https://www.googleapis.com/youtube/v3/search",params=params)
    if res.status_code != 200:
        print("Someting Went Wrong!!")
        print(res.json())
        return res.status_code
    data = res.json()
    videos = []
    for item in data["items"]:
        if item["id"]["kind"] == "youtube#video":
            video = item["id"]["videoId"]
            videos.append(video)
    return videos


def parseDuration(s):
    duration_str =""
    iso816 = s.split("T")
    if "D" in iso816[0] :

        duration_str += f"{iso816[0][1:]} Days"
    if "H" in iso816[1]:
        duration_str+= iso816[1].split("H")[0] + " : "
        iso816[1] = iso816[1].split("H")[1]
    if "M" in iso816[1]:
        print(iso816 , "minute")
        duration_str+= iso816[1].split("M")[0] +" : "
        iso816[1] = iso816[1].split("M")[1]
    if "S" in iso816[1]:
        print(iso816)
        duration_str+= iso816[1].split("S")[0] 
        iso816 = iso816[1].split("S")[1]
    
    return duration_str



def fetchVideoMetadata(VideoID):
    params = {"part":"snippet,contentDetails,statistics","id":VideoID,"key":API_KEY}
    res = requests.get("https://www.googleapis.com/youtube/v3/videos",params=params)
    if res.status_code != 200:
        print("Someting Went Wrong!!")
        pprint(res.json())
        return -1
    data = res.json()
    video = {}
    video["id"] = data["items"][0]["id"]
    video["title"] = data["items"][0]["snippet"]["title"]
    try:
        video["thumbnail"] = data["items"][0]["snippet"]["thumbnails"]["high"]
    except:
        video["thumbnail"] = data["items"][0]["snippet"]["thumbnails"]["default"]
    video["duration"] = parseDuration(data["items"][0]["contentDetails"]["duration"])
    video["views"] = data["items"][0]["statistics"]["viewCount"]

    return video

def getVideoIdsAndDumptoJSON(AllChannels):
    videosDict = {}
    for channel in AllChannels:
        videosDict[channel] = fetchVideosByChannelID(channel)
    file = open("Videos.json","w")
    json.dump(videosDict,file)
    file.close()

def checkWinner(selectedVideo,VideoIds):
    winner = fetchVideoMetadata(selectedVideo)

    for videoId in VideoIds:
        videoData = fetchVideoMetadata(videoId)
        if videoId["views"] > winner["views"]:
            winner = videoId
    
    if winner == selectedVideo:
        return True
    return False

def newTurn(AllChannels):
    
    file = open("Videos.json","r")
    videosDict = json.load(file)
    file.close()

    currentOptions = random.sample(list(videosDict.keys()),2)
    video1 = fetchVideoMetadata( random.sample(videosDict[currentOptions[0]],1) )
    video2 = fetchVideoMetadata( random.sample(videosDict[currentOptions[1]],1) )

    return [video1,video2]


file = open("key.txt","r")
API_KEY = file.read().strip()
file.close()
AllChannels = getChannels()
app = Flask(__name__)

@app.route("/")
def hello_world():
    selectedVideos =  newTurn(AllChannels)
    return render_template("index.HTML",videos = selectedVideos)

