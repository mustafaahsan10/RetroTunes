from operator import or_
from flask import Blueprint,render_template,request,flash,redirect,url_for
from flask_login import login_required,current_user
from .models import Playlist, User,Song,Rating,Album
from . import db
from .utils import encode_image_to_base64,encode_song_to_base64,encode_lyrics_to_base64
from .helper import populate_dictionary
import time
from sqlalchemy import or_ ,func
from sqlalchemy.orm import joinedload



views =Blueprint("views",__name__)


@views.route("/home")
@login_required
def home():
    start_time = time.time()
    user_profile_images = {}
    songs={}
    playlists={}
    album={}
    song_ratings = {}
    playlist_ratings={}
    all_songs= Song.query.all()
    all_playlists = Playlist.query.all()
    all_album=Album.query.all()
    all_data=all_songs+all_playlists+all_album

    for data in all_data:
        user=data.user
        if isinstance(data, Song):
            profile_image_base64 = encode_image_to_base64(user.image)
            user_profile_images[user.id] = profile_image_base64
        
            song_data = {} 
            song_data['song_profile'] = encode_image_to_base64(data.song_profile)
            song_data['song'] = encode_song_to_base64(data.song)
            song_data['song_name'] = data.song_name
            song_data["author"] =user.username
            song_data["userId"]=user.id
          
            songs[data.id] = song_data
           
            ratings = data.ratings
            if ratings:
                average_rating = sum(rating.value for rating in ratings) / len(ratings)
            else:
                average_rating = 0
            song_ratings[data.id] = average_rating
        elif isinstance(data, Playlist):
            playlist_data = {
                'type': 'playlist',
                'image': encode_image_to_base64(data.image),
                'name': data.name,
                'description': data.description,
                "userId": user.id,
            }
            playlists[data.id] = playlist_data
            ratings = data.ratings
           
            if ratings:
                average_rating = sum(rating.value for rating in ratings) / len(ratings)
            else:
                average_rating = 0
            playlist_ratings[data.id] = average_rating
        else:
            album_data={
                'type':'album',
                'image':encode_image_to_base64(data.image),
                'name':data.name,
                'artist':data.artist,
                'userId':data.user_id
            }
           
            album[data.id]=album_data

    sorted_songs = {k: v for k, v in sorted(songs.items(), key=lambda item: song_ratings[item[0]], reverse=True)[:10]}

    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Execution time: {execution_time} seconds")
    return render_template("home.html", user=current_user,album=album,sorted_songs=sorted_songs,
                            playlists=playlists,songs=songs,playlist_ratings=playlist_ratings,
                            user_profile_images=user_profile_images,song_ratings=song_ratings)



# ...................................................................................admin...................................................................................

@views.route("/admin_dashboard/<username>")
@login_required
def admin_dashboard(username):
   
    all_users = User.query.all()
    all_data=Song.query.all()+ Playlist.query.all()+Album.query.all()
    
    songs, song_ratings, playlists, playlist_ratings ,album = populate_dictionary(all_data)
   
    user_count=len(all_users)
    song_count=len(songs)
    playlist_count=len(playlists)

    user_profile_images={}

    for user in all_users:
        profile_image_base64 = encode_image_to_base64(user.image)
        user_profile_images[user.id] = profile_image_base64
  

    print(playlist_ratings)
    print(song_ratings)


    
    statistics={"users":user_count,"songs":song_count,"playlist":playlist_count}
    

    sorted_songs = {k: v for k, v in sorted(songs.items(), key=lambda item: song_ratings[item[0]], reverse=True)[:10]}

    

    return render_template("admin_page.html",user=current_user, sorted_songs=sorted_songs,statistics=statistics,
                           playlists=playlists, playlist_ratings= playlist_ratings,users=all_users,album=album,
                           username=username,user_profile_images=user_profile_images,songs=songs,song_ratings=song_ratings)






# ...........................................................................................user......................................................................................

@views.route("/delete-user-account/<username>")
@views.route("user/delete-user-account/<username>")
@views.route("posts/delete-user-account/<username>")
@login_required
def delete_user(username):
    user= User.query.filter_by(username=username).first()
    

    if not user:
        flash("user does not exits",category="error")

    elif not current_user.is_admin and current_user.id != user.id:
        flash("you dont have a permission" , category="error")
    else:
        for song in user.Song:
            db.session.delete(song)
         
        for playlist in user.playlists:
            db.session.delete(playlist)
        
        for rating in user.ratings:
            db.session.delete(rating)
        db.session.delete(user)
        db.session.commit()
    return redirect(url_for("views.admin_dashboard",username=current_user.username))



