#!/usr/bin/env python3
#!/usr/bin/env python3
"""
Wakatimer - Simulates human-like coding behavior to generate retroactive time tracking data.

This script copies a coding project from source to destination while simulating realistic
coding patterns including typing delays, debugging phases, and human-like behavior.

Author: Sukarth Achaya
Version: 2.0.2
"""

import os
import shutil
import time
import random
import argparse
import json
import csv
import pickle
import hashlib
from pathlib import Path
from typing import List, Optional
from datetime import datetime
import mimetypes
import fnmatch

def format_time(seconds: float) -> str:
    """Format seconds into HH:MM:SS format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

def print_logo():
    """Print ASCII art logo and author info."""
    logo = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║  ██╗    ██╗ █████╗ ██╗  ██╗ █████╗ ████████╗██╗███╗   ███╗███████╗██████╗    ║
║  ██║    ██║██╔══██╗██║ ██╔╝██╔══██╗╚══██╔══╝██║████╗ ████║██╔════╝██╔══██╗   ║
║  ██║ █╗ ██║███████║█████╔╝ ███████║   ██║   ██║██╔████╔██║█████╗  ██████╔╝   ║
║  ██║███╗██║██╔══██║██╔═██╗ ██╔══██║   ██║   ██║██║╚██╔╝██║██╔══╝  ██╔══██╗   ║
║  ╚███╔███╔╝██║  ██║██║  ██╗██║  ██║   ██║   ██║██║ ╚═╝ ██║███████╗██║  ██║   ║
║   ╚══╝╚══╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚═╝╚═╝     ╚═╝╚══════╝╚═╝  ╚═╝   ║
║                                                                              ║
║                                                                              ║
║                                WAKATIMER                                     ║
║                                                                              ║
║                 Retroactive Time Tracking Data Generator                     ║
║                                                                              ║
║                           By: Sukarth Achaya                                 ║
║                              Version 2.0.2                                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(logo)

def load_project_template(template_name: str) -> dict:
    """Load project template configuration."""
    template_file = Path(f"templates/{template_name}.json")
    if template_file.exists():
        with open(template_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def create_default_templates():
    """Create default project templates."""
    templates_dir = Path("templates")
    templates_dir.mkdir(exist_ok=True)

    # Web App Template
    web_app = {
        "name": "Web Application",
        "description": "Frontend/Backend web development project",
        "file_priorities": {
            "config": ["package.json", "requirements.txt", "Dockerfile", "docker-compose.yml"],
            "core": ["*.js", "*.ts", "*.py", "*.html", "*.css"],
            "tests": ["*test*", "*spec*"],
            "docs": ["README.md", "*.md"]
        },
        "typing_speed_multipliers": {
            "JavaScript": 1.1,
            "TypeScript": 0.9,
            "Python": 1.0,
            "HTML": 1.3,
            "CSS": 1.2
        },
        "refactoring_probability": 0.4,
        "debugging_probability": 0.25
    }

    # Data Science Template
    data_science = {
        "name": "Data Science Project",
        "description": "Machine learning and data analysis project",
        "file_priorities": {
            "config": ["requirements.txt", "environment.yml", "setup.py"],
            "core": ["*.py", "*.ipynb", "*.R"],
            "data": ["*.csv", "*.json", "*.parquet"],
            "docs": ["README.md", "*.md"]
        },
        "typing_speed_multipliers": {
            "Python": 0.8,  # More complex algorithms
            "Jupyter": 0.7,
            "R": 0.9
        },
        "refactoring_probability": 0.5,
        "debugging_probability": 0.35
    }

    # Save templates
    with open(templates_dir / "web_app.json", 'w', encoding='utf-8') as f:
        json.dump(web_app, f, indent=2)

    with open(templates_dir / "data_science.json", 'w', encoding='utf-8') as f:
        json.dump(data_science, f, indent=2)

class VisualTimeline:
    """Handles visual timeline generation and display."""

    def __init__(self):
        self.events = []
        self.start_time = None

    def start_session(self):
        """Start tracking the session."""
        self.start_time = time.time()

    def add_event(self, event_type: str, file_name: str, language: str, duration: float):
        """Add an event to the timeline."""
        if self.start_time is None:
            self.start_session()

        self.events.append({
            'timestamp': time.time() - (self.start_time or time.time()),
            'type': event_type,
            'file': file_name,
            'language': language,
            'duration': duration
        })

    def display_progress_bar(self, current: int, total: int, file_name: str, language: str):
        """Display a real-time progress bar."""
        bar_length = 50
        progress = current / total
        filled_length = int(bar_length * progress)

        # Color coding for different languages
        colors = {
            'Python': '🐍', 'JavaScript': '🟨', 'TypeScript': '🔷', 'HTML': '🟧',
            'CSS': '🎨', 'JSON': '📄', 'Markdown': '📝', 'Java': '☕', 'C++': '⚡'
        }

        icon = colors.get(language, '📄')
        bar = '█' * filled_length + '░' * (bar_length - filled_length)

        print(f"\r{icon} [{bar}] {progress*100:.1f}% | {file_name}", end='', flush=True)

    def generate_timeline_chart(self, session_dir: Path):
        """Generate a visual timeline chart."""
        if not self.events:
            return

        timeline_file = session_dir / "timeline.txt"

        # Group events by hour
        hourly_data = {}
        total_duration = max(event['timestamp'] + event['duration'] for event in self.events)

        for event in self.events:
            hour = int(event['timestamp'] // 3600)
            if hour not in hourly_data:
                hourly_data[hour] = {'languages': {}, 'total_time': 0}

            lang = event['language']
            if lang not in hourly_data[hour]['languages']:
                hourly_data[hour]['languages'][lang] = 0

            hourly_data[hour]['languages'][lang] += event['duration']
            hourly_data[hour]['total_time'] += event['duration']

        # Generate ASCII timeline
        with open(timeline_file, 'w', encoding='utf-8') as f:
            f.write("📊 CODING SESSION TIMELINE\n")
            f.write("=" * 80 + "\n\n")

            for hour in sorted(hourly_data.keys()):
                data = hourly_data[hour]
                f.write(f"Hour {hour + 1}:\n")

                # Create a visual bar for this hour
                bar_length = 60
                total_time = data['total_time']

                if total_time > 0:
                    bar = ""
                    for lang, time_spent in data['languages'].items():
                        proportion = time_spent / total_time
                        lang_length = int(bar_length * proportion)

                        # Language symbols
                        symbols = {
                            'Python': '🐍', 'JavaScript': '🟨', 'TypeScript': '🔷',
                            'HTML': '🟧', 'CSS': '🎨', 'JSON': '📄'
                        }
                        symbol = symbols.get(lang, '▓')
                        bar += symbol * max(1, lang_length)

                    f.write(f"  [{bar:<{bar_length}}] {total_time/60:.1f} min\n")

                    # Language breakdown
                    for lang, time_spent in sorted(data['languages'].items(), key=lambda x: x[1], reverse=True):
                        percentage = (time_spent / total_time) * 100
                        f.write(f"    {lang}: {time_spent/60:.1f} min ({percentage:.1f}%)\n")
                else:
                    f.write(f"  [{'░' * bar_length}] 0.0 min\n")

                f.write("\n")

        print(f"📈 Timeline chart saved to: {timeline_file}")

class CodingSimulator:
    def __init__(self, source_dir: str, dest_dir: str, mode: str = "auto", total_hours: Optional[float] = None):
        self.source_dir = Path(source_dir)
        self.dest_dir = Path(dest_dir)
        self.mode = mode
        self.total_hours = total_hours
        self.total_seconds = total_hours * 3600 if total_hours else None
        
        # Typing speeds (characters per minute)
        self.base_typing_speed = 200  # Average developer typing speed
        self.min_typing_speed = 120
        self.max_typing_speed = 300
        
        # File extensions that are considered "codeable"
        self.code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss', '.sass',
            '.java', '.cpp', '.c', '.h', '.hpp', '.cs', '.php', '.rb', '.go',
            '.rs', '.swift', '.kt', '.scala', '.clj', '.hs', '.ml', '.fs',
            '.sql', '.sh', '.bash', '.ps1', '.bat', '.yaml', '.yml', '.json',
            '.xml', '.toml', '.ini', '.cfg', '.conf', '.md', '.rst',
            '.vue', '.svelte', '.dart', '.r', '.m', '.pl', '.lua', '.vim'
        }
        
        # Files/directories to skip entirely
        self.skip_patterns = {
            'node_modules', '.git', '.svn', '.hg', '__pycache__', '.pytest_cache',
            'venv', 'env', '.env', 'dist', 'build', 'target', 'bin', 'obj',
            '.idea', '.vscode', '.vs', 'coverage', '.coverage', '.nyc_output'
        }
        
        # Binary file extensions (copy without simulation)
        self.binary_extensions = {
            '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
            '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.ico', '.webp',
            '.mp4', '.avi', '.mov', '.wmv', '.flv', '.webm', '.mp3', '.wav',
            '.ogg', '.flac', '.zip', '.rar', '.7z', '.tar', '.gz', '.bz2',
            '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx'
        }
        
        self.start_time = time.time()
        self.elapsed_time = 0
        self.files_processed = 0
        self.total_files = 0

        # Time tracking grace period (90 seconds max between content changes)
        self.max_grace_period = 90.0  # seconds
        self.last_content_change = None

        # File analysis and dependency tracking
        self.file_analysis = {}
        self.file_dependencies = {}
        self.processed_files = set()
        self.session_stats = {
            'total_chars_typed': 0,
            'files_modified': 0,
            'refactoring_sessions': 0,
            'debugging_sessions': 0,
            'time_by_language': {},
            'hourly_breakdown': []
        }

        # Feature toggles
        self.enable_refactoring = True
        self.enable_analytics = True
        self.enable_testing_cycles = True
        self.enable_research_pauses = True
        self.enable_copy_paste = True

        # Interactive and resume features
        self.interactive_mode = False
        self.ignore_patterns = set()
        self.project_template = {}

        # Session management
        self.sessions_dir = Path("WakatimerSessions")
        self.sessions_dir.mkdir(exist_ok=True)

        # Generate project name for session files
        self.project_name = self.source_dir.name[:20]  # Truncate to 20 chars
        self.resume_file = self.sessions_dir / f"{self.project_name}_session.pkl"

        # Visual timeline
        self.timeline = VisualTimeline()

        # Session state for resume
        self.session_state = {
            'processed_files': [],
            'current_file_index': 0,
            'current_file_path': None,
            'current_file_progress': 0.0,  # Progress within current file (0.0 to 1.0)
            'current_file_chunks_completed': 0,
            'current_file_total_chunks': 0,
            'elapsed_time': 0,
            'session_id': None
        }
        
    def should_skip_path(self, path: Path) -> bool:
        """Check if a path should be skipped entirely."""
        for part in path.parts:
            if part in self.skip_patterns:
                return True
        return False
    
    def is_binary_file(self, file_path: Path) -> bool:
        """Check if a file is binary and should be copied without simulation."""
        if file_path.suffix.lower() in self.binary_extensions:
            return True
        
        # Additional MIME type check
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if mime_type and not mime_type.startswith('text'):
            return True
            
        return False
    
    def is_code_file(self, file_path: Path) -> bool:
        """Check if a file should be treated as code for simulation."""
        return file_path.suffix.lower() in self.code_extensions

    def analyze_file(self, file_path: Path) -> dict:
        """Analyze file complexity and characteristics with error handling."""
        if file_path in self.file_analysis:
            return self.file_analysis[file_path]

        # Default analysis (fallback)
        analysis = {
            'size': 0,
            'extension': file_path.suffix.lower(),
            'language': self.get_language(file_path),
            'complexity': 'simple',
            'estimated_lines': 0,
            'has_functions': False,
            'has_classes': False,
            'has_imports': False,
            'is_config': False,
            'is_test': False
        }

        try:
            analysis['size'] = file_path.stat().st_size
        except (OSError, IOError):
            # Fallback: estimate size or use 0
            analysis['size'] = 0

        if self.is_code_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    lines = content.split('\n')
                    analysis['estimated_lines'] = len([l for l in lines if l.strip()])

                    # Analyze content complexity
                    content_lower = content.lower()
                    analysis['has_functions'] = any(keyword in content_lower for keyword in
                                                  ['def ', 'function ', 'func ', 'method'])
                    analysis['has_classes'] = any(keyword in content_lower for keyword in
                                                ['class ', 'interface ', 'struct '])
                    analysis['has_imports'] = any(keyword in content_lower for keyword in
                                                ['import ', 'require(', 'include ', '#include'])
                    analysis['is_config'] = file_path.suffix.lower() in {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg'}
                    analysis['is_test'] = any(keyword in file_path.name.lower() for keyword in
                                            ['test', 'spec', '_test', '.test'])

                    # Determine complexity
                    if analysis['has_classes'] or analysis['estimated_lines'] > 200:
                        analysis['complexity'] = 'complex'
                    elif analysis['has_functions'] or analysis['estimated_lines'] > 50:
                        analysis['complexity'] = 'medium'
                    elif analysis['is_config']:
                        analysis['complexity'] = 'simple'

            except (IOError, OSError, UnicodeDecodeError, MemoryError) as e:
                # Fallback: estimate complexity from file size
                try:
                    if analysis['size'] > 5000:  # Large file
                        analysis['complexity'] = 'complex'
                    elif analysis['size'] > 1000:  # Medium file
                        analysis['complexity'] = 'medium'
                    analysis['estimated_lines'] = max(1, analysis['size'] // 50)  # Rough estimate
                except Exception:
                    # Ultimate fallback
                    analysis['complexity'] = 'simple'
                    analysis['estimated_lines'] = 10

        self.file_analysis[file_path] = analysis
        return analysis

    def get_language(self, file_path: Path) -> str:
        """Determine programming language from file extension."""
        ext = file_path.suffix.lower()
        language_map = {
            '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript', '.jsx': 'React',
            '.tsx': 'React', '.html': 'HTML', '.css': 'CSS', '.scss': 'SCSS',
            '.java': 'Java', '.cpp': 'C++', '.c': 'C', '.h': 'C/C++', '.cs': 'C#',
            '.php': 'PHP', '.rb': 'Ruby', '.go': 'Go', '.rs': 'Rust', '.swift': 'Swift',
            '.kt': 'Kotlin', '.sql': 'SQL', '.sh': 'Shell', '.ps1': 'PowerShell',
            '.json': 'JSON', '.yaml': 'YAML', '.yml': 'YAML', '.xml': 'XML',
            '.md': 'Markdown', '.txt': 'Text', '.vue': 'Vue', '.svelte': 'Svelte'
        }
        return language_map.get(ext, 'Unknown')

    def get_language_typing_speed(self, language: str, complexity: str) -> float:
        """Get typing speed based on language and complexity."""
        base_speeds = {
            'Python': 180, 'JavaScript': 200, 'TypeScript': 170, 'React': 160,
            'HTML': 250, 'CSS': 220, 'SCSS': 200, 'JSON': 280, 'YAML': 260,
            'Java': 160, 'C++': 140, 'C': 150, 'C#': 165, 'PHP': 190,
            'Ruby': 185, 'Go': 175, 'Rust': 130, 'Swift': 155, 'Kotlin': 165,
            'SQL': 200, 'Shell': 180, 'PowerShell': 170, 'Markdown': 300,
            'Text': 320, 'XML': 240, 'Vue': 170, 'Svelte': 170
        }

        base_speed = base_speeds.get(language, self.base_typing_speed)

        # Adjust for complexity
        complexity_multipliers = {
            'simple': 1.2,
            'medium': 1.0,
            'complex': 0.7
        }

        return base_speed * complexity_multipliers.get(complexity, 1.0)

    def interactive_setup(self):
        """Interactive setup mode for customizing simulation parameters."""
        print("\n🎛️  INTERACTIVE SETUP")
        print("=" * 50)

        # Mode selection
        print("\n1. Simulation Mode:")
        print("   [1] Auto mode (determine time automatically)")
        print("   [2] Manual mode (specify exact hours)")

        mode_choice = input("\nSelect mode (1-2): ").strip()
        if mode_choice == "2":
            self.mode = "manual"
            while True:
                try:
                    hours = float(input("Enter total coding hours (e.g., 14.5): "))
                    if 0 < hours < 24:
                        self.total_hours = hours
                        self.total_seconds = hours * 3600
                        break
                    else:
                        print("Please enter a value between 0 and 24 hours.")
                except ValueError:
                    print("Please enter a valid number.")
        else:
            self.mode = "auto"

        # Feature toggles
        print("\n2. Features to Enable/Disable:")
        features = [
            ("refactoring", "Refactoring phases (revisit files)", self.enable_refactoring),
            ("testing", "Testing cycles", self.enable_testing_cycles),
            ("research", "Research pauses", self.enable_research_pauses),
            ("copy_paste", "Copy-paste simulation", self.enable_copy_paste),
            ("analytics", "Analytics generation", self.enable_analytics)
        ]

        for key, description, current in features:
            status = "enabled" if current else "disabled"
            toggle = input(f"   {description} (currently {status}) - Toggle? (y/N): ").strip().lower()
            if toggle == 'y':
                setattr(self, f"enable_{key}", not current)

        # Project template
        print("\n3. Project Template:")
        templates = ["none", "web_app", "data_science", "custom"]
        print("   [1] None (default behavior)")
        print("   [2] Web Application")
        print("   [3] Data Science")
        print("   [4] Custom (load from templates/custom.json)")

        template_choice = input("\nSelect template (1-4): ").strip()
        template_map = {"2": "web_app", "3": "data_science", "4": "custom"}
        if template_choice in template_map:
            template_name = template_map[template_choice]
            self.project_template = load_project_template(template_name)
            if self.project_template:
                print(f"✅ Loaded template: {self.project_template.get('name', template_name)}")
            else:
                print(f"⚠️  Template {template_name} not found, using defaults")

        # Grace period
        print(f"\n4. Grace Period (currently {self.max_grace_period}s):")
        grace_input = input("   Enter new grace period in seconds (or press Enter to keep current): ").strip()
        if grace_input:
            try:
                self.max_grace_period = float(grace_input)
                print(f"✅ Grace period set to {self.max_grace_period}s")
            except ValueError:
                print("⚠️  Invalid input, keeping current value")

        print("\n✅ Interactive setup complete!")

    def analyze_project_and_plan(self, all_files: List[Path]) -> dict:
        """Analyze the project and create a detailed execution plan."""
        print("\n🔍 ANALYZING PROJECT...")
        print("=" * 50)

        # Categorize files
        code_files = [f for f in all_files if self.is_code_file(f)]
        binary_files = [f for f in all_files if not self.is_code_file(f)]

        # Language analysis
        languages = {}
        total_code_size = 0
        complexity_breakdown = {'simple': 0, 'medium': 0, 'complex': 0}

        for file_path in code_files:
            analysis = self.analyze_file(file_path)
            lang = analysis['language']
            size = analysis['size']
            complexity = analysis['complexity']

            if lang not in languages:
                languages[lang] = {'files': 0, 'size': 0}

            languages[lang]['files'] += 1
            languages[lang]['size'] += size
            total_code_size += size
            complexity_breakdown[complexity] += 1

        # Estimate time
        if self.mode == "auto":
            estimated_time = self.estimate_auto_time(all_files)
        else:
            estimated_time = self.total_hours

        plan = {
            'total_files': len(all_files),
            'code_files': len(code_files),
            'binary_files': len(binary_files),
            'languages': languages,
            'total_code_size': total_code_size,
            'complexity_breakdown': complexity_breakdown,
            'estimated_time_hours': estimated_time,

            'features_enabled': {
                'refactoring': self.enable_refactoring,
                'testing': self.enable_testing_cycles,
                'research': self.enable_research_pauses,
                'copy_paste': self.enable_copy_paste,
                'analytics': self.enable_analytics
            }
        }

        return plan

    def display_execution_plan(self, plan: dict):
        """Display the execution plan and get user confirmation."""
        print("\n📋 EXECUTION PLAN")
        print("=" * 50)

        print(f"📊 Project Overview:")
        print(f"   Total files: {plan['total_files']}")
        print(f"   Code files: {plan['code_files']}")
        print(f"   Binary files: {plan['binary_files']}")
        print(f"   Total code size: {plan['total_code_size']:,} characters")

        print(f"\n🗣️  Languages detected:")
        for lang, data in sorted(plan['languages'].items(), key=lambda x: x[1]['size'], reverse=True):
            percentage = (data['size'] / plan['total_code_size']) * 100
            print(f"   {lang}: {data['files']} files, {data['size']:,} chars ({percentage:.1f}%)")

        print(f"\n🧠 Complexity breakdown:")
        total_files = sum(plan['complexity_breakdown'].values())
        for complexity, count in plan['complexity_breakdown'].items():
            if total_files > 0:
                percentage = (count / total_files) * 100
                print(f"   {complexity.title()}: {count} files ({percentage:.1f}%)")

        print(f"\n⏱️  Time estimation:")
        print(f"   Total time: {format_time(plan['estimated_time_hours'] * 3600)}")

        print(f"\n🎛️  Features enabled:")
        for feature, enabled in plan['features_enabled'].items():
            status = "✅" if enabled else "❌"
            print(f"   {status} {feature.replace('_', ' ').title()}")

        print(f"\n🎯 Simulation will:")
        print(f"   • Process files in logical order (config → core → tests → docs)")
        print(f"   • Respect {self.max_grace_period}s grace period between content changes")
        print(f"   • Generate incremental file content changes")
        if self.enable_refactoring:
            print(f"   • Include refactoring phases")
        if self.enable_analytics:
            print(f"   • Export detailed analytics and timeline")

        return self.confirm_execution()

    def confirm_execution(self) -> bool:
        """Get user confirmation to proceed with simulation."""
        print(f"\n" + "=" * 50)
        while True:
            response = input("🚀 Proceed with simulation? (y/N): ").strip().lower()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no', '']:
                return False
            else:
                print("Please enter 'y' for yes or 'n' for no.")

    def save_session_state(self, silent: bool = False):
        """Save current session state for resume capability with corruption protection."""
        try:
            # Calculate current elapsed time
            current_elapsed = time.time() - self.start_time if hasattr(self, 'start_time') else 0

            state = {
                'version': '2.0.2',  
                'checksum': None,    # Will be calculated below
                'session_id': self.session_state['session_id'],
                'source_dir': str(self.source_dir),
                'dest_dir': str(self.dest_dir),
                'mode': self.mode,
                'total_hours': self.total_hours,
                'processed_files': [str(f) for f in self.session_state['processed_files']],
                'current_file_index': self.session_state['current_file_index'],
                'current_file_path': str(self.session_state['current_file_path']) if self.session_state['current_file_path'] else None,
                'current_file_progress': self.session_state['current_file_progress'],
                'current_file_chunks_completed': self.session_state['current_file_chunks_completed'],
                'current_file_total_chunks': self.session_state['current_file_total_chunks'],
                'elapsed_time': current_elapsed,
                'session_stats': self.session_stats,
                'timestamp': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat(),
                'features': {
                    'refactoring': self.enable_refactoring,
                    'testing': self.enable_testing_cycles,
                    'research': self.enable_research_pauses,
                    'copy_paste': self.enable_copy_paste,
                    'analytics': self.enable_analytics
                },
                'timeline_events': getattr(self.timeline, 'events', [])
            }

            # Ensure sessions directory exists
            self.sessions_dir.mkdir(exist_ok=True)

            # Simplified atomic write (remove complex checksum verification for now)
            # Write to temporary file first (atomic operation)
            temp_file = self.resume_file.with_suffix('.tmp')
            with open(temp_file, 'wb') as f:
                pickle.dump(state, f)
                f.flush()  # Ensure data is written to disk
                os.fsync(f.fileno())  # Force OS to write to disk

            # Atomic rename
            temp_file.replace(self.resume_file)

            if not silent:
                print(f"💾 Session saved to {self.resume_file}")

        except Exception as e:
            if not silent:
                print(f"⚠️  Warning: Could not save session state: {e}")
                print(f"  Continuing without session save (simulation will proceed)")
            # Fallback: continue without session saving
            # The simulation can still complete successfully

    def _restore_from_backup(self):
        """Attempt to restore session from backup file."""
        backup_file = self.resume_file.with_suffix('.bak')
        if backup_file.exists():
            try:
                # Verify backup file integrity
                with open(backup_file, 'rb') as f:
                    test_state = pickle.load(f)
                    if 'checksum' in test_state:
                        # Verify checksum if available
                        test_checksum = test_state.get('checksum')
                        test_state_for_checksum = {k: v for k, v in test_state.items() if k != 'checksum'}
                        test_state_str = json.dumps(test_state_for_checksum, sort_keys=True, default=str)
                        calculated_checksum = hashlib.md5(test_state_str.encode()).hexdigest()
                        if test_checksum == calculated_checksum:
                            # Backup is valid, restore it
                            shutil.copy2(backup_file, self.resume_file)
                            print(f"🔄 Restored session from backup: {backup_file}")
                            return True

            except Exception:
                pass  # Backup is also corrupted

        print(f"⚠️  Could not restore from backup, session data may be lost")
        return False

    def validate_session_file(self, file_path: Path) -> bool:
        """Validate session file integrity."""
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'rb') as f:
                state = pickle.load(f)

            # Check if it has required fields
            required_fields = ['session_id', 'source_dir', 'dest_dir', 'mode']
            if not all(field in state for field in required_fields):
                return False

            # Verify checksum if available
            if 'checksum' in state:
                stored_checksum = state.get('checksum')
                state_for_checksum = {k: v for k, v in state.items() if k != 'checksum'}
                state_str = json.dumps(state_for_checksum, sort_keys=True, default=str)
                calculated_checksum = hashlib.md5(state_str.encode()).hexdigest()
                return stored_checksum == calculated_checksum

            return True  # No checksum, but basic structure is valid

        except Exception:
            return False

    def auto_save_session(self):
        """Automatically save session state (silent)."""
        # Check if session state is properly initialized
        if not hasattr(self, 'session_state') or not self.session_state.get('session_id'):
            return

        # Check if resume file path is set
        if not hasattr(self, 'resume_file'):
            return

        self.save_session_state(silent=True)

    def periodic_auto_save(self):
        """Periodic auto-save with timestamp check to avoid too frequent saves."""
        current_time = time.time()

        # Only auto-save if it's been more than 30 seconds since last save
        if not hasattr(self, '_last_auto_save') or (current_time - self._last_auto_save) > 30:
            self.auto_save_session()
            self._last_auto_save = current_time

    def load_session_state(self) -> bool:
        """Load previous session state with integrity verification."""
        if not self.resume_file.exists():
            return False

        try:
            with open(self.resume_file, 'rb') as f:
                state = pickle.load(f)

            # If timeline_events is missing, treat as invalid session
            if 'timeline_events' not in state:
                self.timeline.events = []
                return False

            # Restore state
            self.session_state['session_id'] = state['session_id']
            self.session_state['processed_files'] = [Path(f) for f in state['processed_files']]
            self.session_state['current_file_index'] = state['current_file_index']
            self.session_state['current_file_path'] = Path(state['current_file_path']) if state.get('current_file_path') else None
            self.session_state['current_file_progress'] = state.get('current_file_progress', 0.0)
            self.session_state['current_file_chunks_completed'] = state.get('current_file_chunks_completed', 0)
            self.session_state['current_file_total_chunks'] = state.get('current_file_total_chunks', 0)
            self.session_state['elapsed_time'] = state['elapsed_time']
            self.session_stats = state['session_stats']
            self.timeline.events = state['timeline_events']
            features = state.get('features', {})
            self.enable_refactoring = features.get('refactoring', True)
            self.enable_testing_cycles = features.get('testing', True)
            self.enable_research_pauses = features.get('research', True)
            self.enable_copy_paste = features.get('copy_paste', True)
            self.enable_analytics = features.get('analytics', True)
            if hasattr(self, 'start_time'):
                self.start_time = time.time() - state['elapsed_time']
            print(f"📂 Loaded session from {state.get('last_update', state.get('timestamp', 'unknown'))}")
            print(f"   Progress: {len(state['processed_files'])} files completed")
            print(f"   Elapsed time: {format_time(state['elapsed_time'])}")
            print(f"   Timeline events: {len(state.get('timeline_events', []))}")
            if state.get('current_file_path') and state.get('current_file_progress', 0) > 0:
                current_file = Path(state['current_file_path']).name
                progress_pct = state.get('current_file_progress', 0) * 100
                chunks_info = f"{state.get('current_file_chunks_completed', 0)}/{state.get('current_file_total_chunks', 0)}"
                print(f"   Current file: {current_file} ({progress_pct:.1f}% complete, chunk {chunks_info})")
            return True
        except Exception as e:
            print(f"⚠️  Could not load session: {e}")
            # Try to restore from backup if available
            if self._restore_from_backup():
                try:
                    with open(self.resume_file, 'rb') as f:
                        state = pickle.load(f)
                    if 'timeline_events' not in state:
                        self.timeline.events = []
                        return False
                    self.session_state['session_id'] = state['session_id']
                    self.session_state['processed_files'] = [Path(f) for f in state['processed_files']]
                    self.session_state['current_file_index'] = state['current_file_index']
                    self.session_state['current_file_path'] = Path(state['current_file_path']) if state.get('current_file_path') else None
                    self.session_state['current_file_progress'] = state.get('current_file_progress', 0.0)
                    self.session_state['current_file_chunks_completed'] = state.get('current_file_chunks_completed', 0)
                    self.session_state['current_file_total_chunks'] = state.get('current_file_total_chunks', 0)
                    self.session_state['elapsed_time'] = state['elapsed_time']
                    self.session_stats = state['session_stats']
                    self.timeline.events = state['timeline_events']
                    features = state.get('features', {})
                    self.enable_refactoring = features.get('refactoring', True)
                    self.enable_testing_cycles = features.get('testing', True)
                    self.enable_research_pauses = features.get('research', True)
                    self.enable_copy_paste = features.get('copy_paste', True)
                    self.enable_analytics = features.get('analytics', True)
                    if hasattr(self, 'start_time'):
                        self.start_time = time.time() - state['elapsed_time']
                    print(f"📂 Loaded session from {state.get('last_update', state.get('timestamp', 'unknown'))}")
                    print(f"   Progress: {len(state['processed_files'])} files completed")
                    print(f"   Elapsed time: {format_time(state['elapsed_time'])}")
                    print(f"   Timeline events: {len(state.get('timeline_events', []))}")
                    if state.get('current_file_path') and state.get('current_file_progress', 0) > 0:
                        current_file = Path(state['current_file_path']).name
                        progress_pct = state.get('current_file_progress', 0) * 100
                        chunks_info = f"{state.get('current_file_chunks_completed', 0)}/{state.get('current_file_total_chunks', 0)}"
                        print(f"   Current file: {current_file} ({progress_pct:.1f}% complete, chunk {chunks_info})")
                    return True
                except Exception as e2:
                    print(f"⚠️  Could not load session after restoring backup: {e2}")
                    return False
            return False

    def check_for_resume(self) -> bool:
        """Check if user wants to resume a previous session."""
        if self.resume_file.exists():
            print(f"\n💾 Found previous session for '{self.project_name}': {self.resume_file}")
            resume = input("Resume previous session? (y/N): ").strip().lower()
            if resume == 'y':
                return self.load_session_state()
        return False

    def apply_ignore_patterns(self, files: List[Path]) -> List[Path]:
        """Filter files based on ignore patterns."""
        if not self.ignore_patterns:
            return files

        filtered_files = []
        for file_path in files:
            should_ignore = False
            for pattern in self.ignore_patterns:
                if fnmatch.fnmatch(file_path.name, pattern) or fnmatch.fnmatch(str(file_path), pattern):
                    should_ignore = True
                    break

            if not should_ignore:
                filtered_files.append(file_path)
            else:
                print(f"🚫 Ignoring: {file_path}")

        return filtered_files

    def simulate_testing_cycle(self, file_path: Path):
        """Simulate testing cycle: write code, test, fix."""
        if not self.enable_testing_cycles or random.random() > 0.3:
            return

        print(f"  🧪 Testing cycle for {file_path.name}...")

        # Write test
        test_time = random.uniform(1.0, 3.0)
        self.safe_delay(test_time, "✏️  Writing test")

        # Run test (fail)
        run_time = random.uniform(0.2, 0.8)
        self.safe_delay(run_time, "🔴 Test failed")

        # Fix code
        fix_time = random.uniform(0.5, 2.0)
        self.safe_delay(fix_time, "🔧 Fixing code")

        # Run test (pass)
        rerun_time = random.uniform(0.1, 0.5)
        self.safe_delay(rerun_time, "✅ Test passed")

    def simulate_research_pause(self, complexity: str):
        """Simulate research/thinking pause based on complexity."""
        if not self.enable_research_pauses:
            return

        if complexity == 'complex' and random.random() < 0.4:
            research_time = random.uniform(2.0, 8.0)
            # Ensure it doesn't exceed grace period
            research_time = min(research_time, self.max_grace_period * 0.7)
            self.safe_delay(research_time, "🔍 Researching solution")

    def simulate_copy_paste(self, content_size: int) -> float:
        """Simulate copy-paste behavior for some content."""
        if not self.enable_copy_paste or random.random() > 0.2:
            return 1.0  # Normal speed

        # Some content is "copied" and appears faster
        if content_size > 500:  # Only for larger files
            print(f"    📋 Copy-paste detected (faster typing)")
            return 3.0  # 3x faster for copied sections

        return 1.0

    def analyze_file_dependencies(self, files: List[Path]) -> List[Path]:
        """Analyze and order files based on dependencies and logical development flow."""
        # Categorize files by type and importance
        config_files = []
        core_files = []
        test_files = []
        doc_files = []
        asset_files = []

        for file_path in files:
            if not self.is_code_file(file_path):
                asset_files.append(file_path)
                continue

            analysis = self.analyze_file(file_path)

            if analysis['is_config']:
                config_files.append(file_path)
            elif analysis['is_test']:
                test_files.append(file_path)
            elif analysis['language'] in ['Markdown', 'Text']:
                doc_files.append(file_path)
            else:
                core_files.append(file_path)

        # Sort within categories by complexity and dependencies
        def sort_by_complexity(file_list):
            return sorted(file_list, key=lambda f: (
                self.analyze_file(f)['complexity'] == 'simple',  # Simple first
                self.analyze_file(f)['size']  # Then by size
            ))

        # Logical development order
        ordered_files = []

        # 1. Configuration files first (setup phase)
        ordered_files.extend(sort_by_complexity(config_files))

        # 2. Core files by complexity (simple to complex)
        ordered_files.extend(sort_by_complexity(core_files))

        # 3. Test files (after core implementation)
        ordered_files.extend(sort_by_complexity(test_files))

        # 4. Documentation (final polish)
        ordered_files.extend(sort_by_complexity(doc_files))

        # 5. Assets (copied quickly at any point)
        ordered_files.extend(asset_files)

        return ordered_files

    def get_refactoring_candidates(self, processed_files: List[Path]) -> List[Path]:
        """Get files that are good candidates for refactoring/revisiting."""
        candidates = []
        for file_path in processed_files:
            if self.is_code_file(file_path):
                analysis = self.analyze_file(file_path)
                # Larger, more complex files are more likely to need refactoring
                if analysis['complexity'] in ['medium', 'complex'] and analysis['size'] > 1000:
                    candidates.append(file_path)

        # Return up to 3 random candidates
        return random.sample(candidates, min(3, len(candidates)))

    def simulate_refactoring_phase(self, files_to_refactor: List[Path]):
        """Simulate going back to refactor/improve existing files."""
        print(f"\n🔄 Refactoring phase - revisiting {len(files_to_refactor)} files...")
        self.session_stats['refactoring_sessions'] += 1

        for file_path in files_to_refactor:
            relative_path = file_path.relative_to(self.source_dir)
            dest_file = self.dest_dir / relative_path

            print(f"  🔧 Refactoring: {relative_path}")

            # Simulate reading the existing code
            read_time = random.uniform(1.0, 3.0)
            self.safe_delay(read_time, "📖 Reading existing code")

            # Simulate making small improvements
            refactor_time = random.uniform(2.0, 8.0)
            chunks = max(2, int(refactor_time / 3))
            chunk_time = refactor_time / chunks

            for i in range(chunks):
                time.sleep(chunk_time)

                # Simulate small content changes (append some comments or minor tweaks)
                with open(dest_file, 'a', encoding='utf-8') as f:
                    f.write(f"\n# Refactored on pass {i+1}")

                # Record content change
                self.last_content_change = time.time()

                if i % 2 == 0:
                    print(f"    Refactoring progress: {((i+1)/chunks)*100:.0f}%")

            # Small pause between refactored files
            if len(files_to_refactor) > 1:
                pause_time = random.uniform(0.3, 1.0)
                self.safe_delay(pause_time, "")

    def generate_session_report(self, total_elapsed: float) -> dict:
        """Generate detailed session analytics."""
        report = {
            'summary': {
                'total_time_hours': total_elapsed / 3600,
                'total_time_minutes': total_elapsed / 60,
                'files_processed': self.files_processed,
                'total_files': self.total_files,
                'chars_typed': self.session_stats['total_chars_typed'],
                'avg_typing_speed': (self.session_stats['total_chars_typed'] * 60) / total_elapsed if total_elapsed > 0 else 0,
                'refactoring_sessions': self.session_stats['refactoring_sessions'],
                'debugging_sessions': self.session_stats['debugging_sessions']
            },
            'by_language': {},
            'productivity_metrics': {},
            'timeline': self.session_stats['hourly_breakdown']
        }

        # Calculate time by language (estimate based on file sizes)
        total_code_size = sum(
            self.analyze_file(f)['size'] for f in self.processed_files
            if hasattr(self, 'processed_files') and self.is_code_file(f)
        )

        if hasattr(self, 'processed_files'):
            for file_path in self.processed_files:
                if self.is_code_file(file_path):
                    analysis = self.analyze_file(file_path)
                    lang = analysis['language']
                    file_size = analysis['size']

                    if lang not in report['by_language']:
                        report['by_language'][lang] = {
                            'files': 0,
                            'chars': 0,
                            'estimated_time_minutes': 0,
                            'complexity_breakdown': {'simple': 0, 'medium': 0, 'complex': 0}
                        }

                    report['by_language'][lang]['files'] += 1
                    report['by_language'][lang]['chars'] += file_size
                    report['by_language'][lang]['complexity_breakdown'][analysis['complexity']] += 1

                    # Estimate time spent on this language
                    if total_code_size > 0:
                        lang_time = (file_size / total_code_size) * total_elapsed
                        report['by_language'][lang]['estimated_time_minutes'] += lang_time / 60

        # Productivity metrics
        if total_elapsed > 0:
            report['productivity_metrics'] = {
                'chars_per_minute': (self.session_stats['total_chars_typed'] * 60) / total_elapsed,
                'files_per_hour': (self.files_processed * 3600) / total_elapsed,
                'avg_file_size': self.session_stats['total_chars_typed'] / max(1, self.files_processed),
                'coding_efficiency': min(100, (self.session_stats['total_chars_typed'] / max(1, total_elapsed)) * 100)
            }

        return report

    def export_to_csv(self, report: dict, session_dir: Path):
        """Export session data to CSV files."""
        csv_dir = session_dir / "analytics"
        csv_dir.mkdir(exist_ok=True)

        # Summary CSV
        summary_file = csv_dir / "session_summary.csv"
        with open(summary_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Metric', 'Value'])
            for key, value in report['summary'].items():
                writer.writerow([key.replace('_', ' ').title(), f"{value:.2f}" if isinstance(value, float) else value])

        # Language breakdown CSV
        if report['by_language']:
            lang_file = csv_dir / "language_breakdown.csv"
            with open(lang_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Language', 'Files', 'Characters', 'Time (minutes)', 'Simple', 'Medium', 'Complex'])
                for lang, data in report['by_language'].items():
                    complexity = data['complexity_breakdown']
                    writer.writerow([
                        lang, data['files'], data['chars'], f"{data['estimated_time_minutes']:.2f}",
                        complexity['simple'], complexity['medium'], complexity['complex']
                    ])

        print(f"📊 Analytics exported to: {csv_dir}")
        return csv_dir

    def save_session_json(self, report: dict, session_dir: Path):
        """Save detailed session report as JSON."""
        json_file = session_dir / "session_report.json"

        # Add metadata
        full_report = {
            'metadata': {
                'simulation_mode': self.mode,
                'target_hours': self.total_hours,
                'source_directory': str(self.source_dir),
                'destination_directory': str(self.dest_dir),
                'timestamp': datetime.now().isoformat(),
                'grace_period_seconds': self.max_grace_period
            },
            'session_data': report
        }

        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(full_report, f, indent=2, ensure_ascii=False)

        print(f"📄 Detailed report saved to: {json_file}")
        return json_file

    def create_final_session_folder(self):
        """Create final session folder and organize all files."""
        # Create final session folder name
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        final_session_name = f"WakatimerSession_{self.project_name}_{timestamp}"
        final_session_dir = self.sessions_dir / final_session_name
        final_session_dir.mkdir(exist_ok=True)

        print(f"📁 Creating final session folder: {final_session_dir}")

        # Copy the pkl file to final session folder
        if self.resume_file.exists():
            final_pkl_file = final_session_dir / f"{self.project_name}_session.pkl"
            shutil.copy2(self.resume_file, final_pkl_file)
            print(f"💾 Session data saved to: {final_pkl_file}")

        return final_session_dir
    
    def calculate_typing_speed(self, file_path: Path) -> float:
        """Calculate typing speed based on language, complexity, and mode."""
        analysis = self.analyze_file(file_path)

        if self.mode == "auto":
            # Use language-specific speed with complexity adjustment
            base_speed = self.get_language_typing_speed(analysis['language'], analysis['complexity'])

            # Add random variation for human-like behavior
            variation = random.uniform(0.8, 1.2)
            return base_speed * variation
        else:
            # Manual mode: adjust speed based on available time
            if self.total_seconds:
                # Estimate total characters to type
                total_chars = sum(
                    f.stat().st_size for f in self.source_dir.rglob('*')
                    if f.is_file() and self.is_code_file(f) and not self.should_skip_path(f)
                )

                # Calculate required speed (with buffer for delays)
                required_speed = (total_chars * 60) / (self.total_seconds * 0.6)  # 60% typing, 40% thinking

                # But still respect language characteristics
                language_speed = self.get_language_typing_speed(analysis['language'], analysis['complexity'])

                # Use the required speed but don't go too far from natural language speed
                target_speed = max(self.min_typing_speed, min(self.max_typing_speed, required_speed))
                return (target_speed + language_speed) / 2  # Average of required and natural speed

            return self.get_language_typing_speed(analysis['language'], analysis['complexity'])
    
    def safe_delay(self, delay_time: float, description: str = ""):
        """Apply a delay while respecting the grace period constraint."""
        # Ensure delay doesn't exceed grace period
        safe_delay_time = min(delay_time, self.max_grace_period * 0.8)  # Use 80% of grace period as safety margin

        if safe_delay_time != delay_time and description:
            print(f"    {description} (capped at {safe_delay_time:.1f}s to respect grace period)")
        elif description:
            print(f"    {description} ({safe_delay_time:.1f}s)")

        time.sleep(safe_delay_time)
        return safe_delay_time

    def simulate_human_delays(self, content_length: int, is_code: bool = True):
        """Simulate human-like delays during coding, respecting grace period."""
        if not is_code:
            return

        # Base thinking time - keep it short to respect grace period
        thinking_time = random.uniform(0.1, 0.8)
        self.safe_delay(thinking_time, "💭 Initial thinking")

        # Simulate reading/planning phases - but keep them reasonable
        if content_length > 500:
            planning_time = random.uniform(0.5, 1.5)  # Reduced from 2.0
            self.safe_delay(planning_time, "📖 Planning phase")

        # Random pauses during "typing" - keep them short
        if random.random() < 0.3:  # 30% chance of pause
            pause_time = random.uniform(0.2, 0.8)  # Reduced from 1.0
            self.safe_delay(pause_time, "⏸️  Thinking pause")

    def simulate_debugging_phase(self, source_file: Path, dest_file: Optional[Path] = None):
        """Simulate debugging: write wrong code, wait, then fix it, respecting grace period."""
        if random.random() < 0.2:  # 20% chance of debugging phase
            print(f"  🐛 Debugging phase for {source_file.name}...")

            # Simulate writing wrong code (content modification)
            debug_time = random.uniform(0.8, 2.0)  # Reduced from 3.0
            self.safe_delay(debug_time, "✏️  Writing incorrect code")

            # Simulate realizing the error (thinking time) - keep it short
            realization_time = random.uniform(0.2, 0.6)  # Reduced from 1.0
            self.safe_delay(realization_time, "💡 Realizing error")

            # Simulate fixing the error (content modification)
            fix_time = random.uniform(0.4, 1.2)  # Reduced from 2.0
            self.safe_delay(fix_time, "🔧 Fixing the error")

            # If dest_file provided, ensure final content is correct
            if dest_file:
                shutil.copy2(source_file, dest_file)

    def simulate_typing_file(self, source_file: Path, dest_file: Path): 
        """Simulate typing out a code file with human-like behavior and incremental content changes."""
        try:
            content_size = source_file.stat().st_size
            typing_speed = self.calculate_typing_speed(source_file)
            analysis = self.analyze_file(source_file)
        except (OSError, IOError) as e:
            print(f"  ⚠️  Error accessing {source_file.name}: {e}")
            # Fallback: simple copy without simulation
            try:
                shutil.copy2(source_file, dest_file)
                print(f"  📄 Copied {source_file.name} (fallback)")
                return
            except Exception as copy_error:
                print(f"  ❌ Failed to copy {source_file.name}: {copy_error}")
                return

        print(f"  ⌨️  Coding {source_file.name} ({content_size} bytes) - {analysis['language']} [{analysis['complexity']}]")
        print(f"    Speed: {typing_speed:.0f} chars/min")

        # Check if resuming this file
        is_resuming_file = (self.session_state['current_file_path'] and
                           Path(self.session_state['current_file_path']) == source_file and
                           self.session_state['current_file_progress'] > 0)

        if is_resuming_file:
            print(f"    🔄 Resuming from {self.session_state['current_file_progress']*100:.1f}% progress")

        # Start timeline tracking
        start_time = time.time()

        # Create the file instantly (file operations don't count as coding time)
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.touch()  # Create empty file instantly

        # Read source content to simulate incremental writing
        try:
            with open(source_file, 'r', encoding='utf-8', errors='ignore') as f:
                full_content = f.read()
        except (IOError, OSError, UnicodeDecodeError) as e:
            print(f"  ⚠️  Error reading {source_file.name}: {e}")
            # Fallback: try binary copy
            try:
                shutil.copy2(source_file, dest_file)
                print(f"  📄 Binary copied {source_file.name} (fallback)")
                return
            except Exception as copy_error:
                print(f"  ❌ Failed to copy {source_file.name}: {copy_error}")
                return

        # Research pause for complex files
        self.simulate_research_pause(analysis['complexity'])

        # Pre-coding delays (thinking/planning time)
        self.simulate_human_delays(content_size, True)

        # Copy-paste speed multiplier
        copy_paste_multiplier = self.simulate_copy_paste(content_size)

        # Simulate actual content writing time (this is what gets tracked)
        typing_time = (content_size * 60) / (typing_speed * copy_paste_multiplier)  # Convert to seconds

        # Break content writing into chunks with incremental content changes
        # Ensure chunks are frequent enough to respect grace period
        max_chunk_time = self.max_grace_period * 0.7  # 70% of grace period per chunk
        min_chunks = max(3, int(typing_time / max_chunk_time))
        chunks = max(min_chunks, min(25, int(typing_time / 2)))  # 2-second chunks minimum
        chunk_time = typing_time / chunks

        # Update session state for this file
        self.session_state['current_file_path'] = source_file
        self.session_state['current_file_total_chunks'] = chunks

        # Determine starting chunk (for resume)
        start_chunk = 0
        if is_resuming_file:
            start_chunk = self.session_state['current_file_chunks_completed']
            print(f"    🔄 Resuming from chunk {start_chunk + 1}/{chunks}")
        else:
            print(f"    Writing in {chunks} chunks, {chunk_time:.1f}s per chunk (respecting {self.max_grace_period}s grace period)")

        for i in range(start_chunk, chunks):
            # This sleep represents actual content modification time
            time.sleep(chunk_time)

            # Calculate how much content to write at this point
            progress_ratio = (i + 1) / chunks
            chars_to_write = int(len(full_content) * progress_ratio)
            partial_content = full_content[:chars_to_write]

            # Write incremental content (simulates real typing/content changes)
            try:
                with open(dest_file, 'w', encoding='utf-8') as f:
                    f.write(partial_content)
            except (IOError, OSError, UnicodeEncodeError) as e:
                print(f"  ⚠️  Error writing to {dest_file.name}: {e}")
                # Fallback: try simple copy at the end
                if i == chunks - 1:  # Last chunk, try to save something
                    try:
                        shutil.copy2(source_file, dest_file)
                        print(f"  📄 Fallback copy completed")
                    except Exception:
                        print(f"  ❌ Complete failure for {source_file.name}")
                continue

            # Record this content change time
            self.last_content_change = time.time()

            # Update session state with current progress
            self.session_state['current_file_chunks_completed'] = i + 1
            self.session_state['current_file_progress'] = progress_ratio

            # Update visual progress bar
            self.timeline.display_progress_bar(i + 1, chunks, source_file.name, analysis['language'])

            # Auto-save session state after every chunk (for fine-grained resume)
            self.auto_save_session()

            # Random micro-pauses during content modification (but keep them short)
            if random.random() < 0.3:  # 30% chance
                micro_pause = random.uniform(0.1, 0.5)  # Reduced max pause
                self.safe_delay(micro_pause, "")  # Silent micro-pause

            # Progress indicator (less frequent now due to progress bar)
            if i == chunks - 1:  # Only show final progress
                print(f"\n    ✅ Content written: 100% ({len(full_content)} chars)")

        # Simulate debugging phase (content modifications)
        self.simulate_debugging_phase(source_file, dest_file)

        # Testing cycle
        self.simulate_testing_cycle(source_file)

        # Post-coding review pause (reading time, not tracked)
        if random.random() < 0.4:  # 40% chance of review
            review_time = random.uniform(0.5, 2.0)
            print(f"    📖 Reviewing code... ({review_time:.1f}s)")
            time.sleep(review_time)

        # Add to timeline
        total_time = time.time() - start_time
        self.timeline.add_event('coding', source_file.name, analysis['language'], total_time)

        # Clear current file state (file completed)
        self.session_state['current_file_path'] = None
        self.session_state['current_file_progress'] = 0.0
        self.session_state['current_file_chunks_completed'] = 0
        self.session_state['current_file_total_chunks'] = 0

    def copy_binary_file(self, source_file: Path, dest_file: Path):
        """Copy binary files instantly (no coding time tracked for binary files)."""
        print(f"  📁 Copying binary file: {source_file.name} (instant)")
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            shutil.copy2(source_file, dest_file)
        except Exception as e:
            print(f"  ❌ Failed to copy binary file: {e}")
        # No delay - file operations are instant and don't count as coding time

    def get_all_files(self) -> List[Path]:
        """Get all files to be processed, excluding skipped paths."""
        all_files = []
        try:
            for file_path in self.source_dir.rglob('*'):
                if file_path.is_file() and not self.should_skip_path(file_path):
                    all_files.append(file_path)
        except OSError:
            pass
        return all_files

    def estimate_auto_time(self, files: List[Path]) -> float:
        """Estimate total time for auto mode."""
        total_time = 0

        for file_path in files:
            if self.is_code_file(file_path):
                file_size = file_path.stat().st_size
                typing_speed = self.calculate_typing_speed(file_path)

                # Base typing time
                typing_time = (file_size * 60) / typing_speed

                # Add overhead for delays, debugging, etc.
                overhead_multiplier = random.uniform(1.8, 2.5)
                total_time += typing_time * overhead_multiplier
            else:
                # Binary files - minimal time
                total_time += random.uniform(0.5, 2.0)

        return total_time / 3600  # Convert to hours

    def run_simulation(self):
        """Run the main simulation with enhanced features."""
        # Print logo
        print_logo()

        # Check for resume
        if not self.interactive_mode and self.check_for_resume():
            print("🔄 Resuming previous session...")

        # Interactive setup if enabled
        if self.interactive_mode:
            self.interactive_setup()

        print(f"\n🚀 Starting Wakatimer Simulation")
        print(f"📂 Source: {self.source_dir}")
        print(f"📁 Destination: {self.dest_dir}")
        print(f"🎯 Mode: {self.mode}")

        if self.mode == "manual" and self.total_hours:
            print(f"⏱️  Target time: {format_time(self.total_hours * 3600)}")

        # Initialize session
        if not self.session_state['session_id']:
            self.session_state['session_id'] = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.timeline.start_session()

        # Initial session save
        self.auto_save_session()

        # Get all files to process
        all_files = self.get_all_files()

        # Apply ignore patterns
        all_files = self.apply_ignore_patterns(all_files)

        self.total_files = len(all_files)

        if self.total_files == 0:
            print("❌ No files found to process!")
            # Still save session state even without analytics
            try:
                self.save_session_state()
                print(f"💾 Session saved to: {self.resume_file}")
            except Exception as e:
                print(f"⚠️  Warning: Could not save session state: {e}")
            return

        print(f"📊 Found {self.total_files} files to process")

        # Analyze project and create execution plan
        plan = self.analyze_project_and_plan(all_files)

        # Display plan and get confirmation
        if not self.display_execution_plan(plan):
            print("❌ Simulation cancelled by user")
            return

        # For auto mode, estimate time
        if self.mode == "auto":
            estimated_hours = self.estimate_auto_time(all_files)
            print(f"⏱️  Estimated time: {format_time(estimated_hours * 3600)}")



        # Analyze and order files intelligently
        code_files = [f for f in all_files if self.is_code_file(f)]
        binary_files = [f for f in all_files if not self.is_code_file(f)]

        # Order files by dependencies and logical development flow
        ordered_code_files = self.analyze_file_dependencies(code_files)

        print(f"\n📝 Code files: {len(code_files)}")
        print(f"📁 Binary files: {len(binary_files)}")
        print(f"\n{'='*50}")
        print("Starting simulation...")
        print("Note: Only content modifications count as coding time, file operations are instant")
        print(f"⏱️  Grace period: {self.max_grace_period}s max between content changes\n")

        # Create destination directory structure instantly (file operations)
        self.dest_dir.mkdir(parents=True, exist_ok=True)

        # Simulate initial project setup/environment configuration time
        setup_time = random.uniform(1, 3)  # Brief setup time
        print(f"🔧 Initial project setup... ({setup_time:.1f}s)")
        time.sleep(setup_time)

        # Process code files with simulation using intelligent ordering
        processed_files = list(self.session_state['processed_files'])  # Start with already processed files
        start_index = self.session_state['current_file_index']

        # Check if we're resuming mid-file
        current_file_in_progress = (self.session_state['current_file_path'] and
                                   self.session_state['current_file_progress'] > 0)

        # Skip already processed files if resuming
        files_to_process = ordered_code_files[start_index:] if start_index > 0 else ordered_code_files

        if start_index > 0:
            if current_file_in_progress:
                current_file_name = Path(self.session_state['current_file_path']).name
                progress_pct = self.session_state['current_file_progress'] * 100
                print(f"🔄 Resuming mid-file: {current_file_name} ({progress_pct:.1f}% complete)")
            else:
                print(f"🔄 Resuming from file {start_index + 1}/{len(ordered_code_files)}")

        for i, file_path in enumerate(files_to_process, start_index + 1):
            relative_path = file_path.relative_to(self.source_dir)
            dest_file = self.dest_dir / relative_path

            print(f"\n[{i}/{len(ordered_code_files)}] Processing: {relative_path}")

            # Check if we're running out of time in manual mode
            if self.mode == "manual" and self.total_seconds:
                elapsed = time.time() - self.start_time
                remaining = self.total_seconds - elapsed
                remaining_files = len(ordered_code_files) - i + len(binary_files)

                if remaining < 60 and remaining_files > 5:  # Less than 1 min left, many files
                    print(f"⚡ Speed mode: {remaining:.0f}s left for {remaining_files} files")
                    # Quick copy remaining files
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_file)
                    time.sleep(0.1)
                    continue

            try:
                self.simulate_typing_file(file_path, dest_file)
                processed_files.append(file_path)
                self.files_processed += 1
            except Exception as e:
                print(f"  ❌ Failed to process {file_path.name}: {e}")
                # Fallback: simple copy
                try:
                    dest_file.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(file_path, dest_file)
                    print(f"  📄 Fallback copy successful for {file_path.name}")
                    processed_files.append(file_path)
                    self.files_processed += 1
                except Exception as copy_error:
                    print(f"  ❌ Complete failure for {file_path.name}: {copy_error}")
                    # Continue with next file

            # Update session state for resume capability
            self.session_state['processed_files'] = processed_files
            self.session_state['current_file_index'] = i

            # Update session stats
            analysis = self.analyze_file(file_path)
            self.session_stats['files_modified'] += 1
            self.session_stats['total_chars_typed'] += file_path.stat().st_size

            lang = analysis['language']
            if lang not in self.session_stats['time_by_language']:
                self.session_stats['time_by_language'][lang] = 0
            # We'll update actual time later

            # Auto-save session state after each file
            self.auto_save_session()

            # Refactoring phase - revisit earlier files
            if (self.enable_refactoring and len(processed_files) >= 3 and
                random.random() < 0.3):  # 30% chance after 3+ files
                refactor_candidates = self.get_refactoring_candidates(processed_files)
                if refactor_candidates:
                    self.simulate_refactoring_phase(refactor_candidates)
                    # Auto-save after refactoring
                    self.auto_save_session()

            # Inter-file break (must respect grace period)
            if random.random() < 0.3:  # 30% chance
                # Break time must be less than grace period to maintain coding session
                break_time = random.uniform(0.5, min(3.0, self.max_grace_period * 0.6))
                self.safe_delay(break_time, "☕ Taking a break")

        # Process binary files quickly
        print(f"\n📁 Processing {len(binary_files)} binary files...")
        for file_path in binary_files:
            relative_path = file_path.relative_to(self.source_dir)
            dest_file = self.dest_dir / relative_path
            self.copy_binary_file(file_path, dest_file)
            self.files_processed += 1

        # Store processed files for reporting
        self.processed_files = processed_files

        # Final summary with enhanced analytics
        total_elapsed = time.time() - self.start_time
        print(f"\n{'='*50}")
        print(f"✅ Simulation completed!")
        print(f"⏱️  Total time: {format_time(total_elapsed)}")
        print(f"📊 Files processed: {self.files_processed}/{self.total_files}")
        print(f"📂 Output directory: {self.dest_dir}")

        if self.mode == "manual" and self.total_hours:
            accuracy = (total_elapsed / 3600) / self.total_hours * 100
            target_time = format_time(self.total_hours * 3600)
            print(f"🎯 Target: {target_time} | Actual: {format_time(total_elapsed)} | Accuracy: {accuracy:.1f}%")

        # Generate and display analytics
        if self.enable_analytics:
            print(f"\n{'='*50}")
            print("📈 SESSION ANALYTICS")
            print(f"{'='*50}")

            report = self.generate_session_report(total_elapsed)

            # Display summary
            summary = report['summary']
            print(f"⌨️  Characters typed: {summary['chars_typed']:,}")
            print(f"🚀 Average typing speed: {summary['avg_typing_speed']:.0f} chars/min")
            print(f"🔄 Refactoring sessions: {summary['refactoring_sessions']}")
            print(f"🐛 Debugging sessions: {summary['debugging_sessions']}")

            # Display language breakdown
            if report['by_language']:
                print(f"\n📝 LANGUAGE BREAKDOWN:")
                for lang, data in sorted(report['by_language'].items(), key=lambda x: x[1]['chars'], reverse=True):
                    time_seconds = data['estimated_time_minutes'] * 60
                    print(f"  {lang}: {data['files']} files, {data['chars']:,} chars, {format_time(time_seconds)}")

            # Display productivity metrics
            if report['productivity_metrics']:
                print(f"\n⚡ PRODUCTIVITY METRICS:")
                metrics = report['productivity_metrics']
                print(f"  Chars/minute: {metrics['chars_per_minute']:.0f}")
                print(f"  Files/hour: {metrics['files_per_hour']:.1f}")
                print(f"  Avg file size: {metrics['avg_file_size']:.0f} chars")

            # Create final session folder for this project
            try:
                final_session_dir = self.create_final_session_folder()

                # Export analytics to final session folder with error handling
                try:
                    csv_dir = self.export_to_csv(report, final_session_dir)
                except Exception as e:
                    print(f"  ⚠️  CSV export failed: {e}")
                    csv_dir = "CSV export failed"

                try:
                    json_file = self.save_session_json(report, final_session_dir)
                except Exception as e:
                    print(f"  ⚠️  JSON export failed: {e}")
                    json_file = "JSON export failed"

                # Generate visual timeline with error handling
                try:
                    self.timeline.generate_timeline_chart(final_session_dir)
                    timeline_status = f"{final_session_dir}/timeline.txt"
                except Exception as e:
                    print(f"  ⚠️  Timeline generation failed: {e}")
                    timeline_status = "Timeline generation failed"

                print(f"\n📊 Analytics exported successfully!")
                print(f"  📁 Session folder: {final_session_dir}")
                print(f"  📈 CSV files: {csv_dir}")
                print(f"  📄 JSON report: {json_file}")
                print(f"  📊 Timeline chart: {timeline_status}")

                # Clean up temporary session file
                if self.resume_file.exists():
                    try:
                        self.resume_file.unlink()
                        print("🧹 Cleaned up temporary session file")
                    except Exception:
                        pass

            except Exception as e:
                print(f"\n⚠️  Warning: Could not export analytics: {e}")
        else:
            print(f"\n📊 Analytics disabled (use --no-analytics to skip)")


def main():
    parser = argparse.ArgumentParser(
        description="Wakatimer - Generate retroactive coding time data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Auto mode - automatically determine coding time
  wakatimer /path/to/source /path/to/dest --mode auto

  # Manual mode - specify exact coding time
  wakatimer /path/to/source /path/to/dest --mode manual --hours 14.5

  # Quick test with 2 hours
  wakatimer ./my_project ./simulated_project --mode manual --hours 2
        """
    )

    parser.add_argument("source", nargs="?", help="Source directory containing the coding project")
    parser.add_argument("dest", nargs="?", help="Destination directory for simulated project")
    parser.add_argument("--mode", choices=["auto", "manual"], default="auto",
                       help="Simulation mode (default: auto)")
    parser.add_argument("--hours", type=float,
                       help="Total coding hours for manual mode (supports decimals)")
    parser.add_argument("--no-refactoring", action="store_true",
                       help="Disable refactoring phases")
    parser.add_argument("--no-analytics", action="store_true",
                       help="Skip analytics generation and export")
    parser.add_argument("--grace-period", type=float, default=90.0,
                       help="Grace period in seconds between content changes (default: 90)")
    parser.add_argument("--interactive", action="store_true",
                       help="Enable interactive setup mode")
    parser.add_argument("--template", type=str,
                       help="Use project template (web_app, data_science, custom)")
    parser.add_argument("--ignore", action="append", default=[],
                       help="Ignore files/patterns (can be used multiple times)")
    parser.add_argument("--resume", action="store_true",
                       help="Resume previous session if available")
    parser.add_argument("--no-testing", action="store_true",
                       help="Disable testing cycle simulation")
    parser.add_argument("--no-research", action="store_true",
                       help="Disable research pause simulation")
    parser.add_argument("--no-copy-paste", action="store_true",
                       help="Disable copy-paste speed simulation")
    parser.add_argument('--version', action='store_true', help='Show program version and logo')

    args = parser.parse_args()

    if getattr(args, 'version', False):
        print_logo()
        print('Wakatimer Version:', '2.0.2')
        return 0

    if not args.source or not args.dest:
        parser.print_help()
        parser.exit(1)

    # Validation
    if args.mode == "manual" and args.hours is None:
        parser.error("Manual mode requires --hours parameter")

    if args.hours is not None and args.hours <= 0:
        parser.error("Hours must be positive")

    if args.hours is not None and args.hours >= 24:
        parser.error("Hours must be less than 24")

    source_path = Path(args.source)
    if not source_path.exists():
        print(f"❌ Source directory does not exist: {source_path}")
        return 1

    if not source_path.is_dir():
        print(f"❌ Source path is not a directory: {source_path}")
        return 1

    dest_path = Path(args.dest)
    if dest_path.exists() and any(dest_path.iterdir()):
        response = input(f"⚠️  Destination directory {dest_path} is not empty. Continue? (y/N): ")
        if response.lower() != 'y':
            print("Operation cancelled.")
            return 1

    # Create default templates if they don't exist
    create_default_templates()

    # Create and run simulator
    simulator = CodingSimulator(
        source_dir=str(source_path),
        dest_dir=str(dest_path),
        mode=args.mode,
        total_hours=args.hours
    )

    # Apply command line options
    simulator.max_grace_period = getattr(args, 'grace_period', 90.0)
    simulator.enable_refactoring = not getattr(args, 'no_refactoring', False)
    simulator.enable_analytics = not getattr(args, 'no_analytics', False)
    simulator.enable_testing_cycles = not getattr(args, 'no_testing', False)
    simulator.enable_research_pauses = not getattr(args, 'no_research', False)
    simulator.enable_copy_paste = not getattr(args, 'no_copy_paste', False)
    simulator.interactive_mode = getattr(args, 'interactive', False)
    simulator.ignore_patterns = set(getattr(args, 'ignore', []))

    # Load project template if specified
    if getattr(args, 'template', None):
        simulator.project_template = load_project_template(args.template)
        if simulator.project_template:
            print(f"✅ Loaded template: {simulator.project_template.get('name', args.template)}")
        else:
            print(f"⚠️  Template {args.template} not found, using defaults")

    try:
        simulator.run_simulation()
        return 0
    except KeyboardInterrupt:
        print("\n\n⚠️  Simulation interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
