# 🚀 Wakatimer: Retroactive Time Tracking Simulator

[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![PyPI version](https://img.shields.io/pypi/v/wakatimer.svg)](https://pypi.org/project/wakatimer/)
[![Test Coverage](https://img.shields.io/badge/coverage-98%25-green.svg)](.coveragerc)

Wakatimer is a Python-based CLI tool that simulates human-like coding behavior to generate realistic, retroactive time-tracking data. It's perfect for populating services like WakaTime with historical data for projects you worked on before you started time tracking.

## Key Features

-   **Interactive Setup**: A guided, interactive mode for easy configuration.
-   **Flexible Simulation Modes**: Choose between automatic time estimation or manual duration specification.
-   **Project Templates**: Pre-configured settings for common development workflows (e.g., web app, data science).
-   **Intelligent File Processing**: Smart ordering of files based on type and dependencies, with realistic typing and delays.
-   **Resume Capability**: Pause and resume long simulations without losing progress.
-   **Advanced Human-like Behavior**: Simulates refactoring, debugging, research pauses, and even copy-paste actions.
-   **Comprehensive Analytics**: Detailed session reports, language statistics, and productivity metrics with export options.
-   **Time Tracking Compatibility**: Designed to respect common time-tracking application behaviors like grace periods.

## Installation

Install Wakatimer directly from PyPI:

```bash
pip install wakatimer
```

Alternatively, for development, clone the repository and install in editable mode:
```bash
git clone https://github.com/sukarth/Wakatimer.git
cd Wakatimer
pip install -e .[dev]
```

## Getting Started: First Simulation

Run your first simulation in **interactive mode**. This is the easiest way to get started, as it will guide you through all the required settings.

1.  **Run the interactive command**:
    ```bash
    wakatimer --interactive
    ```

2.  **Follow the prompts**:
    -   Select the source directory of the project you want to simulate.
    -   Choose a destination directory for the output.
    -   Pick a simulation mode (auto or manual).
    -   Enable or disable features like refactoring and testing cycles.

Wakatimer will then analyze your project, display an execution plan, and ask for confirmation before starting the simulation.



## 📋 Command Line Reference

```
wakatimer <source_dir> <dest_dir> [options]

Arguments:
  source_dir              Source directory containing your coding project
  dest_dir                Destination directory for the simulated project

Core Options:
  --mode {auto, manual}    Simulation mode (default: auto)
  --hours HOURS            Total coding hours for manual mode (supports decimals)
  --interactive            Enable interactive setup mode with guided configuration

Features:
  --template NAME          Use project template (web_app, data_science, custom)
  --no-refactoring         Disable refactoring phases
  --no-testing             Disable testing cycle simulation
  --no-research            Disable research pause simulation
  --no-copy-paste          Disable copy-paste speed simulation
  --no-analytics           Skip analytics generation and export

Advanced:
  --grace-period SECONDS   Grace period between content changes (default: 90)
  --ignore PATTERN         Ignore files/patterns (can be used multiple times)
  --resume                 Resume previous session if available
```



## 📁 Project Templates

Pre-configured templates for different project types:

### 🌐 Web Application (`web_app.json`)
- **Optimized for**: Frontend/Backend web development
- **File priorities**: Config → Core JS/TS/Python → Tests → Docs
- **Speed adjustments**: Faster HTML/CSS, slower TypeScript
- **Features**: Higher refactoring probability, moderate debugging

### 📊 Data Science (`data_science.json`)
- **Optimized for**: ML and data analysis projects
- **File priorities**: Config → Python/Jupyter → Data files → Docs
- **Speed adjustments**: Slower Python (complex algorithms), very slow Jupyter
- **Features**: High refactoring probability, high debugging probability

### 📱 Mobile App (`mobile_app.json`)
- **Optimized for**: iOS/Android mobile development
- **File priorities**: Config → Core → UI → Platform-specific → Tests
- **Speed adjustments**: Slower Swift/Kotlin, faster XML/JSON
- **Features**: High debugging, moderate refactoring

### 🔧 Backend API (`backend_api.json`)
- **Optimized for**: REST APIs and microservices
- **File priorities**: Config → Models → Routes → Middleware → Tests
- **Speed adjustments**: Optimized for server-side languages
- **Features**: High refactoring, moderate debugging

### 🎮 Game Development (`game_development.json`)
- **Optimized for**: Video game development
- **File priorities**: Config → Gameplay → Graphics → Audio → UI
- **Speed adjustments**: Slower C++/C#, very slow shaders
- **Features**: High debugging, moderate testing

### ⚙️ DevOps & Infrastructure (`devops_infrastructure.json`)
- **Optimized for**: Infrastructure as Code, CI/CD
- **File priorities**: Config → Infrastructure → Containers → Scripts
- **Speed adjustments**: Faster YAML/JSON, slower Terraform
- **Features**: High testing, moderate research

### 🖥️ Desktop Application (`desktop_application.json`)
- **Optimized for**: Cross-platform desktop apps
- **File priorities**: Config → Core → UI → Components → Resources
- **Speed adjustments**: Balanced for desktop frameworks
- **Features**: Moderate refactoring and debugging

### 🔐 Cybersecurity (`cybersecurity.json`)
- **Optimized for**: Security tools and penetration testing
- **File priorities**: Tools → Exploits → Analysis → Reports
- **Speed adjustments**: Slower assembly, faster scripting
- **Features**: High research, moderate debugging

### 🤖 Machine Learning (`machine_learning.json`)
- **Optimized for**: ML models and AI research
- **File priorities**: Notebooks → Models → Data → Training → Evaluation
- **Speed adjustments**: Slower Python/Jupyter, faster configs
- **Features**: High research, moderate refactoring

### ⛓️ Blockchain & Crypto (`blockchain_crypto.json`)
- **Optimized for**: Smart contracts and DeFi
- **File priorities**: Contracts → Scripts → Frontend → Tests
- **Speed adjustments**: Very slow Solidity/Rust, faster JS/TS
- **Features**: High refactoring and testing

### 🔌 Embedded & IoT (`embedded_iot.json`)
- **Optimized for**: Embedded systems and IoT devices
- **File priorities**: Config → Drivers → Firmware → Protocols
- **Speed adjustments**: Very slow C/Assembly, moderate C++
- **Features**: High debugging, moderate research

### Custom Templates
Create your own templates in `templates/custom.json`:

```json
{
  "name": "My Custom Template",
  "description": "Custom project workflow",
  "file_priorities": {
    "config": ["*.json", "*.yml"],
    "core": ["*.py", "*.js"],
    "tests": ["*test*"],
    "docs": ["*.md"]
  },
  "typing_speed_multipliers": {
    "Python": 0.9,
    "JavaScript": 1.1
  },
  "refactoring_probability": 0.3,
  "debugging_probability": 0.2
}
```

## Usage and Examples

All commands use the `wakatimer` entry point.

### Basic Syntax
```bash
wakatimer [source_directory] [destination_directory] [options]
```

### Simulation Modes

-   **Auto Mode (Default)**: Automatically estimates coding time based on project complexity.
    ```bash
    wakatimer ./my-project ./output-dir --mode auto
    ```

-   **Manual Mode**: Specify an exact duration in hours.
    ```bash
    # Simulate 8.5 hours of work
    wakatimer ./my-project ./output-dir --mode manual --hours 8.5
    ```

### Using Project Templates

Use pre-defined templates for different project types.

```bash
# Use the web application template
wakatimer ./my-project ./output-dir --template web_app

# Use the data science template
wakatimer ./my-project ./output-dir --template data_science
```
You can also create custom templates in the `templates/` directory and load them.

### Ignoring Files

Exclude specific files or directories using glob patterns. The `--ignore` flag can be used multiple times.

```bash
# Ignore log files and the node_modules directory
wakatimer ./my-project ./output-dir --ignore "*.log" --ignore "node_modules/*"
```

### Resuming a Session

Long simulations can be paused (`Ctrl+C`) and resumed later. Wakatimer automatically saves progress.

```bash
# Start a long simulation
wakatimer ./big-project ./output-dir --mode manual --hours 20

# If interrupted, resume it later using the --resume flag
wakatimer ./big-project ./output-dir --resume
```

## How It Works

### Time Tracking Logic
The script simulates the behavior of time tracking apps:
- Continuous activity detection through file modifications
- Grace periods between changes (up to ~1.5 minutes)
- Realistic coding session patterns

### File Processing
1. **Analysis Phase**: Scans project structure and categorizes files
2. **Setup Phase**: Simulates initial project setup (30s-2min)
3. **Coding Phase**: Processes code files with human-like behavior
4. **Asset Phase**: Quickly copies binary files and assets
5. **Summary**: Reports total time and accuracy

### Realistic Delays Include
- Planning and reading time before coding
- Variable typing speeds based on file complexity
- Debugging phases (20% chance per file)
- Micro-pauses during typing
- Break times between files
- Code review periods

### Advanced Simulation Features

Wakatimer includes several features to make the generated data look more human and realistic.

-   **Testing Cycles**: Simulates a realistic test-driven development workflow: write code → write test → test fails → fix code → test passes.
-   **Research Pauses**: Adds thinking time for complex problems, with longer pauses for more complex algorithms.
-   **Copy-Paste Simulation**: Mimics real coding behavior where some content appears faster, simulating copy-pasting from external sources. This applies primarily to larger files to maintain realism.

## Supported File Types

### Code Files (Full Simulation)
- **Languages**: Python, JavaScript, TypeScript, Java, C++, C#, PHP, Ruby, Go, Rust, Swift, Kotlin, and 30+ more
- **Config**: JSON, YAML, XML, TOML, INI files
- **Documentation**: Markdown, reStructuredText, plain text
- **Web**: HTML, CSS, SCSS, Vue, Svelte
- **Scripts**: Shell, PowerShell, Batch files

### Binary Files (Quick Copy)
- Images: JPG, PNG, GIF, SVG, etc.
- Videos: MP4, AVI, MOV, etc.
- Audio: MP3, WAV, OGG, etc.
- Archives: ZIP, RAR, TAR, etc.
- Executables: EXE, DLL, SO, etc.
- Documents: PDF, DOC, XLS, etc.

### Automatically Skipped
- node_modules, .git, .svn directories
- Build outputs: dist, build, target, bin, obj
- Cache directories: __pycache__, .pytest_cache
- IDE files: .idea, .vscode, .vs


## Session Management and Analytics

All session data, including progress files and final reports, is stored in the `WakatimerSessions/` directory.

### Folder Structure

-   **Resume Files**: Temporary `.pkl` files store session state, allowing you to resume if the simulation is interrupted.
-   **Completed Sessions**: Each completed simulation gets its own timestamped folder.

```
WakatimerSessions/
├── project_name_session.pkl          # Temporary session files (for resume)
├── WakatimerSession_project_20241225_143022/  # Completed sessions
│   ├── project_session.pkl           # Final session data
│   ├── session_report.json           # Detailed analytics
│   ├── timeline.txt                  # Visual timeline (ASCII art)
│   └── analytics/                    # CSV exports
│       ├── session_summary.csv
│       └── language_breakdown.csv
└── WakatimerSession_webapp_20241225_150145/   # Another project session
    └── ...
```

### Analytics Export Formats

-   **CSV Files (`analytics/`)**:
    -   `session_summary.csv`: Overall session metrics.
    -   `language_breakdown.csv`: Time spent per programming language.
-   **JSON Report (`session_report.json`)**: Complete session metadata, detailed productivity metrics, and timeline data.
-   **Timeline Chart (`timeline.txt`)**: A visual ASCII timeline providing an hourly breakdown with language distribution and session flow visualization.

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing guidelines, and pull request instructions.

## Changelog

For a detailed history of changes, please refer to [CHANGELOG.md](CHANGELOG.md).

## License

This tool is provided as-is for educational and personal use under the MIT License. Use responsibly and in accordance with your time tracking service's terms of service. See the [License](LICENSE) for more details.

----

**Made with ❤️ by Sukarth Achaya**
