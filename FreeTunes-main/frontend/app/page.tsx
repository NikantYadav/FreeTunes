"use client";
import React, {useState, useEffect, useRef} from "react";
import { motion } from "framer-motion";
import {Zap, Shield, Code, Search } from "lucide-react";
import Link from "next/link";
import ReactAudioPlayer from 'react-h5-audio-player'
import { buttonVariants } from "@/components/ui/button";
import { siteConfig } from "@/config/site";
import Hls from "hls.js"
import 'react-h5-audio-player/lib/styles.css'
import { ArrowLeft, ArrowRight } from "lucide-react";
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";

const MotionLink = motion(Link);

const FeatureCard = ({ feature, icon: Icon, delay }) => (
  <motion.div 
    className="bg-white/5 backdrop-blur-xl rounded-xl p-6 shadow-lg hover:shadow-xl transition-all duration-300 ease-in-out border border-white/10"
    whileHover={{ scale: 1.05, rotateY: 15, borderColor: "rgba(255,255,255,0.2)" }}
    whileTap={{ scale: 0.95 }}
    initial={{ opacity: 0, y: 20 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.5, delay }}
  >
    <Icon className="w-12 h-12 mb-4 text-indigo-400" />
    <h3 className="text-xl font-bold mb-2 text-white">{feature}</h3>
    <p className="text-gray-300">
      Empowering your projects with easyui.pro and design.
    </p>
  </motion.div>
);

