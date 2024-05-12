from youtubesearchpython import VideosSearch

item_id = input('song name')

videosSearch = VideosSearch(item_id, limit = 2)
url = videosSearch.result()['result'][0]['title']
print(url)