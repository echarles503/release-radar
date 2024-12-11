import requests, datetime, urllib.parse, os, string, secrets
from album_parser import get_album_data, soupify_wiki_page, get_today_album_ids, get_spotify_access_token
#Initialize variables to scrape wiki page

year = datetime.datetime.now().strftime('%Y')
wiki_url = f"https://en.wikipedia.org/w/api.php"
wiki_headers = {
    'action': 'parse',
    'page': f'List_of_{year}_albums',
    'format': 'json'
}

redirect_uri = "https://141e-76-115-139-54.ngrok-free.app/callback"
user_id = "bill_nye_the_soviet_spy"
playlist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"

alphabet = string.ascii_letters + string.digits
state = ''.join(secrets.choice(alphabet) for _ in range(16))

playlist_description = f"Releases on {datetime.datetime.now().strftime('%B %d')}."
playlist_name = datetime.datetime.now().strftime('%m.%d.%Y')
playlist_params = {
    "name" : playlist_name,
    "description" : playlist_description,
    "public" : False
}
scope = "user-read-email user-read-private playlist-modify-public playlist-modify-private"
auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode({
    'client_id': os.getenv("SPOTIFY_CLIENT_ID"),
    'response_type': 'code',
    'redirect_uri': redirect_uri,
    'scope': scope,
    'state': state
})}"

print(auth_url)

# Convert the wiki page to a soupified json format
#soup = soupify_wiki_page(wiki_url, wiki_headers)
# Scrape the page to create a dictionary of albums sorted by month
#new_albums = get_album_data(soup)
#print(new_albums)
# Generate a list of album ids that were released today
#auth_token = get_spotify_access_token()

#album_ids = get_today_album_ids(new_albums, auth_token)
#print(album_ids)


""" Create a new playlist for target user """
#playlist_response = requests.post(url=playlist_url, headers=token_headers, params=playlist_params) 
#print(playlist_response.status_code)
#print(playlist_response.json())
#for id in album_ids:
