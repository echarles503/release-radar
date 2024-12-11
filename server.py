from flask import Flask, request, jsonify, redirect
import datetime
import requests
import base64
import urllib.parse
import string
import secrets

from album_parser import soupify_wiki_page, get_album_data, get_spotify_access_token, get_today_album_ids
from constants import SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET, SPOTIFY_USER_ENDPOINT, REDIRECT_URI, WIKI_URL, WIKI_HEADERS, ALBUMS_BY_MONTH


# Initialize Flask app
app = Flask(__name__)

# Example route to simulate OAuth callback
@app.route("/callback")
def callback():
    # Capture the authorization code sent by Spotify
    code = request.args.get('code')
    state = request.args.get('state')

    # Check for state mismatch
    if state is None:
        return redirect('/#error=state_mismatch')
    
    
    # Exchange the authorization code for an access token
    token_url = "https://accounts.spotify.com/api/token"

    auth_header = base64.b64encode(f"{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth_header}'
    }

    payload = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': REDIRECT_URI
    }

    response = requests.post(token_url, data=payload, headers=headers)
    if response.status_code == 200:
        try:
            token_data = response.json()
            access_token = token_data['access_token']

            # Fetch user's profile_url
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(SPOTIFY_USER_ENDPOINT, headers=headers)
            if user_response.status_code != 200:
                return jsonify({"error": "Failed to fetch user profile"}), user_response.status_code
            
            user_data = user_response.json()
            user_id = user_data.get('id')
            #print(user_id)
            if not user_id:
                return jsonify({"error": "User ID not found in response"}), 500
            
            playlist_url = f"https://api.spotify.com/v1/users/{user_id}/playlists"
            playlist_description = f"Releases on {datetime.datetime.now().strftime('%B %d')}."
            playlist_name = datetime.datetime.now().strftime('%m.%d.%Y')
            playlist_payload = {
                "name" : playlist_name,
                "description" : playlist_description,
                "public" : False
            }
            access_headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }

            playlist_response = requests.post(url=playlist_url, headers=access_headers, json=playlist_payload)
           
            if playlist_response.status_code != 201:
                return jsonify({"error": playlist_response.text}), playlist_response.status_code
            
            playlist_info = playlist_response.json()
            get_album_data()
            auth_token = get_spotify_access_token()
            album_ids = get_today_album_ids(auth_token)
            playlist_id = playlist_info.get('id')
            #print(playlist_id)
            playlist_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
            test_slice = album_ids[:100]
            #print(test_slice)
            
            n = len(album_ids)
            q = n // 100
            r = n % 100
            for i in range(q):
                    req_slice = album_ids[i*100:(i+1)*100] 
                    songs_payload = {
                        "uris" : req_slice
                    }
                    add_songs_response = requests.post(url=playlist_url, headers=access_headers, json=songs_payload)
                    #print(add_songs_response.text, add_songs_response.status_code)
            if r > 0:
                req_slice = album_ids[q*100:]
                songs_payload = {
                        "uris" : req_slice
                    }
                add_songs_response = requests.post(url=playlist_url, headers=access_headers, json=songs_payload)
            

            return jsonify({
                    "message": "Playlist created successfully",
                    "playlist": {
                        "name": playlist_info.get('name'),
                        "id": playlist_info.get('id'),
                        "url": playlist_info.get('external_urls', {}).get('spotify')
                    }
            })
        except Exception as e:
            return jsonify({"error": f"Unexpected error: {str(e)}"}), 500 
    

# Simple route to confirm Flask is running
@app.route("/")
def homepage():
    alphabet = string.ascii_letters + string.digits
    scope = "user-read-email user-read-private playlist-modify-public playlist-modify-private"
    state = ''.join(secrets.choice(alphabet) for _ in range(16))
    auth_url = f"https://accounts.spotify.com/authorize?{urllib.parse.urlencode({
        'client_id': SPOTIFY_CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': scope,
        'state': state
    })}"
    return auth_url

if __name__ == "__main__":
    app.run(debug=True)
