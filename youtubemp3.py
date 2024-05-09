from pytube import YouTube
from pytube.exceptions import VideoUnavailable
from moviepy.editor import *


#try:
#    yt = YouTube('https://youtu.be/JDjhs9hF9f0?si=1XrgFNYR-iCp_uaG')
#except VideoUnavailable:
#    print("The video is unavailable.")
#    exit()
#streams = yt.streams
#audiostreams = yt.streams.filter(only_audio=True)
#teststream = yt.streams.get_by_itag('140')
#quality = []
#for stream in audiostreams:
#    quality.append(stream.abr)
    
#int_quality = [int(qu[:-4]) for qu in quality]

#best_quality = max(int_quality)
#print(best_quality)

#best_quality_index = int_quality.index(best_quality)

#downloadable_stream = audiostreams[best_quality_index]
#downloadable_stream.download(output_path = 'downloaded/',filename = 'video.mp4', max_retries = 5)


#print('Your video file has been downloaded')

inputfile = '/ownloaded/video.mp4'
outputfile = 'mp3/audio.mp3'

AudioFileClip(inputfile).write_audiofile(outputfile, bitrate='3000k')
