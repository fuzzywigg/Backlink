"""Unit tests for LIVE process_transcripts parsing/aggregation helpers.

Covers pure helpers only — no network, Gemini, OntologyManager, or write_outputs.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from process_transcripts import parse_full_file, parse_log_line, process_data


@pytest.mark.unit
class TestParseLogLine:
    """parse_log_line() timestamp + JSON extraction."""

    def test_parses_dict_payload(self) -> None:
        line = '[14:22:01] {"segment_type": "speech", "transcript": "hello"}'
        ts, data = parse_log_line(line)
        assert ts == "14:22:01"
        assert data == {"segment_type": "speech", "transcript": "hello"}

    def test_parses_list_payload(self) -> None:
        line = '[09:00:00] [{"segment_type": "music"}, {"segment_type": "speech"}]'
        ts, data = parse_log_line(line)
        assert ts == "09:00:00"
        assert isinstance(data, list)
        assert len(data) == 2

    def test_returns_none_without_timestamp(self) -> None:
        assert parse_log_line('{"segment_type": "speech"}') == (None, None)

    def test_returns_none_for_invalid_json(self) -> None:
        assert parse_log_line("[12:00:00] not-json") == (None, None)

    def test_strips_whitespace(self) -> None:
        line = '  [01:02:03] {"ok": true}  \n'
        ts, data = parse_log_line(line)
        assert ts == "01:02:03"
        assert data == {"ok": True}


@pytest.mark.unit
class TestParseFullFile:
    """parse_full_file() multi-block transcript log splitting."""

    def test_parses_multiple_timestamped_blocks(self, tmp_path: Path) -> None:
        log = tmp_path / "transcript_log.txt"
        log.write_text(
            "[10:00:00]\n"
            '{"segment_type": "speech", "transcript": "open"}\n'
            "[10:05:00]\n"
            '{"segment_type": "music", "song_info": "A - B"}\n',
            encoding="utf-8",
        )
        entries = parse_full_file(str(log))
        assert len(entries) == 2
        assert entries[0][0] == "10:00:00"
        assert entries[0][1]["transcript"] == "open"
        assert entries[1][0] == "10:05:00"
        assert entries[1][1]["song_info"] == "A - B"

    def test_skips_empty_and_malformed_blocks(self, tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
        log = tmp_path / "messy.txt"
        log.write_text(
            "[11:00:00]\n"
            "\n"
            "[11:01:00]\n"
            "{not valid json}\n"
            "[11:02:00]\n"
            '{"segment_type": "speech", "transcript": "ok"}\n',
            encoding="utf-8",
        )
        entries = parse_full_file(str(log))
        assert len(entries) == 1
        assert entries[0][0] == "11:02:00"
        captured = capsys.readouterr()
        assert "Failed to parse JSON for 11:01:00" in captured.out

    def test_parses_list_block(self, tmp_path: Path) -> None:
        log = tmp_path / "list_block.txt"
        payload = [{"segment_type": "music", "song_info": "X - Y"}]
        log.write_text(f"[12:30:00]\n{json.dumps(payload)}\n", encoding="utf-8")
        entries = parse_full_file(str(log))
        assert len(entries) == 1
        assert entries[0][1] == payload


@pytest.mark.unit
class TestProcessData:
    """process_data() song aggregation and continuity events."""

    def test_splits_artist_title_and_builds_continuity(self) -> None:
        entries: list[tuple[str, dict[str, Any]]] = [
            (
                "08:15:00",
                {
                    "segment_type": "music",
                    "transcript": None,
                    "song_info": "Radiohead - Creep",
                    "notes": "opener",
                },
            )
        ]
        songs, continuity = process_data(entries)
        assert songs == [
            {
                "timestamp": "08:15:00",
                "artist": "Radiohead",
                "title": "Creep",
                "raw_info": "Radiohead - Creep",
            }
        ]
        assert len(continuity) == 1
        assert continuity[0]["type"] == "music"
        assert continuity[0]["notes"] == "opener"

    def test_unknown_artist_when_no_dash_separator(self) -> None:
        entries = [("09:00:00", {"song_info": "Instrumental Loop", "segment_type": "music"})]
        songs, _ = process_data(entries)
        assert songs[0]["artist"] == "Unknown"
        assert songs[0]["title"] == "Instrumental Loop"

    def test_skips_unknown_and_missing_song_info(self) -> None:
        entries = [
            ("10:00:00", {"segment_type": "speech", "transcript": "hi", "song_info": None}),
            ("10:01:00", {"segment_type": "music", "song_info": "Unknown"}),
            ("10:02:00", {"segment_type": "music", "song_info": "Band - Track"}),
        ]
        songs, continuity = process_data(entries)
        assert len(songs) == 1
        assert songs[0]["title"] == "Track"
        assert len(continuity) == 3

    def test_expands_list_payloads(self) -> None:
        entries = [
            (
                "13:00:00",
                [
                    {"segment_type": "speech", "transcript": "welcome"},
                    {"segment_type": "music", "song_info": "Artist - Song"},
                ],
            )
        ]
        songs, continuity = process_data(entries)
        assert len(songs) == 1
        assert len(continuity) == 2
        assert continuity[0]["transcript"] == "welcome"
        assert continuity[1]["song_info"] == "Artist - Song"

    def test_empty_entries(self) -> None:
        songs, continuity = process_data([])
        assert songs == []
        assert continuity == []
