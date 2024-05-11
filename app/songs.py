from operator import or_
from flask import Blueprint,render_template,request,flash,redirect,url_for
from flask_login import login_required,current_user
from .models import Playlist, User,Song,Rating,Album
from . import db
from .utils import encode_image_to_base64,encode_song_to_base64




songs_blueprint =Blueprint('songs',__name__)

@songs_blueprint.route("/create-post", methods=['GET', "POST"])
@login_required
def create_post():
    if request.method == "POST":
        # Check if a song is being created!
        if 'song_profile' in request.files:
            song_name = request.form.get('song_name')
            song_profile = request.files.get('song_profile')
            song = request.files.get('post_song')
            lyrics = request.files.get('lyrics_text')
            selected_genre = request.form.get('genre')
            artist =request.form.get('artist')

            if not (song or lyrics):
                flash("Please upload either a song or lyrics to create a post.", category="error")
            else:
                post = Song(song_name=song_name,
                            author=current_user.id,
                            artist=artist,
                            song_profile=song_profile.read(),
                            song=song.read(),
                            song_lyrics=lyrics.read(),
                            genre=selected_genre ,
                            mimetype_song_profile=song_profile.mimetype if song_profile else None,
                            mimetype_song_audio=song.mimetype if song else None,
                            mimetype_song_lyrics=lyrics.mimetype if lyrics else None,
                )
                db.session.add(post)
                db.session.commit()
                flash("Song created successfully.", category="success")
                return redirect(url_for("views.home"))

        # Check if a playlist is being created!
        elif 'playlist_profile' in request.files:
            name = request.form['playlist_name']
            description = request.form['description']
            playlist_profile = request.files['playlist_profile']

            if playlist_profile:
                image = playlist_profile.read()
                mimetype_profile = playlist_profile.mimetype
            else:
                image = None
                mimetype_profile = None

            playlist = Playlist(name=name,user_id=current_user.id, description=description, image=image, mimetype_profile=mimetype_profile)
            db.session.add(playlist)
            db.session.commit()
            flash("Playlist created successfully.", category="success")
            return redirect(url_for('views.home'))
        
        else:
            name = request.form["album_name"]
            artist=request.form['artist_name']
            song_profile = request.files.get('album_profile')
            selected_genre = request.form.get('genre')

            if not (artist or song_profile):
                flash("Please upload either a song or lyrics to create a post.", category="error")
            else:
                post = Album(name=name,
                             artist=artist,
                            image=song_profile.read(),
                            gernre=selected_genre ,
                            user_id=current_user.id,
                )
                db.session.add(post)
                db.session.commit()
                flash("Album created successfully.", category="success")
                return redirect(url_for("views.home"))


    return render_template('create_song.html', user=current_user)





# .........................................................................................songs post----------------------------

@songs_blueprint.route("/song/<int:id>")
@login_required
def songs(id):
    song = Song.query.get(id)
    
    lyrics_data = song.song_lyrics.decode('utf-8')  
    lyrics_data = lyrics_data.replace('\r\n', '\n') 
    song_profile = encode_image_to_base64(song.song_profile)
    songs = encode_song_to_base64(song.song)
    
    ratings = song.ratings
    if ratings:
        average_rating = sum(rating.value for rating in ratings) / len(ratings)
    else:
        average_rating = 0

    return render_template("song.html",song=song,user=current_user,lyrics=lyrics_data,song_profile=song_profile,songs=songs,average_rating=average_rating)


@songs_blueprint.route("/delete-post/<id>")
@login_required
def delete_post(id):
    song = Song.query.filter_by(id=id).first()

    if not song:
        flash("Post does not exit",category="error")
    elif current_user.id != song.author  and not current_user.is_admin :
        flash("you do not have permission to delete this post")
        
    else:
        for rating in song.ratings:
            db.session.delete(rating)

        db.session.delete(song)
        db.session.commit()
        flash("post deleted",category="success")
    return redirect(url_for("views.home"))



@songs_blueprint.route("/edit-song/<int:id>",methods=['POST',"GET"])
@login_required
def edit_song(id):
    song = Song.query.filter_by(id=id).first()

    lyrics_data = song.song_lyrics.decode('utf-8')  
    lyrics_data = lyrics_data.replace('\r\n', '\n') 
    song_profile = encode_image_to_base64(song.song_profile)
    songs = encode_song_to_base64(song.song)
    
    if request.method=="POST":
        new_song_name = request.form.get('song_name')
        new_song_profile = request.files.get('song_profile')
        new_song = request.files.get('post_song')
        new_lyrics = request.files.get('lyrics_text')
        new_selected_genre = request.form.get('genre')
        new_artist =request.form.get('artist')

        if new_song_name:
            song.song_name=new_song_name

        if new_song_profile:
            song.song_profile=new_song_profile.read()
        
        if new_song:
            song.song=new_song.read()
            
        if new_lyrics:
            song.song_lyrics=new_lyrics.read()
        
        if new_selected_genre:
            song.gernre=new_selected_genre
        if new_artist:
            song.artist=new_artist
        db.session.commit()

        return redirect(url_for("songs.songs",id=song.id))

    return render_template('edit.html',user=current_user,song=song,lyrics=lyrics_data,song_profile=song_profile,songs=songs)