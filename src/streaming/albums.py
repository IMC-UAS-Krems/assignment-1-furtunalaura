"""
albums.py
---------
Implement the Album class for collections of AlbumTrack objects.

Classes to implement:
  - Album
"""
from streaming.artists import Artist
from streaming.tracks import AlbumTrack

class Album:
    def __init__(self, album_id:str, title:str, artist:Artist, release_year:int):
        self.album_id = album_id
        self.title = title
        self.artist = artist
        self.release_year = release_year
        self.tracks:list[AlbumTrack] = []

    def add_track(self, track:AlbumTrack):
        self.tracks.append(track)
        track.album = self #set album reference
        self.tracks.sort(key=lambda t: t.track_number) #sort tracks by track_number

    def track_ids(self) -> set[str]:
        return {track.track_id for track in self.tracks}

    def duration_seconds(self) ->int:
        return sum(track.duration_seconds for track in self.tracks)

