# CreateFile with Designated Encoding ✨

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding/blob/main/LICENSE)
[![PyPI Version](https://img.shields.io/pypi/v/stv_create_file)](https://pypi.org/project/stv_create_file/)
[![Python Versions](https://img.shields.io/pypi/pyversions/stv_create_file)](https://pypi.org/project/stv_create_file/)

[中文文档](./README.md)

**CreateFile with Designated Encoding** is a powerful command-line tool for creating files with specified encoding formats, supporting custom metadata tags and multi-language prompts.

> Create Some File with Designated Encoding

## 🌟 Core Features

- **Specify File Encoding** - Create files with various encodings including UTF-8, GBK, Big5, etc.
- **Metadata Tags** - Customize metadata format in the first line of files
- **Multi-language Support** - Automatically adapts to English/Chinese interfaces
- **Encoding Verification** - Auto-detect file encoding after creation
- **Exclusive Mode** - Prevent accidental overwriting of existing files
- **Verbose Logging** - Optional detailed output mode
- **User Configuration** - Save preferences to config file

## 🚀 Installation

### Install via PyPI

```bash
pip install stv_create_file
```

### Install from GitHub Source

```bash
git clone https://github.com/StarWindv/CreateFile-with-DesignatedEncoding.git
cd CreateFile-with-DesignatedEncoding
pip install .
```

## 🛠 Usage Guide

### Basic Commands

```bash
create [file_path] [options]
nf [file_path] [options]      # Short for newfile
newfile [file_path] [options] # Full command
```

### Command Options

| Option           | Shortcut | Default | Description                        |
|------------------|----------|---------|------------------------------------|
| `--encoding`     | `-e`     | `utf-8` | File encoding format               |
| `--prefix`       | `-p`     | `#`     | File header prefix                 |
| `--left-paren`   | `-l`     | `<\|`   | Left metadata tag                  |
| `--right-paren`  | `-r`     | `\|>`   | Right metadata tag                 |
| `--monopolize`   | `-m`     | `False` | Exclusive mode (prevent overwrite) |
| `--coding-check` | `-cc`    | `False` | Verify encoding after creation     |
| `--verbose`      | `-v`     | `False` | Verbose output mode                |
| `--version`      | `-V`     | -       | Show version info                  |
| `--license`      | `-lic`   | -       | Show project license               |

### Usage Examples

1. **Create Basic File**
   ```bash
   create example.txt
   ```

2. **Specify File Encoding**
   ```bash
   nf data.csv -e gbk
   ```

3. **Custom Metadata Format**
   ```bash
   newfile config.ini -p "// " -l "{{" -r "}}"
   ```

4. **Create in Exclusive Mode**
   ```bash
   create important.log -m
   ```

5. **Create with Encoding Verification**
   ```bash
   nf report.txt -e big5 -cc -v
   ```

## ⚙️ Configuration File

Configuration path: `~/.stv_project/config.json`

**Default Configuration:**
```json
{
    "lang": "English",
    "verbose": false
}
```

**Configurable Items:**
- `lang`: Interface language (`English`/`zh-cn`)
- `verbose`: Enable verbose output by default

## 📂 Project Structure

```
CreateFile-with-DesignatedEncoding/
├── LICENSE
├── pyproject.toml
├── README.md
├── README.en.md
└── src/
    └── stv_create_file/
        ├── core/
        │   ├── __init__.py
        │   ├── FileCreator.py    # File creation core logic
        │   └── stv_parse.py      # CLI argument parsing
        ├── main.py               # Program entry point
        ├── mul_lang/
        │   ├── __init__.py
        │   └── change_text.py    # Multi-language support
        └── utils/
            ├── __init__.py
            ├── GetConfig.py      # Configuration management
            └── utils.py          # Utility functions
```

## 📦 Dependencies

- `chardet` - File encoding detection library

## 📜 License

This project is licensed under [MIT License](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding/blob/main/LICENSE)

## 🤝 Contribution Guidelines

Contributions via Issues or Pull Requests are welcome!  
Project URL: [GitHub Repository](https://github.com/StarWindv/CreateFile-with-DesignatedEncoding)