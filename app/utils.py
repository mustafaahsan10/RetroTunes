import base64
# In a separate utility function (e.g., utils.py)


def encode_image_to_base64(image_data):
    if image_data:
        return base64.b64encode(image_data).decode('utf-8')
    return None


def encode_song_to_base64(song_data):
    if song_data:
        return base64.b64encode(song_data).decode('utf-8')
    return None


def encode_lyrics_to_base64(lyrics_data):
    if lyrics_data:
        return base64.b64encode(lyrics_data).decode('utf-8')
    return None
