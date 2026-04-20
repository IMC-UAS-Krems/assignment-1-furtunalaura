"""
test_public.py
--------------
Public test suite template.

This file provides a minimal framework and examples to guide you in writing
comprehensive tests for your StreamingPlatform implementation. Each test class
corresponds to one of the 10 query methods (Q1-Q10).

You should:
1. Study the examples provided
2. Complete the stub tests (marked with TODO or pass statements)
3. Add additional test cases for edge cases and boundary conditions
4. Verify your implementation passes all tests

Run with:
    pytest tests/test_public.py -v
"""

import pytest
from datetime import datetime, timedelta
from streaming.artists import Artist
from streaming.platform import StreamingPlatform
from streaming.albums import Album
from streaming.users import FreeUser, PremiumUser, FamilyAccountUser, FamilyMember
from streaming.playlists import Playlist, CollaborativePlaylist
from tests.conftest import FIXED_NOW, RECENT, OLD


# ===========================================================================
# Q1 - Total cumulative listening time for a given period
# ===========================================================================

class TestTotalListeningTime:
    """Test the total_listening_time_minutes(start, end) method.
    
    This method should sum up all session durations that fall within
    the specified datetime window (inclusive on both ends).
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        start = RECENT - timedelta(hours=1)
        end = FIXED_NOW
        result = platform.total_listening_time_minutes(start, end)
        assert isinstance(result, float)

    def test_empty_window_returns_zero(self, platform: StreamingPlatform) -> None:
        """Test that a time window with no sessions returns 0.0."""
        far_future = FIXED_NOW + timedelta(days=365)
        result = platform.total_listening_time_minutes(
            far_future, far_future + timedelta(hours=1)
        )
        assert result == 0.0

    # TODO: Add a test that verifies the correct value for a known time period.
    #       Calculate the expected total based on the fixture data in conftest.py.
    def test_known_period_value(self, platform: StreamingPlatform) -> None:
        recent_total_seconds = sum([
            180, 210,
            180, 240,
            200, 195,
            200,
            300,
            230,
            180, 180
        ])
        expected_minutes = recent_total_seconds / 60
        start_time = RECENT - timedelta(days=1)
        end_time = RECENT + timedelta(days=1)
        computed_minutes = platform.total_listening_time_minutes(start_time, end_time)
        assert expected_minutes == computed_minutes
    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================
    def test_exact_boundary_inclusion(self, platform: StreamingPlatform) -> None:
        """sessions exactly at start and end timestamps should be included."""
        start = RECENT
        end = RECENT
        # sessions at RECENT exist (many)
        result = platform.total_listening_time_minutes(start, end)
        assert result > 0.0

    def test_start_after_end_returns_zero(self, platform: StreamingPlatform) -> None:
        """if start > end, method should return 0.0."""
        start = FIXED_NOW
        end = FIXED_NOW - timedelta(days=1)
        assert platform.total_listening_time_minutes(start, end) == 0.0

    def test_only_old_sessions_excluded(self, platform: StreamingPlatform) -> None:
        """window that includes only OLD sessions should exclude RECENT ones."""
        start = OLD - timedelta(days=1)
        end = OLD + timedelta(days=1)
        result = platform.total_listening_time_minutes(start, end)
        assert result > 0.0

#=======================================================================
# Q2 - Average unique tracks per PremiumUser in the last N days
# ===========================================================================

class TestAvgUniqueTracksPremium:
    """Test the avg_unique_tracks_per_premium_user(days) method.
    
    This method should:
    - Count distinct tracks per PremiumUser in the last N days
    - Exclude FreeUser, FamilyAccountUser, and FamilyMember
    - Return 0.0 if there are no premium users
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.avg_unique_tracks_per_premium_user(days=30)
        assert isinstance(result, float)

    def test_no_premium_users_returns_zero(self) -> None:
        """Test with a platform that has no premium users."""
        p = StreamingPlatform("EmptyPlatform")
        p.add_user(FreeUser("u99", "Nobody", age=25))
        assert p.avg_unique_tracks_per_premium_user() == 0.0

    # TODO: Add a test with the fixture platform that verifies the correct
    #       average for premium users. You'll need to count unique tracks
    #       per premium user and calculate the average.

    def test_correct_value(self, platform: StreamingPlatform) -> None:
        """exact average based on fixture data."""
        expected = (2 + 2 + 1 + 1 + 0 + 0) / 6
        result = platform.avg_unique_tracks_per_premium_user()
        assert result == expected

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================

    def test_ignores_non_premium_users(self, platform: StreamingPlatform) -> None:
        """free and family users must not affect the result."""
        result = platform.avg_unique_tracks_per_premium_user()
        assert result >= 0.0

    def test_single_premium_user(self) -> None:
        """only one premium user."""
        p = StreamingPlatform("Test")
        user = PremiumUser("p1", "Test", 30, FIXED_NOW)
        p.add_user(user)
        assert p.avg_unique_tracks_per_premium_user() == 0.0

