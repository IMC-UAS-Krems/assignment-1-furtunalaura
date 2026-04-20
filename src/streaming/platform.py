"""
platform.py
-----------
Implement the central StreamingPlatform class that orchestrates all domain entities
and provides query methods for analytics.

Classes to implement:
  - StreamingPlatform
"""
from __future__ import annotations

from streaming.tracks import Song
from streaming.users import User, PremiumUser, FamilyMember
from datetime import datetime, timedelta
from streaming.playlists import Playlist, CollaborativePlaylist
from streaming.tracks import Track
from streaming.artists import Artist
from streaming.albums import Album
from streaming.sessions import ListeningSession

class StreamingPlatform:
    def __init__(self, name: str):
        self.name = name
        self._catalogue: dict[str, Track] = {}
        self._users: dict[str, User] = {}
        self._artists: dict[str, Artist] = {}
        self._albums: dict[str, Album] = {}
        self._playlists: dict[str, Playlist] = {}
        self._sessions: list[ListeningSession] = []

    def add_track(self, track:Track):
        self._catalogue[track.track_id] = track

    def add_user(self, user:User):
        self._users[user.user_id] = user

    def add_artist(self, artist:Artist):
        self._artists[artist.artist_id] = artist

    def add_album(self, album:Album) :
        self._albums[album.album_id] = album

    def add_playlist(self, playlist: Playlist):
        self._playlists[playlist.playlist_id] = playlist

    def record_session(self, session:ListeningSession):
        self._sessions.append(session)
        session.user.add_session(session)

    def get_track(self, track_id: str) -> Track | None:
        return self._catalogue.get(track_id)

    def get_user(self, user_id: str) -> User | None:
        return self._users.get(user_id)

    def get_artist(self, artist_id: str) -> Artist | None:
        return self._artists.get(artist_id)

    def get_album(self, album_id: str) -> Album | None:
        return self._albums.get(album_id)

    def all_users(self) -> list[User]:
        return list(self._users.values())

    def all_tracks(self) -> list[Track]:
        return list(self._catalogue.values())

    #Q1
    def  total_listening_time_minutes(self, start:datetime, end:datetime) ->float:
        """Returns the total listening time( in minutes) across the platform for each session."""

        total_seconds= 0
        for session in self._sessions:
            if start<= session.timestamp <=end:
                total_seconds += session.duration_listened_seconds
        return total_seconds/60

    #Q2
    def avg_unique_tracks_per_premium_user(self, days:int =30) -> float:
        """Returns the average number of unique tracks listened
         to per premium user over the past `days` (default 30).
         Returns 0.0 if no premium users exist."""
        premium_users = [
            u for u in self._users.values()
            if isinstance(u, PremiumUser)
        ]
        if not premium_users:
            return 0.0
        cutoff= datetime.now() - timedelta(days=days)
        total_unique=0
        for user in premium_users:
            tracks ={s.track.track_id
                     for s in user.sessions
                     if s.timestamp >= cutoff}
            total_unique += len(tracks)
        return float(total_unique / len(premium_users))

    #Q3
    def track_with_most_distinct_listeners(self) -> Track | None:
        """Builds a mapping of each track to the set of users who listened to it,
        then returns the track with the highest number of distinct listeners."""
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
        """Computes the average session duration (in seconds) for each user type
        and returns a list of (user_type, average_duration) tuples
        sorted in descending order."""
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
        return sorted(result, key=lambda x: x[1], reverse=True)

    #Q5
    def total_listening_time_underage_sub_users_minutes(self, age_threshold: int = 18) -> float:
        """Calculates the total listening time (in minutes)
        of underage family members (age below the given threshold, default 18) across all sessions."""
        total_seconds = 0
        for session in self._sessions:
            user = session.user
            if isinstance(user, FamilyMember) and user.age < age_threshold:
                total_seconds += session.duration_listened_seconds
        return float(total_seconds / 60)

    #Q6
    def top_artists_by_listening_time(self, n: int = 5) -> list[tuple[Artist, float]]:
        """Returns the top N artists ranked by total listening time (in minutes) across all sessions."""
        artist_time = {}
        for session in self._sessions:
            if isinstance(session.track, Song):
                artist = session.track.artist
                if artist not in artist_time:
                    artist_time[artist] = 0
                artist_time[artist] += session.duration_listened_seconds
        result = [(artist, seconds / 60) for artist, seconds in artist_time.items()]
        result.sort(key=lambda x: x[1], reverse=True)
        return result[:n]

    #Q7
    def user_top_genre(self, user_id: str) -> tuple[str, float] | None:
        """Returns the user's most listened-to genre and its share of total listening time (as a percentage).
        Returns None if the user does not exist or has no sessions."""
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
        """Returns collaborative playlists that contain tracks from more than `threshold` unique artists."""
        def unique_artists(total):
            return {track.artist.artist_id for track in total if isinstance(track, Song) }
        return [ playlist for playlist in self._playlists.values()
                 if isinstance(playlist, CollaborativePlaylist) and len(unique_artists(playlist.tracks)) > threshold]
    #Q9
    def avg_tracks_per_playlist_type(self) -> dict[str, float]:
        """Computes the average number of tracks per playlist type,
        returning a dictionary for regular and collaborative playlists."""
        playlist_total = playlist_count = 0
        collab_total = collab_count = 0
        for playlist in self._playlists.values():
            if isinstance(playlist, CollaborativePlaylist):
                collab_total += len(playlist.tracks)
                collab_count += 1
            else:
                playlist_total += len(playlist.tracks)
                playlist_count += 1
        return {
            "Playlist": float(playlist_total / playlist_count) if playlist_count else 0.0,
            "CollaborativePlaylist": float(collab_total / collab_count) if collab_count else 0.0}

    #Q10
    def users_who_completed_albums(self) -> list[tuple[User, list[str]]]:
        """Returns users who have listened to all tracks of at least one album,
        along with the list of completed album titles."""
        result = []
        for user in self._users.values():
            user_tracks = {s.track.track_id for s in user.sessions}
            completed_albums = []
            for album in self._albums.values():
                album_tracks = album.track_ids()
                if album_tracks and album_tracks.issubset(user_tracks):
                    completed_albums.append(album.title)
            if completed_albums:
                result.append((user, completed_albums))
        return result
