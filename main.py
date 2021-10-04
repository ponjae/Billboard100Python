from bs4 import BeautifulSoup
import requests
from requests.api import put
from requests.sessions import REDIRECT_STATI
from credentials import credentials
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import pprint as pp


CLIENT_ID = credentials["client_id"]
SECRET = credentials["client_secret"]
REDIRECT_URL = "http://example.com"

date = input(
    "Which year do you want to travel back to? Type the date in this format YYYY-MM-DD: ")

# Basic test that the input has the correct length
assert len(date) == 10

# Find the top 100 songs from that specific date
response = requests.get(f"https://www.billboard.com/charts/hot-100/{date}")
response.raise_for_status()


# Fetches the songs and the artist for the specific date
soup = BeautifulSoup(response.text, "html.parser")
songs = [song.text for song in soup.find_all(
    "span", class_="chart-element__information__song text--truncate color--primary")]
artists = [artist.text for artist in soup.find_all(
    "span", class_="chart-element__information__artist text--truncate color--secondary")]


# Log in to Spotify
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-private",
        client_id=CLIENT_ID,
        client_secret=SECRET,
        redirect_uri=REDIRECT_URL,
        show_dialog=True,
        cache_path="token.txt"
    )
)

user_id = sp.current_user()["id"]

# Get the uri:s for the songs

song_uris = []
year = date.split('-')[0]

for song in songs:
    result = sp.search(f"track: {song} year:{year}", type="track")
    try:
        track = result["tracks"]["items"][0]["uri"]
        song_uris.append(track)
    except IndexError:
        print(f"{song} does not exist in Spotify, skipped :/")


# Create the playlist

play_list = sp.user_playlist_create(
    user=user_id, name=f"{date} Billboard 100", public=False, description="A Python generated billboard playlist for a specific date")

sp.playlist_add_items(playlist_id=play_list["id"], items=song_uris)
