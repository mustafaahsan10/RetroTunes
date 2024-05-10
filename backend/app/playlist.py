from operator import or_
from flask import Blueprint,render_template,request,flash,redirect,url_for
from flask_login import login_required,current_user
from .models import Playlist, User,Song,Rating
from . import db
from .utils import encode_image_to_base64,encode_song_to_base64

playlist_bp = Blueprint('playlist',__name__)
 
# ...........................................................................................playlist........................................................................


@playlist_bp.route('/playlists/<int:id>')
@login_required
def view_playlists(id):
    all_songs = Song.query.all()
    playlist = Playlist.query.get(id)
    pl_id = id
    print(playlist.user)
    print(playlist.user_id)

    playlist_data = {}
    songs = {}

    if playlist:
        ratings=playlist.ratings
        author = playlist.user.username if playlist.user else "Unknown"
        average_rating = sum(rating.value for rating in ratings) / len(ratings) if ratings else 0
        playlist_data = {
            'type': 'playlist',
            'image': encode_image_to_base64(playlist.image),
            'name': playlist.name,
            'author': author,
            'description': playlist.description,
            'rating': average_rating,
        }

        songs = playlist.songs

    song_data = {}
    for song in all_songs:
        song_id = song.id
        song_data[song_id] = {
            'song_profile': encode_image_to_base64(song.song_profile),
            'song': encode_song_to_base64(song.song),
            'song_name': song.song_name,
            'author': song.user.username  
        }
    return render_template('playlists.html', all_songs=all_songs,pl_id=pl_id,playlist=playlist, song_data=song_data, playlist_data=playlist_data, songs=songs, user=current_user)





@playlist_bp.route('/add_song_to_playlist/<int:playlist_id>/<int:song_id>', methods=['POST'])
@login_required
def add_song_to_playlist(playlist_id, song_id):
    song = Song.query.get(song_id)
    playlist = Playlist.query.get(playlist_id)

    if playlist and song and song not in playlist.songs:
        playlist.songs.append(song)
        db.session.commit()
    else:
        flash("the song alredy exist in the play list")
    return redirect(url_for('playlist.view_playlists', id=playlist_id))




@playlist_bp.route('/remove_song_from_playlist/<int:playlist_id>/<int:song_id>', methods=['POST'])
@login_required
def remove_song_from_playlist(playlist_id, song_id):
    playlist = Playlist.query.get(playlist_id)
    song = Song.query.get(song_id)
    if current_user == playlist.user or current_user.is_admin:
        if playlist and song:
            if song in playlist.songs:
                playlist.songs.remove(song)
                db.session.commit()
    else:
        flash("Permission denied.", "error")

        return redirect(url_for("views.home"))             
        
    return redirect(url_for('playlist.view_playlists', id=playlist_id))



@playlist_bp.route("/delete-playlist/<id>")
@login_required
def delete_playlist(id):
    Playlists = Playlist.query.filter_by(id=id).first()

    if not Playlist:
        flash("Post does not exit",category="error")
    elif current_user.id != Playlists.user_id  and not current_user.is_admin :
        flash("you do not have permission to delete this post")

    else:
        for rating in Playlists.ratings:
            db.session.delete(rating)
        db.session.delete(Playlists)
        db.session.commit()
        flash("playlist deleted",category="success")
    return redirect(url_for("views.home"))