@views.route("/user/<username>")
@views.route("/posts/<username>")
@login_required
def posts(username):
    user = User.query.filter_by(username=username).first()
    all_songs = Song.query.filter_by(author=user.id).all()
    all_playlists= Playlist.query.filter_by(user_id=user.id).all()
    all_albums=Album.query.filter_by(user_id=user.id).all()

 
    all_data=all_songs+all_playlists+all_albums


    songs, song_ratings, playlists, playlist_ratings ,album= populate_dictionary(all_data)

    user_profile_images={}
    profile_image_base64 = encode_image_to_base64(user.image)
    user_profile_images[user.id] = profile_image_base64
    

    sorted_songs = {k: v for k, v in sorted(songs.items(), key=lambda item: song_ratings[item[0]], reverse=True)[:10]}
       
    return render_template("posts.html",user=user,songs=songs,playlists=playlists,album=album,
                           sorted_songs=sorted_songs,playlist_ratings= playlist_ratings,
                           username=username,song_ratings=song_ratings, user_profile_images=user_profile_images)




@views.route("/creator_profile/<username>")
@login_required
def creator(username):
    user= User.query.filter_by(username=username).first()
    print(user.is_creator)
       
    if user.is_creator==False:
        user.is_creator=True
        db.session.commit()
        
    return redirect(url_for("views.home"))


#..................................................rating....................................................................




@views.route('/rate_playlist/<int:playlist_id>', methods=['POST'])
@login_required
def rate_playlist(playlist_id):
    playlist = Playlist.query.get(playlist_id)
    if playlist is not None:
        rating_value = int(request.form.get('playlist_rating'))
        user_id = current_user.id
        existing_rating = Rating.query.filter_by(user_id=user_id, playlist_id= playlist.id).first()

        if existing_rating:
           
            existing_rating.value = rating_value
            print(rating_value)

        else:
           
            new_rating = Rating(value=rating_value, playlist_id= playlist.id, user_id=user_id)
            db.session.add(new_rating)
            print(rating_value)

        db.session.commit()
    return redirect(url_for('views.home'))


@views.route('/rate_song/<int:song_id>', methods=['POST'])
@login_required
def rate_song(song_id):
    song = Song.query.get(song_id)
    if song is not None:
        rating_value = int(request.form.get('rating'))
        user_id = current_user.id
        existing_rating = Rating.query.filter_by(user_id=user_id, song_id=song.id).first()
        if existing_rating:
            existing_rating.value = rating_value
        else:
            new_rating = Rating(value=rating_value, song_id=song.id, user_id=user_id)
            db.session.add(new_rating)

        db.session.commit()
    return redirect(url_for('views.home'))



#.........................................search......................................................


@views.route("/search-songs", methods=["GET","POST"])
@login_required
def search_songs():
    
    search_results = {
            'song_results': [],
            'playlist_results': [],
            'user_results': [],
            'gernre':{},
            'album_results':[],
        }

    all_users = User.query.all()
    all_data=Song.query.all()+ Playlist.query.all()+all_users+Album.query.all()
    songs, song_ratings, playlists, playlist_ratings ,album= populate_dictionary(all_data)

    sorted_songs = {k: v for k, v in sorted(songs.items(), key=lambda item: song_ratings[item[0]], reverse=True)[:10]}

    user_profile_images={}
    for user in all_users:
        profile_image_base64 = encode_image_to_base64(user.image)
        user_profile_images[user.id] = profile_image_base64
        
    if request.method == "POST":
        q=request.form.get("search")

        
 
        # Filter songs, playlists, and users and store results in the dictionary
        search_results['song_results'] = Song.query.filter(
            or_(Song.song_name.ilike(f"%{q}%"), Song.author.ilike(f"%{q}%"))
        ).limit(30).all()

        search_results['playlist_results'] = Playlist.query.filter(Playlist.name.ilike(f"%{q}%")).all()
        search_results['user_results'] = User.query.filter(User.username.ilike(f"%{q}%")).all()
        search_results['album_results'] =Album.query.filter(Album.artist.ilike(f"%{q}%")).all()
        print(search_results['album_results'])   #to avoid a rpeataion we displaying search artist only by ablums
        search_results['gernre'] = Song.query.filter(Song.gernre.ilike(f"%{q}%")).all()
        print(search_results['gernre'])
    return render_template("search.html", user=current_user,sorted_songs=sorted_songs,album=album, playlists=playlists,songs=songs,playlist_ratings=playlist_ratings,user_profile_images=user_profile_images,song_ratings=song_ratings,search_results=search_results)




#.................................................................. Create post...................................................................