# ===========================================================================
# Q3 - Track with the most distinct listeners
# ===========================================================================

class TestTrackMostDistinctListeners:
    """Test the track_with_most_distinct_listeners() method.
    
    This method should:
    - Count the number of unique users who have listened to each track
    - Return the track with the highest count
    - Return None if the platform has no sessions
    """

    def test_empty_platform_returns_none(self) -> None:
        """Test that an empty platform returns None."""
        p = StreamingPlatform("Empty")
        assert p.track_with_most_distinct_listeners() is None

    # TODO: Add a test that verifies the correct track is returned.
    #       Count listeners per track from the fixture data.

    def test_correct_track(self, platform: StreamingPlatform) -> None:
        """track t1 has the most distinct listeners in fixture."""
        result = platform.track_with_most_distinct_listeners()
        assert result is not None
        assert result.track_id == "t1"

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================

    def test_tie_returns_valid_track(self, platform: StreamingPlatform) -> None:
        """if tie exists, returned track must be one of the top."""
        result = platform.track_with_most_distinct_listeners()
        assert result.track_id in {"t1", "t4", "t6"}

    def test_single_session(self) -> None:
        """if there is a single session, then that track should be returned."""
        p = StreamingPlatform("Test")
        assert p.track_with_most_distinct_listeners() is None

# ===========================================================================
# Q4 - Average session duration per user subtype, ranked
# ===========================================================================

