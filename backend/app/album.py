from operator import or_
from flask import Blueprint,render_template,request,flash,redirect,url_for
from flask_login import login_required,current_user
from .models import User,Song,Rating,Album
from . import db
from .utils import encode_image_to_base64,encode_song_to_base64

album_bp = Blueprint('album',__name__)


@album_bp.route('/album/<int:id>')
@login_required
def view_albums(id):
    
    album = Album.query.filter_by(id=id).first()
    Artist= album.artist
    print(Artist)
    all_songs = Song.query.filter_by(artist=Artist).all()

    pl_id = id

    album_data = {}
    songs = {}

    if album:
       
        album_data = {
            'type': 'album',
            'image': encode_image_to_base64(album.image),
            'name': album.name,
            'artist':album.artist,
            'userId': album.user_id,
            "author":album.user.username
            
        }

        songs = album.songs
       

    song_data = {}
    for song in all_songs:
        song_id = song.id
        song_data[song_id] = {
            'song_profile': encode_image_to_base64(song.song_profile),
            'song': encode_song_to_base64(song.song),
            'song_name': song.song_name,
            'author': song.user.username  
        }
    return render_template('album.html', all_songs=all_songs,pl_id=pl_id,album=album, song_data=song_data, album_data=album_data, songs=songs, user=current_user)




@album_bp.route('/add_song_to_album/<int:album_id>/<int:song_id>', methods=['POST'])
@login_required
def add_song_to_album(album_id, song_id):
    song = Song.query.get(song_id)
    album = Album.query.get(album_id)

    if album and song and song not in album.songs:
        album.songs.append(song)
        db.session.commit()
    else:
        flash("the song alredy exist in the play list")
    return redirect(url_for('album.view_albums', id=album_id))


@album_bp.route('/remove_song_from_album/<int:album_id>/<int:song_id>', methods=['POST'])
@login_required
def remove_song_from_album(album_id, song_id):
    album = Album.query.get(album_id)
    song = Song.query.get(song_id)
    if current_user == album.user or current_user.is_admin:
        if album and song:
            if song in album.songs:
                album.songs.remove(song)
                db.session.commit()
    else:
        flash("Permission denied.", "error")

        return redirect(url_for("views.home"))             
        
    return redirect(url_for('album.view_albums', id=album_id))

 

@album_bp.route("/delete-album/<id>")
@login_required
def delete_album(id):
    album = Album.query.filter_by(id=id).first()

    if not album:
        flash("Post does not exit",category="error")
    elif current_user.id != album.user_id  and not current_user.is_admin :
        flash("you do not have permission to delete this album")

    else:
        db.session.delete(album)
        db.session.commit()
        flash("album deleted",category="success")
    return redirect(url_for("views.home"))


@album_bp.route("/edit-album/<int:id>",methods=['POST',"GET"])
@login_required
def edit_album(id):
    album = Album.query.filter_by(id=id).first()
    image = encode_image_to_base64(album.image)
    
    songs = album.songs
    print(len(songs))
   
    
    if request.method=="POST":
        new_album_name = request.form.get('album_name')
        new_album_profile = request.files.get('album_profile')
        new_selected_genre = request.form.get('genre')
        new_artist =request.form.get('artist_name')

        if new_album_name:
            album.name=new_album_name
        if new_album_profile:
            album.image=new_album_profile.read()


        
        if new_selected_genre:
            album.gernre=new_selected_genre
        if new_artist:
            if new_artist and len(songs)<=0:
                album.artist=new_artist
            else:
                flash("cannot change the artist when the current ablum having songs")
        db.session.commit()

        return redirect(url_for("album.view_albums",id=album.id))

    return render_template('edit.html',user=current_user,album=album,album_profile=image)