export default function IndexPage() {
  const serverURL = process.env.NEXT_PUBLIC_SERVER_URL;
  const wssURL = process.env.NEXT_PUBLIC_WSS_URL
  const router = useRouter();

  const [songName, setSongName] = useState("");
  const [artistName, setArtistName] = useState("");
  const [songData, setSongData] = useState({ name: "", artist: "" });


  const [searchQuery, setSearchQuery] = useState("")
  const [m3u8Url, setM3u8Url] = useState(""); 
  const [isLoading, setIsLoading] = useState(false); 
  const [showPlayer, setShowPlayer] = useState(false);
  const [isPlayerVisible, setIsPlayerVisible] = useState(false)
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  const hlsRef = useRef<Hls | null>(null);
  const socketRef = useRef<WebSocket | null>(null);
  const [isHlsReady, setIsHlsReady] = useState(false);
  const [isUrlavailable, setIsUrlavailable] = useState(false)


  const handleSearch = async () => {
    resetPlayer();
    console.log(songName);

    setIsLoading(true);
    setSearchQuery(`${songName} song`);
  };

  useEffect(() => {
    if (searchQuery) {
      console.log(searchQuery)
        const authToken = Cookies.get('access_token')

        socketRef.current = new WebSocket(`${wssURL}`);


        socketRef.current.onopen = () => {
            console.log("WebSocket connection established");
            socketRef.current?.send(JSON.stringify({ type: 'auth', token: authToken }));
            socketRef.current?.send(searchQuery);  
        };

        socketRef.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            console.log(data);
            

            if (data.artist && data.song) {
                setSongData({
                    name: data.song,
                    artist: data.artist,
                });
                setShowPlayer(true);
            }
            


            if (data.hls !== undefined) {
                if (data.hls) {
                    console.log("HLS stream ready");
                    setM3u8Url(data.file);
                    setIsUrlavailable(true);
                } else {
                    setIsLoading(true)
                    console.log("HLS stream not ready");
                    setM3u8Url("");
                    setIsUrlavailable(false);
                }
            }
        };

        socketRef.current.onerror = (event: Event) => {
            console.error("Websocket error:", event);
        };

        socketRef.current.onclose = () => {
            console.log("WebSocket connection closed");
            setIsLoading(false);
        };

        return () => {
            if (socketRef.current) {
                socketRef.current.close();
            }
        };
    }
  }, [searchQuery]); 

  useEffect(() => {
    if (isUrlavailable && m3u8Url && Hls.isSupported() && audioRef.current) {
        
        const hls = new Hls();
        hlsRef.current = hls; 
        
        const desiredUrl = `${serverURL}/static/${m3u8Url}`;
        console.log("Loading HLS stream from:", desiredUrl);
    
          
        hls.loadSource(desiredUrl);
        hls.attachMedia(audioRef.current);
    
          
        hls.on(Hls.Events.MANIFEST_PARSED, () => {
            console.log("HLS manifest parsed, ready to play.");
            setIsHlsReady(true)
            setIsLoading(false)
        });
    
        
        hls.on(Hls.Events.ERROR, (event, data) => {
          console.error("HLS.js error:", data);
          
          if (typeof data.fatal === 'string' && Object.values(Hls.ErrorTypes).includes(data.fatal)) {
            switch (data.fatal) {
                case Hls.ErrorTypes.NETWORK_ERROR:
                    console.error("Network error while fetching .ts files.");
                    break;
                case Hls.ErrorTypes.MEDIA_ERROR:
                    console.error("Error loading media.");
                    break;
                case Hls.ErrorTypes.OTHER_ERROR:
                    console.error("Other HLS.js error.");
                    break;
                case Hls.ErrorTypes.KEY_SYSTEM_ERROR:
                    console.error("Key system error.");
                    break;
                case Hls.ErrorTypes.MUX_ERROR:
                    console.error("Mux error.");
                    break;
                default:
                    console.error("Unknown fatal error.");
                    break;
            }
        }
      });
    
        return () => {
            hls.destroy();
            hlsRef.current = null 
        };
    } else if (audioRef.current) {
          
          audioRef.current.src = m3u8Url;
          setIsHlsReady(true)
          setIsLoading(false)
    }
  }, [isUrlavailable, m3u8Url]);
    
  const skip = (seconds: number) => {
    if (audioRef.current) {
      audioRef.current.currentTime += seconds;
    }
  };

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      setCurrentTime(audioRef.current.currentTime);
      setDuration(audioRef.current.duration || 0);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds < 10 ? "0" : ""}${seconds}`;
  };

  const togglePlayPause = () => {
    if (!audioRef.current) return;

    if (audioRef.current.paused) {
      audioRef.current.play();
      setIsPlaying(true);
    } else {
      audioRef.current.pause();
      setIsPlaying(false);
    }
  };


  const handleSeek = (e: React.MouseEvent<HTMLDivElement, MouseEvent>) => {
    if (!audioRef.current || duration === 0) return;
  
    const progressBar = e.currentTarget; 
    const rect = progressBar.getBoundingClientRect();
    const clickPosition = e.clientX - rect.left; 
    const newTime = (clickPosition / progressBar.offsetWidth) * duration;
  
    audioRef.current.currentTime = newTime;
    setCurrentTime(newTime);
  };

  const resetPlayer = () => {
    setIsLoading(true)
    console.log('Resetting player...');
    if (audioRef.current) {
        audioRef.current.pause();
        console.log('Audio paused.');
        audioRef.current.src = '';
        audioRef.current.load();
        audioRef.current.currentTime = 0;
        console.log('Audio element reset.');
    }

    if (hlsRef.current) {
        hlsRef.current.destroy();
        console.log('HLS instance destroyed.');
        hlsRef.current = null;
    }

    if (socketRef.current) {
        socketRef.current.close();
        console.log('WebSocket connection closed.');
        socketRef.current = null;
    }

    setCurrentTime(0);
    setDuration(0);
    setIsPlaying(false);
    setM3u8Url('');
    setIsHlsReady(false);
    // setSongData(null);
    setIsUrlavailable(false);
    console.log('State reset complete.');
  };

  const handlePlayClick = () => {
    setIsPlayerVisible(true)
  }

  const Loader = () => (
    <motion.div
      className="flex justify-center items-center"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <motion.div
        className="w-12 h-12 border-4 border-t-transparent border-indigo-500 border-solid rounded-full animate-spin"
        style={{
          borderColor: 'rgba(255, 255, 255, 0.5)',
          borderTopColor: 'rgba(255, 255, 255, 0.8)',
        }}
      />
    </motion.div>
  );

  return (
    <div className="relative min-h-screen overflow-hidden text-white">
      {/* Enhanced background elements */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-1/4 -left-1/4 w-1/2 h-1/2 bg-indigo-700 rounded-full filter blur-[100px] opacity-30 animate-pulse"></div>
        <div className="absolute -bottom-1/4 -right-1/4 w-1/2 h-1/2 bg-purple-700 rounded-full filter blur-[100px] opacity-30 animate-pulse"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-full h-full bg-gradient-to-br from-indigo-500/10 to-purple-500/10 rounded-full filter blur-[100px] animate-spin-slow"></div>
      </div>

      {/* Content */}
      <div className="relative z-10 mt-5 lg:mt-0">
        <section className="container min-h-screen flex flex-col justify-center items-center gap-8 pb-8 pt-6 md:py-10">
          <motion.div 
            className="flex max-w-[980px] flex-col items-center gap-4 text-center"
            initial={{ opacity: 0, y: -50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, ease: "easeOut" }}
          >
            <motion.h1 
              className="text-5xl font-extrabold leading-tight tracking-tighter md:text-7xl bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 via-purple-400 to-pink-400"
              initial={{ scale: 0.9, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.2, ease: "easeOut" }}
            >
              FreeTunes <br></br>
              Pure Music, Zero Interruptions
            </motion.h1>
            <motion.p 
              className="max-w-[700px] text-xl text-gray-500 mt-2 font-normal"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: 0.6 }}
            >
              Listen to your favorite music without any interruptions for completely free
            </motion.p>
          </motion.div>
          
          {/* Search Bar with Search Button */}
          <motion.div 
            className="flex gap-6 mt-8"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
            <div className="relative w-full max-w-lg">
              <input 
                type="text" 
                placeholder="Search for your favorite tunes" 
                value={songName}
                onChange={(e) => setSongName(e.target.value)}
                className="w-full p-4 pl-10 bg-white/10 border border-white/20 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <span className="absolute left-3 top-1/2 transform -translate-y-1/2 text-white">
                <ArrowRight className="ml-2 h-5 w-5" />
              </span>
            </div>
            <button 
              onClick={handleSearch}
              className="flex items-center bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold px-8 py-4 rounded-full hover:scale-105 transition-all"
            >
              <Search className="h-5 w-5" />
            </button>
          </motion.div>

        {showPlayer && songData && (
          <div className="mt-8 w-full max-w-5xl p-6 bg-gray-800 rounded-xl border border-gray-700 shadow-lg">
            <h3 className="text-2xl font-bold">{songData.name}</h3>
            <p className="text-gray-400">{songData.artist}</p>

            <div className="mt-4 flex flex-col items-center">
              <audio
                ref={audioRef}
                onTimeUpdate={handleTimeUpdate}
                src={m3u8Url}
                className="hidden"
                preload="auto"
              />

              {/* Custom Controls */}
              <div className="flex items-center space-x-4">
                <button
                  onClick={() => skip(-5)}
                  className="text-white p-2 rounded-md hover:bg-gray-600"
                >
                  <ArrowLeft className="w-5 h-5"/>
                </button>

                {/* Play Button with Loading Text */}
                <button
                  onClick={togglePlayPause}
                  className="text-white bg-indigo-500 px-6 py-2 rounded-full hover:scale-105 transition-transform"
                  disabled={!isHlsReady} // Disable until HLS is ready
                >
                  {isHlsReady ? (isPlaying ? "Pause" : "Play") : "Loading..."} {/* Show "Loading..." until HLS is ready */}
                </button>

                <button
                  onClick={() => skip(5)}
                  className="text-white p-2 rounded-md hover:bg-gray-600"
                >
                  <ArrowRight className="w-5 h-5" />
                </button>
              </div>

              {/* Progress Bar */}
              <div
                className="mt-4 w-full bg-gray-700 rounded-full h-2 relative"
                onClick={handleSeek}
              >
                <div
                  style={{
                    width: `${(currentTime / duration) * 100 || 0}%`,
                  }}
                  className="bg-indigo-500 h-2 rounded-full"
                ></div>
              </div>

              {/* Time Labels */}
              <div className="mt-2 flex justify-between w-full text-sm text-gray-400">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(duration)}</span>
              </div>
            </div>
          </div>
        )}


        



        {isLoading && !songData && <Loader />}

        {/* Login and Sign Up Buttons */}
        <motion.div 
            className="flex gap-6 mt-8"
            initial={{ opacity: 0, y: 50 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.8 }}
          >
        <div className="flex gap-6 mt-8">
            <button 
              className="flex items-center bg-gradient-to-r from-green-500 to-teal-500 text-white font-semibold px-8 py-4 rounded-full hover:scale-105 transition-all"
              onClick={() => router.push("/login")}            
            >
              Login

            </button>
            <button 
              className="flex items-center bg-gradient-to-r from-indigo-500 to-purple-500 text-white font-semibold px-8 py-4 rounded-full hover:scale-105 transition-all"
              onClick={() => router.push("/signup")}
            >
            
              Sign Up
            </button>
          </div>
          </motion.div>
        </section>
      </div>
    </div>
  );
}