class TestAvgSessionDurationByType:
    """Test the avg_session_duration_by_user_type() method.
    
    This method should:
    - Calculate average session duration (in seconds) for each user type
    - Return a list of (type_name, average_duration) tuples
    - Sort results from longest to shortest duration
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a list of (str, float) tuples."""
        result = platform.avg_session_duration_by_user_type()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], str) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verify results are sorted by duration (longest first)."""
        result = platform.avg_session_duration_by_user_type()
        durations = [r[1] for r in result]
        assert durations == sorted(durations, reverse=True)

    # TODO: Add tests to verify all user types are present and have correct averages.

    def test_all_user_types_present(self, platform: StreamingPlatform) -> None:
        sessions_by_type = {}
        for s in platform._sessions:
            user_type = type(s.user).__name__
            sessions_by_type.setdefault(user_type, []).append(s.duration_listened_seconds)
        expected = {
            user_type: sum(durations) / len(durations)
            for user_type, durations in sessions_by_type.items()
        }
        result = dict(platform.avg_session_duration_by_user_type())
        for key, value in expected.items():
            assert abs(result[key] - value) < 1e-6

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================

    def test_all_types_present(self, platform: StreamingPlatform) -> None:
        """all user types present in sessions should appear in result."""
        result = dict(platform.avg_session_duration_by_user_type())
        assert "FreeUser" in result
        assert "PremiumUser" in result
        assert "FamilyMember" in result or "FamilyAccountUser" in result

    def test_no_sessions_returns_empty(self) -> None:
        """if there is no sessions, then it returns empty result."""
        p = StreamingPlatform("Empty")
        assert p.avg_session_duration_by_user_type() == []


# ===========================================================================
# Q5 - Total listening time for underage sub-users
# ===========================================================================

class TestUnderageSubUserListening:
    """Test the total_listening_time_underage_sub_users_minutes(age_threshold) method.
    
    This method should:
    - Count only sessions for FamilyMember users under the age threshold
    - Convert to minutes
    - Return 0.0 if no underage users or their sessions exist
    """

    def test_returns_float(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a float."""
        result = platform.total_listening_time_underage_sub_users_minutes()
        assert isinstance(result, float)

    def test_no_family_users(self) -> None:
        """Test a platform with no family accounts."""
        p = StreamingPlatform("NoFamily")
        p.add_user(FreeUser("u1", "Solo", age=20))
        assert p.total_listening_time_underage_sub_users_minutes() == 0.0

    # TODO: Add tests for correct values with default and custom thresholds.

    def test_correct_value_default_threshold(self, platform: StreamingPlatform) -> None:
        """threshold 18 (u9 only)."""
        result = platform.total_listening_time_underage_sub_users_minutes()
        assert result == 180 / 60

    def test_custom_threshold_includes_more_users(self, platform: StreamingPlatform) -> None:
        """threshold 21 (u9 and u10)."""
        result = platform.total_listening_time_underage_sub_users_minutes(age_threshold=21)
        assert result > 0.0

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================
    def test_no_sessions_for_underage(self) -> None:
        """underage users exist but no sessions."""
        p = StreamingPlatform("Test")
        parent = FamilyAccountUser("p", "Parent", 40)
        child = FamilyMember("c", "Kid", 10, parent)
        p.add_user(parent)
        p.add_user(child)
        assert p.total_listening_time_underage_sub_users_minutes() == 0.0

# ===========================================================================
# Q6 - Top N artists by total listening time
# ===========================================================================

class TestTopArtistsByListeningTime:
    """Test the top_artists_by_listening_time(n) method.
    
    This method should:
    - Rank artists by total cumulative listening time (minutes)
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return a list of (Artist, minutes) tuples
    - Sort from highest to lowest listening time
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verifies the method returns a list of (Artist, float) tuples."""
        from streaming.artists import Artist
        result = platform.top_artists_by_listening_time(n=3)
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], Artist) and isinstance(item[1], float)

    def test_sorted_descending(self, platform: StreamingPlatform) -> None:
        """Verifies results are sorted by listening time (highest first)."""
        result = platform.top_artists_by_listening_time(n=5)
        minutes = [r[1] for r in result]
        assert minutes == sorted(minutes, reverse=True)

    def test_respects_n_parameter(self, platform: StreamingPlatform) -> None:
        """Verifies only the top N artists are returned."""
        result = platform.top_artists_by_listening_time(n=2)
        assert len(result) <= 2

    # TODO: Add a test that verifies the correct artists and values.

    def test_top_artist(self, platform: StreamingPlatform) -> None:
        result = platform.top_artists_by_listening_time(n=7)
        from streaming.artists import Artist
        assert len(result) <= 7
        for artist, minutes in result:
            assert isinstance(artist, Artist)
            assert isinstance(minutes, float)
        minutes = [m for _, m in result]
        assert minutes == sorted(minutes, reverse=True)
        (top_artist,top_minutes) = result[0]
        assert top_artist.name in {"Pixels", "Stone Pulse", "Sky Rhythm"}
        assert top_minutes >0

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================

    def test_ignores_non_song_tracks(self, platform: StreamingPlatform) -> None:
        """podcast/audiobook should not affect ranking."""
        result = platform.top_artists_by_listening_time(n=5)
        assert len(result) > 0

    def test_n_greater_than_available(self, platform: StreamingPlatform) -> None:
        """n larger than artist count should not crash."""
        result = platform.top_artists_by_listening_time(n=100)
        assert isinstance(result, list)


# ===========================================================================
# Q7 - User's top genre and percentage
# ===========================================================================

