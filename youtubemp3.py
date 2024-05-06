from pytube import YouTube
from pytube.exceptions import VideoUnavailable

yt = YouTube('https://youtu.be/Lh-YS0IczmM?si=Awg4kLoa6m0we1hO')
streams = yt.streams
audiostreams = yt.streams.filter(only_audio=True)
teststream = yt.streams.get_by_itag('140')
quality = []
for stream in audiostreams:
    quality.append(stream.abr)
    
int_quality = [int(qu[:-4]) for qu in quality]

best_quality = max(int_quality)
print(best_quality)

best_quality_index = int_quality.index(best_quality)

downloadable_stream = audiostreams[best_quality_index]
downloadable_stream.download(output_path = 'C:\\Users\\Nikant Yadav\\Desktop\\Programming\\Anti Spotify App\\downloaded')