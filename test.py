import pandas as pd
import pytest


def test_playlist_tracks():
    df = pd.read_csv("playlist_tracks.csv")
    assert not df.empty, "The DataFrame should not be empty"
    assert "id" in df.columns, "DataFrame should contain 'id' column"
    assert "name" in df.columns, "DataFrame should contain 'name' column"
    assert "added_at" in df.columns, "DataFrame should contain 'added_at' column"
    assert "album_id" in df.columns, "DataFrame should contain 'album_id' column"
    assert "album_name" in df.columns, "DataFrame should contain 'album_name' column"
    assert "artist_id" in df.columns, "DataFrame should contain 'artist_id' column"
    assert "artists_name" in df.columns, (
        "DataFrame should contain 'artists_name' column"
    )
    assert "duration_ms" in df.columns, "DataFrame should contain 'duration_ms' column"
    assert "is_explicit" in df.columns, "DataFrame should contain 'is_explicit' column"
    assert "popularity" in df.columns, "DataFrame should contain 'popularity' column"


if __name__ == "__main__":
    pytest.main([__file__])