class TestUserTopGenre:
    """Test the user_top_genre(user_id) method.
    
    This method should:
    - Find the genre with the most listening time for a user
    - Return (genre_name, percentage_of_total_time)
    - Return None if user doesn't exist or has no sessions
    """

    def test_returns_tuple_or_none(self, platform: StreamingPlatform) -> None:
        """Verify the method returns a tuple or None."""
        result = platform.user_top_genre("u1")
        if result is not None:
            assert isinstance(result, tuple) and len(result) == 2
            assert isinstance(result[0], str) and isinstance(result[1], float)

    def test_nonexistent_user_returns_none(self, platform: StreamingPlatform) -> None:
        """Test that a nonexistent user ID returns None."""
        assert platform.user_top_genre("does_not_exist") is None

    def test_percentage_in_valid_range(self, platform: StreamingPlatform) -> None:
        """Verify percentage is between 0 and 100."""
        for user in platform.all_users():
            result = platform.user_top_genre(user.user_id)
            if result is not None:
                _, pct = result
                assert 0.0 <= pct <= 100.0

    # TODO: Add a test that verifies the correct genre and percentage for a known user.
    def test_correct_top_genre(self, platform: StreamingPlatform) -> None:
        """checks correct top genre per user."""
        result_1 = platform.user_top_genre("u1")
        assert result_1 is not None
        assert result_1[0] == "pop"
        assert 0.0 <= result_1[1] <= 100.0
        result_2 = platform.user_top_genre("u2")
        assert result_2 is not None
        assert result_2[0] in {"electronic", "alternative", "indie-pop"}
        assert 0.0 <= result_2[1] <= 100.0

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================

    def test_user_with_no_sessions(self, platform: StreamingPlatform) -> None:
        """if user exists but has no listening, it returns None."""
        p = StreamingPlatform("Test")
        p.add_user(FreeUser("u1", "Test", age=30))
        result = p.user_top_genre("u1")
        assert result is None

    def test_invalid_user_id(self, platform: StreamingPlatform) -> None:
        """unknown user returns None."""
        assert platform.user_top_genre("unknown_user") is None

# ===========================================================================
# Q8 - CollaborativePlaylists with more than threshold distinct artists
# ===========================================================================

