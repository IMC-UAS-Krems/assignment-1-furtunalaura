from streaming.tracks import Track, Song
from streaming.users import User, PremiumUser, FamilyMember
from datetime import datetime, timedelta
from streaming.artists import Artist
from streaming.albums import Album
from streaming.playlists import Playlist, CollaborativePlaylist
from streaming.sessions import ListeningSession
from typing import Optional

class StreamingPlatform:
    def __init__(self, name: str):
        self.name = name
        # dictionaries for fast lookup by ID
        self._catalogue: dict[str, Track] = {}
        self._users: dict[str, User] = {}
        self._artists: dict[str, Artist] = {}
        self._albums: dict[str, Album] = {}
        self._playlists: dict[str, Playlist] = {}
        # list of all sessions
        self._sessions: list[ListeningSession] = []
    def add_track(self, track:Track) -> None:
        self._catalogue[track.track_id] = track
    def add_user(self, user: User) -> None:
        self._users[user.user_id] = user
    def add_artist(self, artist: Artist) -> None:
        self._artists[artist.artist_id] = artist
    def add_album(self, album: Album) -> None:
        self._albums[album.album_id] = album
    def add_playlist(self, playlist: Playlist) -> None:
        self._playlists[playlist.playlist_id] = playlist
    def record_session(self, session: ListeningSession) -> None:
        self._sessions.append(session)
        #add session to user
        session.user.add_session(session)
    def get_track(self, track_id: str):
        return self._catalogue.get(track_id)
    def get_user(self, user_id: str):
        return self._users.get(user_id)
    def get_artist(self, artist_id: str):
        return self._artists.get(artist_id)
    def get_album(self, album_id: str):
        return self._albums.get(album_id)
    def all_users(self):
        return list(self._users.values())
    def all_tracks(self):
        return list(self._catalogue.values())
    #Q1
    def  total_listening_time_minutes(self, start:datetime, end:datetime) ->float:
        total_seconds= 0
        for session in self._sessions:
            if start<= session.timestamp <=end:
                total_seconds += session.duration_listened_seconds
        return float(total_seconds/60)
    #Q2
    def avg_unique_tracks_per_premium_user(self, days:int =30) -> float:
        premium_users = [
            u for u in self._users.values()
            if isinstance(u, PremiumUser)
        ]
        if not premium_users:
            return 0.0
        if self._sessions:
            latest_time = max (s.timestamp for s in self._sessions)
        else:
            return 0.0
        cutoff = latest_time - timedelta(days=days)
        total_unique=0
        for user in premium_users:
            tracks ={s.track.track_id
                     for s in user.sessions
                     if s.timestamp >= cutoff
                     }
            total_unique += len(tracks)
        return float(total_unique / len(premium_users))
    #Q3
    def track_with_most_distinct_listeners(self):
        #find track listened by the highest number of unique users.
        if not self._sessions:
            return None
        track_users = {}
        for session in self._sessions:
            tid = session.track.track_id
            user = session.user
            if tid not in track_users:
                track_users[tid] = set()
            track_users[tid].add(user)
        best_track_id = max(track_users, key=lambda t: len(track_users[t]))
        return self._catalogue.get(best_track_id)
    #Q4
    def avg_session_duration_by_user_type(self) -> list[tuple[str, float]]:
        data ={}
        for session in self._sessions:
            type_name = type(session.user).__name__
            if type_name not in data:
                data[type_name] = {"total": 0, "count": 0}
            data[type_name]["total"] += session.duration_listened_seconds
            data[type_name]["count"] += 1
        result = []
        for type_name, values in data.items():
            average_duration_seconds = values["total"] / values["count"]
            result.append((type_name, float(average_duration_seconds)))
        #sorted list descending
        return sorted(result, key=lambda x: x[1], reverse=True)
    #Q5
    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        #Sum listening time for FamilyMember users with age < threshold.
        total_seconds = 0
        for session in self._sessions:
            user = session.user
            if isinstance(user, FamilyMember) and user.age < age_threshold:
                total_seconds += session.duration_listened_seconds
        return float(total_seconds / 60)
    #Q6
    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
        #Rank artists by total listening time.
        artist_time = {}
        for session in self._sessions:
            track = session.track
            # ignore podcasts and audiobooks
            if isinstance(track, Song):
                artist = track.artist
                if artist not in artist_time:
                    artist_time[artist] = 0
                artist_time[artist] += session.duration_listened_seconds
        # convert to minutes
        result = [
            (artist, seconds / 60)
            for artist, seconds in artist_time.items()
        ]
        # sort descending
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]
    #Q7
    def user_top_genre(self, user_id: str) -> Optional[tuple[str, float]]:
        #Find the genre with top listening time for a user. Return percentage of total listening time.
        user = self.get_user(user_id)
        if user is None or not user.sessions:
            return None
        genre_time = {}
        for session in user.sessions:
            genre = session.track.genre
            if genre not in genre_time:
                genre_time[genre] = 0
            genre_time[genre] += session.duration_listened_seconds
        total = sum(genre_time.values())
        top_genre = max(genre_time, key=genre_time.get)
        percentage = (genre_time[top_genre] / total) * 100
        return top_genre, float(percentage)
    #Q8
    def collaborative_playlists_with_many_artists(self, threshold: int = 3) -> list[CollaborativePlaylist]:
        result = []
        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                artists = {
                    track.artist
                    for track in playlist.tracks
                    if isinstance(track, Song)
                }
                if len(artists) > threshold:
                    result.append(playlist)
        return result
    #Q9
    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        normal_total = normal_count = 0 #total tracks in normal playlists
        collab_total = collab_count = 0 #total tracks in collaborative playlists
        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                collab_total += len(playlist.tracks)
                collab_count += 1
            else:
                normal_total += len(playlist.tracks)
                normal_count += 1
        return {
            "Playlist": float(normal_total / normal_count) if normal_count else 0.0,
            "CollaborativePlaylist": float(collab_total / collab_count) if collab_count else 0.0}
    #Q10
    def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
        result = []
        for user in self._users.values():
            # all tracks user listened to
            user_tracks = {s.track.track_id for s in user.sessions}
            completed_albums = []
            for album in self._albums.values():
                album_tracks = album.track_ids()
                # ignore empty albums
                if album_tracks and album_tracks.issubset(user_tracks):
                    completed_albums.append(album.title)
            if completed_albums:
                result.append((user, completed_albums))
        return result
