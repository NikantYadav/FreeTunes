from youtubesearchpython import VideosSearch
videosSearch = VideosSearch('NoCopyrightSounds', limit = 2)

url = videosSearch.result()['result'][0]['link']