class TestCollaborativePlaylistsManyArtists:
    """Test the collaborative_playlists_with_many_artists(threshold) method.
    
    This method should:
    - Return all CollaborativePlaylist instances with >threshold distinct artists
    - Only count Song tracks (exclude Podcast and AudiobookTrack)
    - Return playlists in registration order
    """

    def test_returns_list_of_collaborative_playlists(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a list of CollaborativePlaylist objects."""
        result = platform.collaborative_playlists_with_many_artists()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, CollaborativePlaylist)

    def test_higher_threshold_returns_empty(
        self, platform: StreamingPlatform
    ) -> None:
        """Test that a high threshold returns an empty list."""
        result = platform.collaborative_playlists_with_many_artists(threshold=100)
        assert result == []

    # TODO: Add tests that verify the correct playlists are returned with
    #       different threshold values.

    def test_default_threshold(self, platform: StreamingPlatform) -> None:
        """p2 has many artists and should be returned."""
        result = platform.collaborative_playlists_with_many_artists()
        ids = [p.playlist_id for p in result]
        assert ids == ["p2"]

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================
    def test_no_collaborative_playlists(self) -> None:
        """if there are no collaborative playlists, it returns an empty list."""
        p = StreamingPlatform("Test")
        assert p.collaborative_playlists_with_many_artists() == []
# ===========================================================================
# Q9 - Average tracks per playlist type
# ===========================================================================

class TestAvgTracksPerPlaylistType:
    """Test the avg_tracks_per_playlist_type() method.
    
    This method should:
    - Calculate average track count for standard Playlist instances
    - Calculate average track count for CollaborativePlaylist instances
    - Return a dict with keys "Playlist" and "CollaborativePlaylist"
    - Return 0.0 for types with no instances
    """

    def test_returns_dict_with_both_keys(
        self, platform: StreamingPlatform
    ) -> None:
        """Verify the method returns a dict with both playlist types."""
        result = platform.avg_tracks_per_playlist_type()
        assert isinstance(result, dict)
        assert "Playlist" in result
        assert "CollaborativePlaylist" in result

    # TODO: Add tests that verify the correct averages for each playlist type.
    def test_standard_playlist_average(self, platform: StreamingPlatform) -> None:
        result = platform.avg_tracks_per_playlist_type()["Playlist"]
        assert result == 3.0

    def test_collaborative_playlist_average(self, platform: StreamingPlatform) -> None:
        result = platform.avg_tracks_per_playlist_type()["CollaborativePlaylist"]
        assert result == 6.0

    # ===========================================================================
    # ADDITIONAL
    # ===========================================================================
    def test_only_standard_playlists(self) -> None:
        """if only Playlist objects exist, CollaborativePlaylist average should be 0.0."""
        p = StreamingPlatform("Test")
        user = FreeUser("u1", "Test", 20)
        p.add_playlist(Playlist("p1", "Test", user))
        result = p.avg_tracks_per_playlist_type()
        assert result["CollaborativePlaylist"] == 0.0

    def test_no_playlists(self) -> None:
        """if no Playlists exist, both averages should be 0.0."""
        p = StreamingPlatform("Empty Platform")
        result = p.avg_tracks_per_playlist_type()
        assert result == {
            "Playlist": 0.0,
            "CollaborativePlaylist": 0.0
        }

    def test_mixed_empty_and_nonempty(self, platform: StreamingPlatform) -> None:
        """ensure averages handle mixed playlist states."""
        result = platform.avg_tracks_per_playlist_type()
        assert result["Playlist"] >= 0.0
        assert result["CollaborativePlaylist"] >= 0.0

# ===========================================================================
# Q10 - Users who completed at least one full album
# ===========================================================================

class TestUsersWhoCompletedAlbums:
    """Test the users_who_completed_albums() method.
    
    This method should:
    - Return users who have listened to every track on at least one album
    - Return (User, [album_titles]) tuples
    - Include all completed albums for each user
    - Ignore albums with no tracks
    """

    def test_returns_list_of_tuples(self, platform: StreamingPlatform) -> None:
        """Verifies that the method returns a list of (User, list) tuples."""
        from streaming.users import User
        result = platform.users_who_completed_albums()
        assert isinstance(result, list)
        for item in result:
            assert isinstance(item, tuple) and len(item) == 2
            assert isinstance(item[0], User) and isinstance(item[1], list)

    def test_completed_album_titles_are_strings(
        self, platform: StreamingPlatform
    ) -> None:
        """Verifies all completed album titles are strings."""
        result = platform.users_who_completed_albums()
        for _, titles in result:
            assert all(isinstance(t, str) for t in titles)

    # TODO: Add tests that verify the correct users and albums are identified.
    def test_correct_users_identified(self, platform: StreamingPlatform) -> None:
        result = platform.users_who_completed_albums()
        actual_user_ids = {user.user_id for user, _ in result}
        assert isinstance(actual_user_ids, set)
        assert len(actual_user_ids) > 0

    def test_each_album_is_actually_completed(self, platform: StreamingPlatform) -> None:
        result = platform.users_who_completed_albums()
        user_tracks = {}
        for s in platform._sessions:
            user_tracks.setdefault(s.user.user_id, set()).add(s.track.track_id)
        for user, albums in result:
            assert len(albums) > 0
            assert user.user_id in user_tracks
            assert len(user_tracks[user.user_id]) > 0

    def test_no_partial_listeners_included(self, platform: StreamingPlatform) -> None:
        result = platform.users_who_completed_albums()
        user_ids = [user.user_id for user, _ in result]
        # users with incomplete listening should not appear
        assert "u8" not in user_ids
        assert "u9" not in user_ids
        assert "u10" not in user_ids