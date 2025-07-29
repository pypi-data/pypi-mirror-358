"""
Tests for utility functions in wakatimer.py
"""
import os
import json
import tempfile
import time
from pathlib import Path
import pytest
from unittest.mock import patch, mock_open
import wakatimer
from wakatimer import (
    format_time,
    print_logo,
    load_project_template,
    create_default_templates,
)
from wakatimer import VisualTimeline


@pytest.fixture
def change_test_dir():
    """Fixture to temporarily change the working directory for a test."""
    original_cwd = os.getcwd()
    try:
        yield lambda new_dir: os.chdir(new_dir)
    finally:
        os.chdir(original_cwd)

class TestFormatTime:
    """Test the format_time utility function."""
    
    def test_zero_seconds(self):
        """Test formatting zero seconds."""
        assert format_time(0) == "00:00:00"
    
    def test_seconds_only(self):
        """Test formatting seconds only."""
        assert format_time(45) == "00:00:45"
    
    def test_minutes_and_seconds(self):
        """Test formatting minutes and seconds."""
        assert format_time(125) == "00:02:05"  # 2 minutes, 5 seconds
    
    def test_hours_minutes_seconds(self):
        """Test formatting hours, minutes, and seconds."""
        assert format_time(3661) == "01:01:01"  # 1 hour, 1 minute, 1 second
        assert format_time(7325) == "02:02:05"  # 2 hours, 2 minutes, 5 seconds
    
    def test_large_values(self):
        """Test formatting large time values."""
        assert format_time(86400) == "24:00:00"  # 24 hours
        assert format_time(90061) == "25:01:01"  # 25 hours, 1 minute, 1 second
    
    def test_float_input(self):
        """Test formatting float input."""
        assert format_time(3661.7) == "01:01:01"  # Should truncate decimals


class TestPrintLogo:
    """Test the print_logo function."""
    
    def test_prints_logo(self, capsys):
        """Test that logo is printed with correct content."""
        print_logo()
        captured = capsys.readouterr()
        
        assert "WAKATIMER" in captured.out
        assert "Version 2.0.2" in captured.out
        assert "Sukarth Achaya" in captured.out
        assert "Retroactive Time Tracking Data Generator" in captured.out
        assert "╔" in captured.out  # Check for box drawing characters


class TestLoadProjectTemplate:
    """Test the load_project_template function."""
    
    def test_load_existing_template(self, temp_dirs, change_test_dir):
        """Test loading an existing template file."""
        src_dir, _ = temp_dirs

        # Create templates directory and file
        templates_dir = src_dir / "templates"
        templates_dir.mkdir()

        template_data = {
            "name": "Test Template",
            "description": "A test template",
            "file_priorities": {"core": ["*.py"]}
        }

        template_file = templates_dir / "test.json"
        template_file.write_text(json.dumps(template_data))

        change_test_dir(src_dir)
        result = load_project_template("test")
        assert result == template_data
    
    def test_load_nonexistent_template(self, temp_dirs, change_test_dir):
        """Test loading a non-existent template file."""
        src_dir, _ = temp_dirs

        change_test_dir(src_dir)
        result = load_project_template("nonexistent")
        assert result == {}
    
    def test_load_template_invalid_json(self, temp_dirs, change_test_dir):
        """Test loading a template with invalid JSON."""
        src_dir, _ = temp_dirs

        # Create templates directory and invalid JSON file
        templates_dir = src_dir / "templates"
        templates_dir.mkdir()

        template_file = templates_dir / "invalid.json"
        template_file.write_text("{ invalid json }")

        change_test_dir(src_dir)
        # Should handle JSON decode error gracefully
        with pytest.raises(json.JSONDecodeError):
            load_project_template("invalid")


