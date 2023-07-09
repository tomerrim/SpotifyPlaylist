from bs4 import BeautifulSoup
import requests
import os
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()

CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

songs_endpoint = "https://www.billboard.com/charts/hot-100"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="playlist-modify-private",
                                               cache_path="token.txt",
                                               show_dialog=True))

# Get the current user dictionary
user = sp.current_user()
print(user)
user_id = user["id"]
print(user_id)

user_year = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

response = requests.get(url=f"{songs_endpoint}/{user_year}")
songs = response.text

soup = BeautifulSoup(songs, "html.parser")
titles = soup.findAll(name="h3", id="title-of-a-story")

songs_list = [song.getText().strip() for song in titles]

song_uris = []
year = user_year.split("-")[0]

for song in songs_list:
    result = sp.search(q=f"track:{song} year:{year}", type="track")
    print(result)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        song_uris.append(uri)
    except IndexError:
        print(f"{song} doesn't exist in Spotify. Skipped")

playlist = sp.user_playlist_create(user=user_id, name=f"{user_year} Billboard 100", public=False)
sp.playlist_add_items(playlist_id=playlist["id"], items=song_uris)
