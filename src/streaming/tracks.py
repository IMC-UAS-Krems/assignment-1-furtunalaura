from datetime import date
from typing import Optional

class Track:
    def __init__(self, track_id:str, title:str, duration_seconds: int, genre:str):
        self.track_id = track_id
        self.title = title
        self.duration_seconds = duration_seconds
        self.genre = genre
    def duration_minutes(self) ->float:
        return self.duration_seconds / 60
    def __eq__(self, other):
        if not isinstance(other, Track):
            return False
        return self.track_id == other.track_id

class Song(Track): #song track associated with an artist
    def __init__(self, track_id: str, title:str, duration_seconds:int, genre:str, artist):
        super().__init__(track_id, title, duration_seconds, genre) #Initialize base Track attributes
        self.artist = artist #Artist object
        self.album =None #album object if part of an album
        self.track_number = 0 #position in album, 0 if single

class SingleRelease(Song): #single song
    def __init__(self,track_id: str, title:str, duration_seconds:int, genre:str, artist, release_date:date):
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.release_date = release_date

class AlbumTrack(Song): #song that belongs to an album
    def __init__(self, track_id:str, title:str, duration_seconds:int, genre: str, artist, album= None, track_number:int = 0):
        super().__init__(track_id, title, duration_seconds, genre, artist)
        self.track_number = track_number #album object this track belongs to
        self.album= album #position in album

class Podcast(Track):
    def __init__(self,track_id:str, title:str, duration_seconds:int, genre:str, host:str, description:str = ""):
        super().__init__(track_id, title, duration_seconds, genre)
        self.host=host
        self.description=description

class InterviewEpisode(Podcast):
    def __init__(self, track_id:str, title:str, duration_seconds:int, genre:str, host:str, guest:str, description:str=""):
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.guest=guest

class NarrativeEpisode(Podcast):
    def __init__(self, track_id:str, title:str, duration_seconds:int, genre:str, host: str, season:int, episode_number:int,description:Optional[str]=None):
        super().__init__(track_id, title, duration_seconds, genre, host, description)
        self.season=season
        self.episode_number=episode_number

class AudiobookTrack(Track): #chapter or section from an audiobook
    def __init__(self, track_id:str, title:str, duration_seconds:int, genre:str, author:str, narrator:str):
        super().__init__(track_id, title, duration_seconds, genre)
        self.author =author
        self.narrator=narrator  #person reading the audiobook