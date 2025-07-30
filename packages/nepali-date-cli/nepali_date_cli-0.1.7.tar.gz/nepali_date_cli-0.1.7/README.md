# Nepali Date CLI

A simple command-line tool to display Nepali dates with beautiful boxed output and Nepali numerals (देवनागरी अंक).

## Installation

You can install this package using pip:

```bash
pip install nepali-date-cli
```

To upgrade to the latest version:

```bash
pip install --upgrade nepali-date-cli
```

## Usage

### Command Line
After installation, you can use the `miti` command in your terminal:

```bash
miti
```

This will display both the current English date and the corresponding Nepali date with Nepali numerals in a beautiful boxed format.

> **Note:** The old `nepdate` command is deprecated and will show a warning. Please use `miti` instead.

## Example Output

```
┌─────────────────────────────────────────────────────────┐
│                     Today's Date                        │
├─────────────────────────────────────────────────────────┤
     नेपाली मिति    २०८२-३-१४ (असार १४)      शनिबार       
     English Date   2025-06-28 (June 28)     Saturday       
└─────────────────────────────────────────────────────────┘
```

## Features

- Displays current English date with day name
- Shows Nepali date in Devanagari numerals (देवनागरी अंक)
- Includes Nepali day names (e.g., आइतबार, सोमबार, etc.)
- Beautiful boxed output format
- Simple command-line interface
- Can be used as a Python module

## Requirements

- Python 3.6+
- nepali-datetime package (automatically installed)


