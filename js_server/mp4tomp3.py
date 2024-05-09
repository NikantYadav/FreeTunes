from moviepy.editor import *

inputfile = 'downloaded/video.mp4'
outputfile = 'mp3/audio.mp3'

AudioFileClip(inputfile).write_audiofile(outputfile, bitrate='3000k')

print('Mp4 converted to Mp3 successfully')