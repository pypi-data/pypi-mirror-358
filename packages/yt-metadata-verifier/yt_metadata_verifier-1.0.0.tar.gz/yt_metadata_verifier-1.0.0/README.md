# 🎥 YouTube Metadata Verifier CLI

A lightweight Python CLI tool to **verify and correct YouTube video metadata**, such as title and channel information. Useful for digital archiving, content validation, or simply cleaning up saved URLs.

---

## ✨ Features

- ✅ Fetch accurate video titles and channel names from YouTube
- ✅ Compare or correct existing metadata
- ✅ Outputs valid and error entries to separate JSON files
- ✅ Clean CLI with `--version`, `--verbose`, and `--help` support
- ✅ Packaged with [Poetry](https://python-poetry.org/)

---

## 📦 Installation

### 1. Clone the repo

```bash
git clone https://github.com/taj54/youtube-metadata-verifier.git
cd youtube-metadata-verifier
```

### 2. Install dependencies

```bash
poetry install
```

### 3. Use the CLI

```bash
poetry run yt-verify --help
```

---

## ⚙️ Usage

### Basic Command

```bash
poetry run yt-verify --json data/videos.json
```

### Full Example

```bash
poetry run yt-verify   --json data/videos.json   --output data/corrected.json   --errors data/errors.json   --verbose
```

### Available Options

| Option        | Description                                   |
|---------------|-----------------------------------------------|
| `--json`      | Path to input JSON file with video URLs       |
| `--output`    | File to save corrected metadata (default: `corrected.json`) |
| `--errors`    | File to save errors (default: `errors.json`)  |
| `--verbose`   | Enable detailed logging                       |
| `--version`   | Show current CLI version                      |

---

## 📄 Input Format

Your input file should be a JSON array with at least a `url` field for each video:

```json
[
  {
    "url": "ttps://www.youtube.com/watch?v=WH0lsTxcw4w"
  }
]
```

---

## 📝 Output Example

```json
[
  {
    "title": "Midnight Coding Session 💻 Coding Lofi Music To Make You Deep Focus On You Work 💻 Programming Lofi",
    "url": "https://www.youtube.com/watch?v=WH0lsTxcw4w",
    "duration": "11:11:55",
    "tags": [
      "Dream lofi",
      "Dream lofi channel",
      "Study",
      "Sleep",
      "study music",
      "lofi hip hop",
      "chill lofi",
      "lofi music",
      "lofi study",
      "lofi sleep",
      "sleep music",
      "Deep Sleeping Music",
      "chill music",
      "lofi studying",
      "studying lofi",
      "lofi",
      "dreamy lofi",
      "lofi girl",
      "stop overthinking",
      "sleep lofi",
      "lofi sleep music",
      "lofi live",
      "sleeping music for deep sleeping",
      "lo fi",
      "Midnight Coding Session",
      "Coding Lofi Music",
      "Deep Focus On You Work",
      "Programming Lofi",
      "lofi corgi",
      "corgi lofi",
      "lofi programming",
      "programming lofi"
    ],
    "channel": {
      "name": "Dreamy Lofi",
      "url": "https://www.youtube.com/@Mellow_lofi"
    }
  }
]
```

---

## 🐛 Error Handling

Any failed lookups are saved to the `--errors` file:

```json
[
  {
    "url": "https://www.youtube.com/watch?v=invalid",
    "error": "Video unavailable"
  }
]
```

---

## 🧪 Dev Tips

### Run locally

```bash
python src/yt_metadata_verifier/cli.py --json data/videos.json
```

### Export as CLI tool

```bash
poetry build
pip install dist/yt_metadata_verifier-<version>.whl
yt-verify --version
```

---

## 📄 License

[MIT](LICENSE) © [taj](https://github.com/taj54)

---