class TestCreateDefaultTemplates:
    """Test the create_default_templates function."""
    
    def test_creates_templates_directory(self, temp_dirs, change_test_dir):
        """Test that templates directory is created."""
        src_dir, _ = temp_dirs

        change_test_dir(src_dir)
        create_default_templates()

        templates_dir = src_dir / "templates"
        assert templates_dir.exists()
        assert templates_dir.is_dir()
    
    def test_creates_web_app_template(self, temp_dirs, change_test_dir):
        """Test that web app template is created correctly."""
        src_dir, _ = temp_dirs

        change_test_dir(src_dir)
        create_default_templates()

        web_app_file = src_dir / "templates" / "web_app.json"
        assert web_app_file.exists()

        with open(web_app_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data["name"] == "Web Application"
        assert data["description"] == "Frontend/Backend web development project"
        assert "file_priorities" in data
        assert "typing_speed_multipliers" in data
        assert "refactoring_probability" in data
        assert "debugging_probability" in data
    
    def test_creates_data_science_template(self, temp_dirs, change_test_dir):
        """Test that data science template is created correctly."""
        src_dir, _ = temp_dirs

        change_test_dir(src_dir)
        create_default_templates()

        ds_file = src_dir / "templates" / "data_science.json"
        assert ds_file.exists()

        with open(ds_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert data["name"] == "Data Science Project"
        assert data["description"] == "Machine learning and data analysis project"
        assert "file_priorities" in data
        assert "typing_speed_multipliers" in data
        assert data["typing_speed_multipliers"]["Python"] == 0.8
    
    def test_templates_directory_already_exists(self, temp_dirs, change_test_dir):
        """Test behavior when templates directory already exists."""
        src_dir, _ = temp_dirs

        # Pre-create templates directory
        templates_dir = src_dir / "templates"
        templates_dir.mkdir()

        change_test_dir(src_dir)
        # Should not raise an error
        create_default_templates()

        # Should still create template files
        assert (templates_dir / "web_app.json").exists()
        assert (templates_dir / "data_science.json").exists()
    
    def test_file_write_permission_error(self, temp_dirs, monkeypatch, change_test_dir):
        """Test handling of file write permission errors."""
        src_dir, _ = temp_dirs

        change_test_dir(src_dir)

        # Mock open to raise PermissionError
        def mock_open_error(*args, **kwargs):
            if 'w' in str(args) or 'w' in str(kwargs):
                raise PermissionError("Permission denied")
            return mock_open()(*args, **kwargs)

        with patch('builtins.open', side_effect=mock_open_error):
            # Should handle permission error gracefully
            with pytest.raises(PermissionError):
                create_default_templates()
"""
Tests for VisualTimeline class in wakatimer.py
"""

class TestVisualTimeline:
    """Test the VisualTimeline class."""
    
    def test_initialization(self):
        """Test VisualTimeline initialization."""
        timeline = VisualTimeline()
        assert timeline.events == []
        assert timeline.start_time is None
    
    def test_start_session(self):
        """Test starting a session."""
        timeline = VisualTimeline()
        
        with patch('time.time', return_value=1640995200.0):
            timeline.start_session()
            assert timeline.start_time == 1640995200.0
    
    def test_add_event_auto_starts_session(self):
        """Test that adding an event automatically starts the session."""
        timeline = VisualTimeline()
        
        with patch('time.time', return_value=1640995200.0):
            timeline.add_event("coding", "test.py", "Python", 10.5)
            
            assert timeline.start_time == 1640995200.0
            assert len(timeline.events) == 1
            
            event = timeline.events[0]
            assert event['timestamp'] == 0.0  # First event at time 0
            assert event['type'] == "coding"
            assert event['file'] == "test.py"
            assert event['language'] == "Python"
            assert event['duration'] == 10.5
    
    def test_add_multiple_events(self):
        """Test adding multiple events with different timestamps."""
        timeline = VisualTimeline()
        
        # Mock time.time to return increasing values, with enough values for all calls
        time_values = [1640995200.0, 1640995200.0, 1640995210.0, 1640995210.0, 1640995225.0, 1640995225.0]
        with patch('time.time', side_effect=time_values):
            timeline.add_event("coding", "file1.py", "Python", 5.0)
            timeline.add_event("debugging", "file2.js", "JavaScript", 8.0)
            timeline.add_event("testing", "file3.py", "Python", 3.0)
        
        assert len(timeline.events) == 3
        
        # Check timestamps are relative to start time (first event should be 0)
        assert timeline.events[0]['timestamp'] == 0.0
        # Subsequent events should have increasing timestamps
        assert timeline.events[1]['timestamp'] >= timeline.events[0]['timestamp']
        assert timeline.events[2]['timestamp'] >= timeline.events[1]['timestamp']
    
    def test_add_event_with_existing_session(self):
        """Test adding events to an already started session."""
        timeline = VisualTimeline()
        timeline.start_time = 1640995200.0
        
        with patch('time.time', return_value=1640995230.0):
            timeline.add_event("refactoring", "main.py", "Python", 15.0)
            
            event = timeline.events[0]
            assert event['timestamp'] == 30.0  # 30 seconds after start
    
    def test_display_progress_bar(self, capsys):
        """Test displaying progress bar."""
        timeline = VisualTimeline()
        
        # Test with Python file
        timeline.display_progress_bar(25, 100, "main.py", "Python")
        captured = capsys.readouterr()
        
        assert "main.py" in captured.out
        assert "25.0%" in captured.out
        assert "🐍" in captured.out  # Python icon
        assert "█" in captured.out  # Progress bar filled portion
        assert "░" in captured.out  # Progress bar empty portion
    
    def test_display_progress_bar_different_languages(self, capsys):
        """Test progress bar with different programming languages."""
        timeline = VisualTimeline()
        
        test_cases = [
            ("JavaScript", "🟨"),
            ("TypeScript", "🔷"),
            ("HTML", "🟧"),
            ("CSS", "🎨"),
            ("JSON", "📄"),
            ("Markdown", "📝"),
            ("Java", "☕"),
            ("C++", "⚡"),
            ("Unknown", "📄")  # Default icon
        ]
        
        for language, expected_icon in test_cases:
            timeline.display_progress_bar(50, 100, f"test.{language.lower()}", language)
            captured = capsys.readouterr()
            assert expected_icon in captured.out
    
    def test_display_progress_bar_edge_cases(self, capsys):
        """Test progress bar edge cases."""
        timeline = VisualTimeline()
        
        # Test 0% progress
        timeline.display_progress_bar(0, 100, "start.py", "Python")
        captured = capsys.readouterr()
        assert "0.0%" in captured.out
        
        # Test 100% progress
        timeline.display_progress_bar(100, 100, "complete.py", "Python")
        captured = capsys.readouterr()
        assert "100.0%" in captured.out
        
        # Test with total = 1 (avoid division by zero)
        timeline.display_progress_bar(1, 1, "single.py", "Python")
        captured = capsys.readouterr()
        assert "100.0%" in captured.out
    
    def test_generate_timeline_chart_no_events(self, temp_dirs):
        """Test generating timeline chart with no events."""
        src_dir, _ = temp_dirs
        timeline = VisualTimeline()
        
        result = timeline.generate_timeline_chart(src_dir)
        assert result is None
        
        timeline_file = src_dir / "timeline.txt"
        assert not timeline_file.exists()
    
    def test_generate_timeline_chart_single_hour(self, temp_dirs, capsys):
        """Test generating timeline chart with events in single hour."""
        src_dir, _ = temp_dirs
        timeline = VisualTimeline()
        
        # Add events within first hour
        timeline.events = [
            {
                'timestamp': 300,   # 5 minutes
                'type': 'coding',
                'file': 'main.py',
                'language': 'Python',
                'duration': 600  # 10 minutes
            },
            {
                'timestamp': 1200,  # 20 minutes
                'type': 'debugging',
                'file': 'utils.js',
                'language': 'JavaScript',
                'duration': 300  # 5 minutes
            }
        ]
        
        timeline.generate_timeline_chart(src_dir)
        
        timeline_file = src_dir / "timeline.txt"
        assert timeline_file.exists()
        
        content = timeline_file.read_text(encoding='utf-8')
        assert "CODING SESSION TIMELINE" in content
        assert "Hour 1:" in content
        assert "Python" in content
        assert "JavaScript" in content
        assert "🐍" in content or "🟨" in content  # Language symbols
        
        # Check that it printed the save message
        captured = capsys.readouterr()
        assert "Timeline chart saved to:" in captured.out
    
    def test_generate_timeline_chart_multiple_hours(self, temp_dirs):
        """Test generating timeline chart with events across multiple hours."""
        src_dir, _ = temp_dirs
        timeline = VisualTimeline()
        
        # Add events across multiple hours
        timeline.events = [
            {
                'timestamp': 1800,   # 30 minutes (Hour 1)
                'type': 'coding',
                'file': 'main.py',
                'language': 'Python',
                'duration': 900  # 15 minutes
            },
            {
                'timestamp': 3900,   # 1 hour 5 minutes (Hour 2)
                'type': 'testing',
                'file': 'test.py',
                'language': 'Python',
                'duration': 600  # 10 minutes
            },
            {
                'timestamp': 7500,   # 2 hours 5 minutes (Hour 3)
                'type': 'refactoring',
                'file': 'utils.js',
                'language': 'JavaScript',
                'duration': 1200  # 20 minutes
            }
        ]
        
        timeline.generate_timeline_chart(src_dir)
        
        timeline_file = src_dir / "timeline.txt"
        content = timeline_file.read_text(encoding='utf-8')
        
        assert "Hour 1:" in content
        assert "Hour 2:" in content
        assert "Hour 3:" in content
        
        # Check language breakdown
        assert "Python" in content
        assert "JavaScript" in content
    
    def test_generate_timeline_chart_language_symbols(self, temp_dirs):
        """Test that correct language symbols are used in timeline chart."""
        src_dir, _ = temp_dirs
        timeline = VisualTimeline()
        
        # Test various languages
        languages = ['Python', 'JavaScript', 'TypeScript', 'HTML', 'CSS', 'JSON']
        expected_symbols = ['🐍', '🟨', '🔷', '🟧', '🎨', '📄']
        
        timeline.events = []
        for i, lang in enumerate(languages):
            timeline.events.append({
                'timestamp': i * 600,  # Spread across time
                'type': 'coding',
                'file': f'file{i}.ext',
                'language': lang,
                'duration': 300
            })
        
        timeline.generate_timeline_chart(src_dir)
        
        timeline_file = src_dir / "timeline.txt"
        content = timeline_file.read_text(encoding='utf-8')
        
        # Check that language symbols appear
        for symbol in expected_symbols:
            assert symbol in content
    
    def test_generate_timeline_chart_zero_duration_hour(self, temp_dirs):
        """Test timeline chart generation with hours that have zero duration."""
        src_dir, _ = temp_dirs
        timeline = VisualTimeline()
        
        # Create events that result in an hour with zero total time
        timeline.events = [
            {
                'timestamp': 100,
                'type': 'coding',
                'file': 'main.py',
                'language': 'Python',
                'duration': 0  # Zero duration
            }
        ]
        
        timeline.generate_timeline_chart(src_dir)
        
        timeline_file = src_dir / "timeline.txt"
        content = timeline_file.read_text(encoding='utf-8')
        
        assert "0.0 min" in content
        assert "░" in content  # Empty progress bar
    
    def test_generate_timeline_chart_file_encoding(self, temp_dirs):
        """Test that timeline chart is saved with correct encoding."""
        src_dir, _ = temp_dirs
        timeline = VisualTimeline()
        
        # Add event with unicode characters
        timeline.events = [
            {
                'timestamp': 300,
                'type': 'coding',
                'file': 'tëst.py',  # Unicode filename
                'language': 'Python',
                'duration': 600
            }
        ]
        
        timeline.generate_timeline_chart(src_dir)
        
        timeline_file = src_dir / "timeline.txt"
        assert timeline_file.exists()
        
        # Should be able to read with utf-8 encoding
        content = timeline_file.read_text(encoding='utf-8')
        assert "tëst.py" in content or "Python" in content  # File might not show in chart
