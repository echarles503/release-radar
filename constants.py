import os
import datetime

# Global Variables

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
REDIRECT_URI = "https://141e-76-115-139-54.ngrok-free.app/callback"
YEAR = datetime.datetime.now().strftime('%Y')
WIKI_URL = f"https://en.wikipedia.org/w/api.php"
SPOTIFY_USER_ENDPOINT = "https://api.spotify.com/v1/me"
WIKI_HEADERS = {
    'action': 'parse',
    'page': f'List_of_{YEAR}_albums',
    'format': 'json'
}
ALBUMS_BY_MONTH = {
    'January': [], 
    'February': [], 
    'March': [],
    'April': [],
    'May': [],
    'June': [],
    'July': [],
    'August': [],
    'September': [],
    'October': [],
    'November': [],
    'December': [],
    'TBA': []
}