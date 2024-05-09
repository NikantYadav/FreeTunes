const fs = require('fs');
const ytdl = require('ytdl-core');

const videoURL = 'https://youtu.be/JDjhs9hF9f0?si=1XrgFNYR-iCp_uaG';
const outputFilePath = 'downloaded/video.mp4';

const audio = ytdl(videoURL, { quality: 'highestaudio' })

audio.on('end', () => {
    console.log("Audio has been downloaded completely")
  });
  
  audio.pipe(fs.createWriteStream(outputFilePath));