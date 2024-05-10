from operator import or_
from .utils import encode_image_to_base64,encode_song_to_base64
from .models import Playlist, User,Song,Rating,Album
from . import db
import matplotlib.pyplot as plt  
from sqlalchemy import func

def populate_dictionary(data):

    songs = {}
    album={}
    song_ratings = {}
    playlists = {}
    playlist_ratings = {}
    

    for item in data:
        if isinstance(item, Song):
            user = item.user
            

            song_data = {
                'song_profile': encode_image_to_base64(item.song_profile),
                'song': encode_song_to_base64(item.song),
                'song_name': item.song_name,
                'userId':user.id,
                'author': user.username,
            }
            

            songs[item.id] = song_data

            ratings = item.ratings
            average_rating = sum(rating.value for rating in ratings) / len(ratings) if ratings else 0
            song_ratings[item.id] = average_rating
        elif isinstance(item, Playlist):
            playlist_data = {
                'type': 'playlist',
                'image': encode_image_to_base64(item.image),
                'name': item.name,
                'description': item.description,
            }

            playlists[item.id] = playlist_data

            ratings = item.ratings
            average_rating = sum(rating.value for rating in ratings) / len(ratings) if ratings else 0
            playlist_ratings[item.id] = average_rating
        elif isinstance(item, Album):
            album_data={
                'type':'album',
                'image':encode_image_to_base64(item.image),
                'name':item.name,
                'artist':item.artist,
                'userId':item.user_id
            }
            album[item.id]=album_data

    return songs, song_ratings, playlists, playlist_ratings,album


