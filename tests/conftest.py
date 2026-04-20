"""
conftest.py
-----------
Shared pytest fixtures used by both the public and private test suites.
"""

import pytest
from datetime import date, datetime, timedelta

from streaming.platform import StreamingPlatform
from streaming.artists import Artist
from streaming.albums import Album
from streaming.tracks import (
    AlbumTrack,
    SingleRelease,
    InterviewEpisode,
    NarrativeEpisode,
    AudiobookTrack,
)
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.sessions import ListeningSession
from streaming.playlists import Playlist, CollaborativePlaylist


# ---------------------------------------------------------------------------
# Helper - timestamps relative to the real current time so that the
# "last 30 days" window in Q2 always contains RECENT sessions.
# ---------------------------------------------------------------------------
FIXED_NOW = datetime.now().replace(microsecond=0)
RECENT = FIXED_NOW - timedelta(days=10)   # well within 30-day window
OLD    = FIXED_NOW - timedelta(days=60)   # outside 30-day window


@pytest.fixture
def platform() -> StreamingPlatform:
    """Return a fully populated StreamingPlatform instance."""
    platform = StreamingPlatform("TestStream")

    # ------------------------------------------------------------------
    # Artists
    # ------------------------------------------------------------------
    pixels  = Artist("a1", "Pixels",    genre="pop")
    a2 = Artist("a2", "Stone Pulse", genre="alternative")
    a3 = Artist("a3", "Sky Rhythm", genre="indie-pop")
    a4 = Artist("a4", "Iron Echo", genre="metal")
    a5 = Artist("a5", "Golden Baroque", genre="baroque")
    a6 = Artist("a6", "Blue Tempo", genre="blues")
    a7 = Artist("a7", "Forest Strings", genre="acoustic")
    for a in (pixels, a2, a3, a4, a5, a6, a7):
        platform.add_artist(a)

    # ------------------------------------------------------------------
    # Albums & AlbumTracks
    # ------------------------------------------------------------------
    dd = Album("alb1", "Digital Dreams", artist=pixels, release_year=2022)
    al1 = Album("alb2", "Midnight Circuits", artist=a2, release_year=2022)
    al2 = Album("alb3", "Synthetic Echoes", artist=a3, release_year=2021)
    al3 = Album("alb4", "Voltage Dreams", artist=a4, release_year=2023)
    al4 = Album("alb5", "Baroque Visions", artist=a5, release_year=2018)
    al5 = Album("alb6", "Blue Night Sessions", artist=a6, release_year=2020)
    al6 = Album("alb7", "Acoustic Tales", artist=a7, release_year=2023)
    t1 = AlbumTrack("t1", "Pixel Rain",      180, "pop",  pixels, track_number=1)
    t2 = AlbumTrack("t2", "Grid Horizon",    210, "pop",  pixels, track_number=2)
    t3 = AlbumTrack("t3", "Vector Fields",   195, "pop",  pixels, track_number=3)
    t4 = AlbumTrack("t4", "Iron Waves", 240, "alternative", artist=a2, track_number=1)
    t5 = AlbumTrack("t5", "Broken Signals", 200, "alternative", artist=a2, track_number=2)
    t6 = AlbumTrack("t6", "Neon Flow", 300, "indie-pop", artist=a3, track_number=1)
    t7 = AlbumTrack("t7", "Pulse Reactor", 260, "electronic", artist=a4, track_number=1)
    t8 = AlbumTrack("t8", "Circuit Drift", 220, "electronic", artist=a4, track_number=2)
    t9 = AlbumTrack("t9", "Golden Prelude", 400, "baroque", artist=a5, track_number=1)
    t10 = AlbumTrack("t10", "Silent Fugue", 500, "baroque", artist=a5, track_number=2)
    t11 = AlbumTrack("t11", "Midnight Brass", 250, "blues", artist=a6, track_number=1)
    t12 = AlbumTrack("t12", "Slow River", 280, "blues", artist=a6, track_number=2)
    t13 = AlbumTrack("t13", "Forest Light", 230, "acoustic", artist=a7, track_number=1)
    t14 = AlbumTrack("t14", "Evening Wind", 210, "acoustic", artist=a7, track_number=2)
    for album, tracks in [
        (dd, [t1, t2, t3]),
        (al1, [t4, t5]),
        (al2, [t6]),
        (al3, [t7, t8]),
        (al4, [t9, t10]),
        (al5, [t11, t12]),
        (al6, [t13, t14])
    ]:
        for track in tracks:
            album.add_track(track)
            platform.add_track(track)
            album.artist.add_track(track)
        platform.add_album(album)

    # ------------------------------------------------------------------
    # Users
    # ------------------------------------------------------------------
    alice = FreeUser("u1", "Alice", age=30)
    bob = PremiumUser("u2", "Bob", age=25, subscription_start=date(2023, 1, 1))
    premium_a = PremiumUser("u3", "Liam", 29, date(2024, 3, 15))
    premium_b = PremiumUser("u4", "Sophia", 34, date(2022, 9, 10))
    premium_c = PremiumUser("u5", "Noah", 23, date(2026, 2, 5))
    premium_d = PremiumUser("u6", "Emma", 41, date(2025, 6, 20))
    premium_e = PremiumUser("u7", "Oliver", 32, date(2023, 11, 11))
    guardian = FamilyAccountUser("u8", "Jordan", age=42)
    kid_a = FamilyMember("u9", "Mia", age=12, parent=guardian)
    kid_b = FamilyMember("u10", "Ethan", age=15, parent=guardian)
    adult_member = FamilyMember("u11", "Lucas", age=22, parent=guardian)

    for user in (
            alice, bob,
            premium_a, premium_b, premium_c, premium_d, premium_e,
            guardian, kid_a, kid_b, adult_member
    ):
        platform.add_user(user)

    # ------------------------------------------------------------------
    # Listening Sessions
    # -----------------------------------------------------------------
    sessions = [
        ListeningSession("s1", alice, t1, RECENT, 180),
        ListeningSession("s2", alice, t2, RECENT, 210),
        ListeningSession("s3", alice, t3, OLD, 195),
        ListeningSession("s4", bob, t1, RECENT, 180),
        ListeningSession("s5", bob, t4, RECENT, 240),
        ListeningSession("s6", bob, t6, OLD, 300),
        ListeningSession("s7", premium_a, t2, RECENT, 200),
        ListeningSession("s8", premium_a, t3, RECENT, 195),
        ListeningSession("s9", premium_b, t5, RECENT, 200),
        ListeningSession("s10", premium_b, t8, OLD, 220),
        ListeningSession("s11", premium_c, t6, RECENT, 300),
        ListeningSession("s12", guardian, t13, RECENT, 230),
        ListeningSession("s13", kid_a, t1, RECENT, 180),
        ListeningSession("s14", adult_member, t1, RECENT, 180)]
    for session in sessions:
        platform.record_session(session)
    # ------------------------------------------------------------------
    # Tracks
    # ------------------------------------------------------------------
    single = SingleRelease("t11", "Neon Single", 210, "synthwave", pixels, release_date=date(2026, 3, 3))
    pixels.add_track(single)
    interview = InterviewEpisode("t12", "Tech Talk OOP", 1800, "tech", host="Alex", guest="Dr. Novak")
    narrative = NarrativeEpisode("t13", "Valley Story", 1500, "story", "Morgan", season=2, episode_number=1)
    audiobook = AudiobookTrack("t14", "Sound History", 2200, "history", author="Jordan", narrator="Casey")
    for track in (single, interview, narrative, audiobook):
        platform.add_track(track)

    # ------------------------------------------------------------------
    # Playlists
    # ------------------------------------------------------------------
    p1 = Playlist("p1", "Chill Mix", alice)

    p1.add_track(t1)
    p1.add_track(t4)
    p1.add_track(t6)

    platform.add_playlist(p1)

    p2 = CollaborativePlaylist("p2", "Shared Vibes", bob)

    p2.add_track(t1)
    p2.add_track(t4)
    p2.add_track(t5)
    p2.add_track(t6)
    p2.add_track(t7)
    p2.add_track(t8)
    p2.add_contributor(premium_a)
    p2.add_contributor(premium_b)
    p2.add_contributor(kid_a)
    p2.add_contributor(guardian)
    p2.remove_contributor(premium_b)
    p2.remove_contributor(bob)

    platform.add_playlist(p2)
    return platform

@pytest.fixture
def fixed_now() -> datetime:
    """Expose the shared FIXED_NOW constant to tests."""
    return FIXED_NOW


@pytest.fixture
def recent_ts() -> datetime:
    return RECENT


@pytest.fixture
def old_ts() -> datetime:
    return OLD
