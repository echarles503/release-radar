import requests
import re
import datetime
import os
from bs4 import BeautifulSoup
from constants import ALBUMS_BY_MONTH, WIKI_HEADERS, WIKI_URL, SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET


def soupify_wiki_page(url, headers):
    """
    Fetches and parses a Wikipedia page into a BeautifulSoup object.

    Args:
        url (str): URL of the Wikipedia page.
        headers (dict): HTTP headers to include in the request.

    Returns:
        BeautifulSoup: Parsed HTML of the page.
    """
    response = requests.get(url, headers)
    return BeautifulSoup(response.text, 'html.parser')


def get_album_data():
    soup = soupify_wiki_page(WIKI_URL, WIKI_HEADERS) 
    tables = soup('table')
    for t in tables:
        release = ['TBA','TBA']
        for row in t.find_all('tr'):
            # Find content within table cells
            cells = row.find_all('td')
            if len(cells) != 5:
                continue
            # Determine release date
            check_release = row.find('th')
            if check_release is not None:
                raw_release = row.find('th').get_text().replace('\\n', '')
                release  = re.findall(r'\D+|\d+', raw_release)
            # Aggregate plain-text and append release
            data = [cell.get_text().replace('\\n', '') for cell in cells]
            del data[4]
            del data[2]
            if release == 'Artist\\n' or release == ['TBA']:
                release = ['TBA', 'TBA']
            data.append(release[1])
            ALBUMS_BY_MONTH[release[0]].append(data)

def get_spotify_access_token():
    spotify_token_url = "https://accounts.spotify.com/api/token"

    spotify_token_headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }

    spotify_data = {
        "grant_type": "client_credentials",
        'client_id': SPOTIFY_CLIENT_ID,
        'client_secret': SPOTIFY_CLIENT_SECRET
    }

    """ Request a spotify Access Token """
    response = requests.post(spotify_token_url, headers=spotify_token_headers, data=spotify_data)
    saved_response = response.json()
    if response.status_code == 200:
        """ Store Token """
        token_type = saved_response['token_type']
        access_token = saved_response['access_token']

        """ Initialize headers for spotify search request """
        token_headers = {
            "Authorization": f"{token_type}  {access_token}"
        }
        return token_headers
    else:
        return 400



def get_spotify_album_tracks(album_id, access_token):
    """
    Generate a list of Spotify song IDs from a Spotify album ID.

    Args:
        album_id (str): The Spotify album URI (e.g., "spotify:album:ALBUM_ID").
        access_token (str): A valid Spotify API access token with `playlist-modify` or `user-read` scope.

    Returns:
        list: A list of Spotify song IDs or an error message if the request fails.
    """
    try:
        
        # Set the API endpoint
        url = f"https://api.spotify.com/v1/albums/{album_id}/tracks"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        # Make the request to the Spotify API
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            return {"error": f"Failed to retrieve tracks: {response.json().get('error', {}).get('message', 'Unknown error')}"}

        # Parse the response JSON to extract track URIs
        data = response.json()
        track_uris = [track["uri"] for track in data["items"]]

        # Handle pagination (if the album has more than 50 tracks)
        while data.get("next"):
            response = requests.get(data["next"], headers=headers)
            if response.status_code != 200:
                return {"error": f"Failed to retrieve additional tracks: {response.json().get('error', {}).get('message', 'Unknown error')}"}
            data = response.json()
            track_uris.extend(track["uri"] for track in data["items"])

        return track_uris
    except Exception as e:
        return {"error": str(e)}

def get_today_album_ids(auth_token):
    """ Generate a list of album ids for todays releases """
    today_dd = int(datetime.datetime.now().strftime('%d'))
    current_month = datetime.datetime.now().strftime('%B')
    search_url = "https://api.spotify.com/v1/search"
    

    album_ids = []
    try:
        for album in ALBUMS_BY_MONTH['October']: 
            if int(album[3]) == 18:
                params = {
                    "q" : f"{album[0]} {album[1]}",
                    "type" : "album",
                    "limit" : 1,
                    "offset" : 0
                }

                query_response = requests.get(url=search_url, headers=auth_token, params=params)
                
                if query_response.status_code == 200:  # Check for a successful response
                    query_response_json = query_response.json()
                    album_id = query_response_json["albums"]["items"][0]["id"]
                    album_track_ids = get_spotify_album_tracks(album_id, auth_token)
                    for track in album_track_ids:
                        album_ids.append(track)
                    # Debug Print - Album Name
                    #print(query_response_json["albums"]["items"][0]["name"])
                    
                else:
                    print(f"Error: {query_response.status_code}")
                    print(query_response.text)  # Print the raw response text if an error occurs
        return album_ids
    except Exception as e:
        return {"error": str(e)}
   
   
def check_release():
    today_dd = int(datetime.datetime.now().strftime('%d'))
    current_month = datetime.datetime.now().strftime('%B')
    for album in ALBUMS_BY_MONTH[current_month]:
        if album[3] == today_dd:
            return True
    return False



#soup = soupify_wiki_page(wiki_url, wiki_headers)
#new_albums = get_album_data(soup)
#auth_token = get_spotify_access_token()
#album_ids = get_today_album_ids(new_albums, auth_token)