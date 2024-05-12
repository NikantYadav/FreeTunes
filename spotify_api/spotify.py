import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import os
from dotenv import load_dotenv, dotenv_values 
from pathlib import Path
from spotipy.oauth2 import SpotifyClientCredentials
import json

with open('songid.json','r') as f:
    data = json.load(f)
#print(data)

dotenv_path = Path('./client.env')
load_dotenv(dotenv_path=dotenv_path)

# print(os.getenv('Client_ID'))

SPOTIFY_CLIENT_ID = str(os.getenv('Client_ID'))
SPOTIFY_CLIENT_SECRET = str(os.getenv('Client_Secret'))

sp = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials(client_id= SPOTIFY_CLIENT_ID,client_secret= SPOTIFY_CLIENT_SECRET))

#track_results = sp.search(q='track:Husn', type='track',limit = '1')
#song_id = track_results
#trackn = sp.track('4eBvRhTJ2AcxCsbfTUjoRp')['artists'][0]['genres']
#print(trackn)
#tracks = ['6VBhH7CyP56BXjp8VsDFPZ','0snQrp1VaY5Pj1YIHRJpRJ','3hkC9EHFZNQPXrtl8WPHnX','2GVVNhSq5gq3rZF2b0UY5a','2fwd3t4N8QNy9w7VT1zC97']
#artists = ['1mYsTxnqsietFxj1OgoGbG','0E02VcvA5p1ndkLdqWD5JB','5GnnSrwNCGyfAU4zuIytiS','1wRPtKGflJrBx9BmLsSwlU','7HCqGPJcQTyGJ2yqntbuyr']
#print('artists = ' + str(artists))
#print('tracks = ' + str(tracks))
#print(recommend)




rec_artist = []
rec_song_id = []

jsonsize = len(data)


if jsonsize < 2:
	rangestart = 0
	rangeend = jsonsize -1
else:
	rangestart = jsonsize-2
	rangeend = jsonsize -1
	# reccomendations



for x in range(rangestart, rangeend+1):
	rec_artist.append(data[x]['artist_id'])


if jsonsize<2:	
	for x in range(rangestart, rangeend+1):
		rec_song_id.append(data[x]['song_id']) 

else:
	for x in range(rangestart-1,rangeend+1):
		rec_song_id.append(data[x]['song_id']) 
                

recommend = sp.recommendations(seed_artists=rec_artist,seed_tracks=rec_song_id,limit=5)

for x in range(0,5):
    print(recommend['tracks'][1]['name'])