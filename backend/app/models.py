from .extensions import db
from flask_login import UserMixin
from sqlalchemy.sql import func
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename



# Association tables for many-to-many relationships
playlist_song = db.Table('playlist_song',
    db.Column('playlist_id', db.Integer, db.ForeignKey('playlist.id')),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id'))
)

album_song = db.Table('album_song',
    db.Column('album_id', db.Integer, db.ForeignKey('album.id', ondelete="CASCADE")),
    db.Column('song_id', db.Integer, db.ForeignKey('song.id', ondelete="CASCADE"))
)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.Text,nullable=False)
    mimetype_profile = db.Column(db.Text,nullable=False)
    name =db.Column(db.Text,nullable=False)
    email =db.Column(db.String(150),unique=True)
    username =db.Column(db.String(150),unique=True)
    password_hash =db.Column(db.String(150))
    date_created = db.Column(db.DateTime(timezone=True),default=func.now())
    is_admin = db.Column(db.Boolean, default=False)
    is_creator = db.Column(db.Boolean, default=False)
    Song = db.relationship("Song",backref="user",passive_deletes=True)
    playlists = db.relationship('Playlist', back_populates='user')
    album=db.relationship("Album",back_populates='user')
    ratings = db.relationship("Rating", back_populates="user")
    
    # Relationships
    items = db.relationship('Item', backref='owned_user', lazy=True)

    @property
    def password(self):
        raise NotImplementedError("Password retrieval is not allowed")

    @password.setter
    def password(self, plain_text_password):
        self.password_hash = generate_password_hash(plain_text_password, method='pbkdf2:sha256')

    def check_password(self, password_attempt):
        return check_password_hash(self.password_hash, password_attempt)

    def can_purchase(self, item_obj):
        return self.budget and self.budget >= item_obj.price
    
    def can_sell(self, item_obj):
        return item_obj in self.items


# Item model for marketplace
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(length=30), nullable=False, unique=True)
    barcode = db.Column(db.String(length=12), nullable=False, unique=True)
    price = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(length=1024), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    
    def __repr__(self):
        return f'Item {self.name}'

# Music related models
class Song(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    song_profile = db.Column(db.Text, nullable=True)
    mimetype_song_profile = db.Column(db.Text, nullable=True)
    song = db.Column(db.Text, nullable=False)
    song_name = db.Column(db.Text, nullable=False)
    mimetype_song_audio = db.Column(db.Text, nullable=False)
    song_lyrics = db.Column(db.Text, nullable=True)
    mimetype_song_lyrics = db.Column(db.Text, nullable=False)
    date_created = db.Column(db.DateTime(timezone=True), default=func.now())
    author = db.Column(db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    artist = db.Column(db.Text, nullable=True)
    genre = db.Column(db.Text, nullable=True)
    ratings = db.relationship('Rating', back_populates='song')

class Playlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=True)
    image = db.Column(db.Text, nullable=False)
    mimetype_profile = db.Column(db.Text, nullable=False)
    songs = db.relationship('Song', secondary=playlist_song, backref='playlists')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    user = db.relationship('User', back_populates='playlists')
    ratings = db.relationship('Rating', back_populates='playlist')


class Album(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    artist = db.Column(db.Text, nullable=False)
    image = db.Column(db.Text, nullable=False)
    genre = db.Column(db.Text, nullable=True)
    songs = db.relationship('Song', secondary=album_song, backref='album')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    user = db.relationship('User', back_populates='album')

class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Integer)  # Rating value (e.g., 1-5 stars)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"), nullable=False)
    user = db.relationship('User', back_populates='ratings')

    song_id = db.Column(db.Integer, db.ForeignKey('song.id', ondelete="CASCADE"), nullable=True)
    song = db.relationship('Song', back_populates='ratings') 

    playlist_id = db.Column(db.Integer, db.ForeignKey('playlist.id', ondelete="CASCADE"), nullable=True)
    playlist = db.relationship('Playlist', back_populates='ratings')
