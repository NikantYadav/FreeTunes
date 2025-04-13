"use client";
import { ArrowLeft, ArrowRight, Music, Play, Pause, Search } from "lucide-react";
import { motion } from "framer-motion";
import React, { useState, useEffect, useRef } from "react";
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import Cookies from "js-cookie";
import { useRouter } from "next/navigation";
import Link from "next/link";
import ReactAudioPlayer from 'react-h5-audio-player';
import { FaPlay, FaPause, FaArrowLeft, FaArrowRight, FaHeart, FaPlus, FaMusic } from 'react-icons/fa';
import { MdMusicNote } from 'react-icons/md';
// Removed HLS import because we are not using HLS streaming now
// import Hls from "hls.js";
import PlusPopup from "@/components/popupCard";
import { fetchPlaylistNames } from "@/components/utils/popupCardFunctions";
import Sidebar from "@/components/sidebar";
import { SidebarItem } from "@/components/sidebar";
import SidebarExpanded, { SidebarExpandedItem } from "@/components/sidebarExpanded";

const Dashboard = () => {

  interface Playlist {
    name: string;
    songCount: string; 
  }

  const serverURL = process.env.NEXT_PUBLIC_SERVER_URL;
  const wssURL = process.env.NEXT_PUBLIC_WSS_URL;

  const router = useRouter();
  const [musicRecommendations, setMusicRecommendations] = useState([]);
  const [selectedTrack, setSelectedTrack] = useState(null);
  const [accessToken, setAccessToken] = useState("");
  const [songName, setSongName] = useState("");
  const [artistName, setArtistName] = useState("");
  const [songData, setSongData] = useState({ name: "", artist: "" });

  const [history, setHistory] = useState([]);
  const [searchQuery, setSearchQuery] = useState("");
  const [m3u8Url, setM3u8Url] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [showPlayer, setShowPlayer] = useState(false);
  const [isPlayerVisible, setIsPlayerVisible] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);
  // Removed HLS ref and ready flag since we are not using HLS
  // const hlsRef = useRef<Hls | null>(null);
  // const [isHlsReady, setIsHlsReady] = useState(false);
  const socketRef = useRef<WebSocket | null>(null);
  const [isLiked, setIsLiked] = useState(false);

  const [isPopupVisible, setIsPopupVisible] = useState(false);
  const [playlistNames, setPlaylistNames] = useState<string[] | null>(null);
  const [selectedPlaylist, setSelectedPlaylist] = useState(null);
  const [playlist, setPlaylist] = useState([]);
  const [isMainContent, setIsMainContent] = useState(true);

  const [wsStatus, setWsStatus] = useState<'connecting'|'open'|'closed'>('closed');

  const fetchPlaylists = async () => {
    try {
      const token = Cookies.get("access_token");
      const response = await fetch(`${serverURL}/model/playlist`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "authorization": token } : {}),
        },
      });

      if (response.ok) {
        const data = await response.json();
        const playlists = data
          .filter((playlist) => !playlist.liked)
          .map((playlist) => ({
            name: playlist.name,
            songCount: playlist.songs.length,
          }));
        setPlaylist(playlists);
      } else {
        throw new Error("Failed to fetch playlists");
      }
    } catch (error) {
      console.error("Error fetching playlists:", error);
    }
  };
  
  const handlePlus = async () => {
    setIsPopupVisible(true);
    const token = Cookies.get("access_token");
    if (token) {
      const { selectedPlaylists, unselectedPlaylists } = await fetchPlaylistNames(token, songData.name, songData.artist);
      const combinedPlaylists = [...selectedPlaylists, ...unselectedPlaylists];
      setPlaylistNames(combinedPlaylists);
    }
  };

  const handlePopupClose = () => {
    setIsPopupVisible(false);
  };

  const handlePlaylistSelect = async (nameplaylist: string) => {
    setIsMainContent(false);
    console.log(nameplaylist);

    const token = Cookies.get("access_token");
    const userString = localStorage.getItem("user");
    const user = userString ? JSON.parse(userString) : null;
    const userID = user?.id;

    try {
      const response = await fetch(`${serverURL}/model/gets/playlist`,{
        method: "POST", 
        headers: {
          "Content-Type" : "application/json",
          ...(token ? { "authorization": token } : {}),
        },
        body: JSON.stringify({
          playlistName : nameplaylist,
          userID : userID,
        }),
      });

      if(response.ok){
        const data = await response.json();
        setSelectedPlaylist(data);
      } else {
        throw new Error("Failed to fetch playlists");
      }
      
    } catch(error){
      console.log(error);
      toast.error("Failed to fetch Playlist");
    }
  };

  const handleBackToMain = () => {
    setSelectedPlaylist(null);
    setIsMainContent(true); 
  };

  const createPlaylist = async (playlistName: string, songName: string, artistName: string) => {
    console.log(`Create Playlist: ${playlistName}`);
    const token = Cookies.get("access_token");
    console.log(token);
    const userString = localStorage.getItem("user");
    const user = userString ? JSON.parse(userString) : null;

    try {
      const response = await fetch(`${serverURL}/model/create/playlist`, {
        method: "POST", 
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "authorization": token } : {}),
        },
        body: JSON.stringify({
          name: playlistName, 
          userID: user?.id,  
          songs: [{
            songName: songName,
            artistName: artistName
          }],
          liked: false
        }),
      });
  
      if (response.ok) {
        const data = await response.json();
        console.log("Playlist created successfully", data);
        const { selectedPlaylists, unselectedPlaylists } = await fetchPlaylistNames(
          token as string,
          songData.name as string,  
          songData.artist as string 
        );
        const combinedPlaylists = [...selectedPlaylists, ...unselectedPlaylists];
        setPlaylistNames(combinedPlaylists);
        console.log(combinedPlaylists);
        return data;
      } else {
        const errorData = await response.json();
        console.error("Failed to create playlist", errorData);
        throw new Error(errorData.message || "Failed to create playlist");
      }
    } catch (error) {
      console.error("Error creating playlist:", error);
      toast.error("Failed to create playlist.");
    }
  };
  
  const verifyToken = async (token) => {
    try {
      const response = await fetch(`${serverURL}/model/verify/token`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ access_token: token })
      });

      const data = await response.json();

      if (response.ok && data.auth) {
        localStorage.setItem("user", JSON.stringify(data.user));
        setAccessToken(token);
        console.log(token);
        // Optionally, call fetchMusicRecommendations() or fetchPlaylists()
      } else {
        router.push("/login");
      }
    } catch {
      // Handle error
    }
  };

  useEffect(() => {
    const token = Cookies.get("access_token");
    verifyToken(token); 
    fetchHistory();
  }, []);

  const fetchMusicRecommendations = async () => {
    const token = Cookies.get("access_token");
    try {
      const response = await fetch(`${serverURL}/model/recommendations`, {
        method: "GET",
        headers: {
          ...(token ? { "authorization": token } : {}),
          "Content-Type": "application/json",
        },
      });
      if (response.ok) {
        const data = await response.json();
        setMusicRecommendations(data.recommendations);
      } else {
        //toast.error("Failed to fetch music recommendations.");
      }
    } catch (error) {
      //toast.error("Error fetching recommendations.");
    }
  };

  const fetchHistory = async () => {
    const token = Cookies.get("access_token");
    if (!token) {
      console.error("No access token found.");
      return;
    }
  
    try {
      const response = await fetch(`${serverURL}/model/get/history`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": token } : {}),
        },
      });
  
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || "Failed to fetch history.");
      }
  
      let data = await response.json();
      
      const uniqueData = data.filter((item, index, self) =>
        index === self.findIndex(
          (otherItem) =>
            otherItem.songName === item.songName &&
            otherItem.artistName === item.artistName
        )
      );

      const topThree = uniqueData.slice(-3);
      
      setHistory(topThree); 
    } catch (error) {
      console.error("Error fetching history:", error.message);
    }
  };
  
  const updateSongHistory = async (songName: string, songArtist: string) => {
    try {
      const token = Cookies.get("access_token");
      const payload = {
        songName: songName,
        artistName: songArtist
      };
      
      console.log('Sending request with payload:', payload); 
      
      const response = await fetch(`${serverURL}/model/update/history`, {
        method: "PUT", 
        headers: {
          "Content-Type" : "application/json",
          ...(token ? { "authorization": token } : {}),
        },
        body : JSON.stringify(payload),
      });

      if(response.ok){
        const updatedUser = await response.json();
      } else {
        console.error("Failed to update song history");
      } 
    } catch(error){
      console.error("Error updating song history", error);
    }
  };

  const handleSearch = async () => {
    resetPlayer();
    console.log(songName);
    setSearchQuery(`${songName} ${artistName} song`);
    setIsLoading(true);
  };

  // ---------------------------
  // Song Playback without HLS
  // ---------------------------
  // Removed all WebSocket/HLS related useEffects and functions.
  // Instead, when a song is searched, we simply fetch from the /mp3 endpoint and update the audio source.
  useEffect(() => {
    if (searchQuery) {
      console.log("Initiating search for:", searchQuery);
      const fetchAudio = async () => {
        const authToken = Cookies.get('access_token');
        setIsLoading(true);
        try {
          const response = await fetch(`${serverURL}/mp3`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              token: authToken,
              search_query: searchQuery
            })
          });

          if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
          }

          const data = await response.json();

          if (data.artist && data.song && data.file) {
            setSongData({
              name: data.song,
              artist: data.artist,
              id: data.id,
              streamURL: data.file,  // fixed assignment syntax
              liked: data.liked || false
            });
            setShowPlayer(true);
            updateSongHistory(data.song, data.artist);
            setM3u8Url(data.file); // set the native audio URL
          } else {
            console.error("Could not retrieve audio stream");
          }   
        } catch (error) {
          console.error("Error fetching audio:", error);
          toast.error("Failed to fetch song");
        } finally {
          setIsLoading(false);
        }
      };
      fetchAudio();
    }
  }, [searchQuery]);

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

  const handlePlayClick = () => {
    setIsPlayerVisible(true);
  };

  const resetPlayer = () => {
    setIsLoading(true);
    console.log('Resetting player...');
    if (audioRef.current) {
        audioRef.current.pause();
        console.log('Audio paused.');
        audioRef.current.src = '';
        audioRef.current.load();
        audioRef.current.currentTime = 0;
        console.log('Audio element reset.');
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
    console.log('State reset complete.');
  };

  const handleLike = async () => {
    const previousLikedState = isLiked; 
    setIsLiked(!isLiked);
    const token = Cookies.get("access_token"); 
    const userString = localStorage.getItem("user");
    const user = userString ? JSON.parse(userString) : null;
    const playlistId = user?.playlist[0]; 
  
    if (!playlistId) {
      toast.error("Playlist not found. Please try again.");
      setIsLiked(previousLikedState);
      return;
    }
  
    const songInfo = {
      songName: songData.name,
      artistName: songData.artist,
    };
  
    const requestBody = {
      action: !isLiked ? "add" : "remove", 
      song: songInfo,
      name: "Liked",
      userID: user.id,
      liked: true,
    };
  
    try {
      const response = await fetch(`${serverURL}/model/update/playlist/${playlistId}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          ...(token ? { "Authorization": token } : {}),
        },
        body: JSON.stringify(requestBody),
      });
  
      if (response.ok) {
        const result = await response.json();
        if (!isLiked) {
          toast.success("Added to Liked Songs!");
        } else {
          toast.success("Removed from Liked Songs!");
        }
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Failed to update the playlist");
      }
    } catch (error) {
      console.error("Error in handleLike:", error.message);
      toast.error("Failed to like the song");
      setIsLiked(previousLikedState);
    }
  };
  
  const playSong = async (songN: string, artistN: string) => {
    resetPlayer();
    setSearchQuery(`${songN} ${artistN} song`);
    setIsLoading(true);
  };

  return (
    <div className="min-h-screen flex bg-gray-950 text-white">
      <ToastContainer />

      {isMainContent ? (
        <Sidebar>
          {playlist.map((playlist, index) => (
            <SidebarItem
              key={index}
              playlist={playlist}
              active={selectedPlaylist && (selectedPlaylist as any).name === (playlist as any).name}
              onSelect={() => handlePlaylistSelect((playlist as any).name)}
            />
          ))}
        </Sidebar>
      ) : (
        <SidebarExpanded>
          <li
            onClick={handleBackToMain}
            className="flex items-center py-3 px-4 rounded-lg cursor-pointer text-gray-400 hover:bg-gray-700 hover:text-white transition-all"
          >
            <ArrowLeft className="h-5 w-5 mr-3" />
            Back to Home
          </li>
          {playlist.map((playlist, index) => (
            <SidebarExpandedItem
              key={index}
              playlist={playlist}
              active={selectedPlaylist && (selectedPlaylist as any).name === (playlist as any).name}
              onSelect={() => handlePlaylistSelect((playlist as any).name)}
            />
          ))}
        </SidebarExpanded>
      )}
  
      {/* Main Content */}
      <main className="flex-1 p-8 transition-all duration-300">
        {isMainContent ? (
          <>
            <h2 className="text-4xl font-extrabold text-gray-100 mb-6">
              Welcome Back!
            </h2>      
  
            {/* Search Bar */}
            <div className="flex items-center space-x-4 mb-6">
              <input
                type="text"
                placeholder="Song name"
                value={songName}
                onChange={(e) => setSongName(e.target.value)}
                className="flex-grow p-4 bg-white/10 border border-white/20 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <input
                type="text"
                placeholder="Artist name"
                value={artistName}
                onChange={(e) => setArtistName(e.target.value)}
                className="flex-grow p-4 bg-white/10 border border-white/20 text-white rounded-full focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
              <button
                onClick={handleSearch}
                className="p-3 bg-gradient-to-r from-indigo-500 to-purple-500 text-white rounded-full hover:scale-105 transition-all"
              >
                <Search className="h-5 w-5" />
              </button>
            </div>

            {/* Recently Played */}
            <section className="mb-12">
              <h3 className="text-2xl font-semibold text-gray-200 mb-4">Recently Played</h3>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                {history && history.length > 0 ? (
                  history.map((item: any, idx) => (
                    <motion.div
                      key={idx}
                      whileHover={{ scale: 1.03 }}
                      className="bg-gradient-to-br from-gray-800 via-gray-900 to-gray-800 shadow-lg rounded-xl p-4 flex items-center gap-4 transition-all"
                    >
                      <div className="w-16 h-16 bg-gray-700 rounded-lg flex items-center justify-center">
                        <Music className="text-gray-300 w-8 h-8" />
                      </div>
                      <div className="flex-1">
                        <h4 className="font-bold text-white">{item.songName || "Unknown Song"}</h4>
                        <p className="text-gray-400 text-sm">{item.artistName || "Unknown Artist"}</p>
                      </div>
                      <button
                        className="text-indigo-400 hover:text-indigo-600 transition-all"
                        onClick={() => playSong(item.songName, item.artistName)}
                      >
                        <Play />
                      </button>
                    </motion.div>
                  ))
                ) : (
                  <p className="text-gray-400">No recently played songs found.</p>
                )}
              </div>
            </section>
          </>
        ) : selectedPlaylist && (selectedPlaylist as any).songs ? (
          <>
            <h2 className="text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-600 to-indigo-600 mb-8">
              {(selectedPlaylist as any).name}
            </h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
              {(selectedPlaylist as any).songs.length > 0 ? (
                (selectedPlaylist as any).songs.map((song, idx) => (
                  <motion.div
                    key={idx}
                    whileHover={{
                      scale: 1.05,
                      boxShadow: "0px 10px 20px rgba(255, 255, 255, 0)"
                    }}
                    className="relative bg-gradient-to-br from-gray-800 via-gray-900 to-gray-800 shadow-xl rounded-xl overflow-hidden group"
                  >
                    <div className="absolute inset-0 bg-gradient-to-r from-purple-600/10 to-gray-600/10 opacity-0 group-hover:opacity-100 transition-all duration-500"></div>
                    <div className="p-6 space-y-3">
                      <div className="flex items-center">
                        <Music className="text-purple-400 w-10 h-10 mr-4 group-hover:scale-110 transition-all" />
                        <div>
                          <h4 className="font-bold text-white text-lg">{song.songName}</h4>
                          <p className="text-sm text-gray-400">{song.artistName}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => playSong(song.songName, song.artistName)}
                        className="absolute bottom-4 right-4 p-3 bg-gradient-to-br from-purple-600 to-indigo-500 rounded-full text-white hover:scale-110 transition-all"
                      >
                        <Play className="h-6 w-6" />
                      </button>
                    </div>
                  </motion.div>
                ))
              ) : (
                <p className="text-gray-400 col-span-full">No songs found in this playlist.</p>
              )}
            </div>
          </>
        ) : (
          <p className="text-gray-400">Playlist not found.</p>
        )}
  
        {/* Player Section */}
        {showPlayer && songData && (
          <div className="bg-black p-6 fixed bottom-0 left-0 w-full z-10">
            <div className="flex justify-between items-center">
              {/* Song Details and Music Icon */}
              <div className="flex items-center">
                <div className="w-10 h-10 bg-gray-700 flex items-center justify-center">
                  <Music className="text-white w-6 h-6" />
                </div>
                <div className="ml-4 text-white">
                  <h4 className="font-semibold text-lg">{songData.name}</h4>
                  <p className="text-gray-400 text-sm">{songData.artist}</p>
                </div>
              </div>
  
              {/* Hidden native Audio Element */}
              <audio
                ref={audioRef}
                onTimeUpdate={handleTimeUpdate}
                src={m3u8Url}
                className="hidden"
                preload="auto"
              />
  
              <div className="flex items-center space-x-6">
                <button onClick={() => skip(-10)} className="text-white hover:text-gray-400 transition duration-200">
                  <ArrowLeft className="h-8 w-8" />
                </button>
                <button
                  onClick={togglePlayPause}
                  className="text-white hover:text-gray-400 transition duration-200"
                  disabled={isLoading || !m3u8Url}
                >
                  {isLoading ? (
                    <div className="w-8 h-8 border-4 border-t-transparent border-indigo-500 rounded-full animate-spin"></div>
                  ) : (
                    isPlaying ? (
                      <Pause className="h-8 w-8" />
                    ) : (
                      <Play className="h-8 w-8" />
                    )
                  )}
                </button>
                <button onClick={() => skip(10)} className="text-white hover:text-gray-400 transition duration-200">
                  <ArrowRight className="h-8 w-8" />
                </button>
              </div>
  
              {/* Right Section with Liked and Plus Buttons */}
              <div className="flex items-center space-x-6">
                <button className="text-white" onClick={handleLike}>
                  <FaHeart
                    className={`h-6 w-6 ${isLiked ? "text-purple-600" : "text-gray-400"}`}
                  />
                </button>
                  
                <button onClick={handlePlus} className="text-white">
                  <FaPlus className="h-6 w-6" />
                </button>
              </div>
            </div>
  
            {/* Progress Bar */}
            <div className="mt-4 w-full bg-gray-700 rounded-full">
              <div
                onClick={handleSeek}
                className="relative w-full h-2 bg-gray-700 rounded-full cursor-pointer"
              >
                <div
                  className="absolute top-0 left-0 h-2 bg-indigo-500 rounded-full"
                  style={{ width: `${(currentTime / duration) * 100}%` }}
                />
              </div>
            </div>
            <div className="flex justify-between text-sm mt-2 text-gray-400">
              <span>{formatTime(currentTime)}</span>
              <span>{formatTime(duration)}</span>
            </div>
          </div>
        )}
  
        {isPopupVisible && (
          <PlusPopup 
            onClose={handlePopupClose}
            playlistNames={playlistNames}
            onPlaylistSelect={handlePlaylistSelect}
            createPlaylist={createPlaylist}
            songName={songData.name}
            artistName={songData.artist}
          />
        )}
        
      </main>
    </div>
  );
};

export default Dashboard;
