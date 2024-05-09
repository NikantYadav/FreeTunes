const fs = require('fs');
const ytdl = require('ytdl-core');

const videoURL = prompt("Input the video URL");
const outputFilePath = 'downloaded/video.mp4';

const audio = ytdl(videoURL, { quality: 'highestaudio' })