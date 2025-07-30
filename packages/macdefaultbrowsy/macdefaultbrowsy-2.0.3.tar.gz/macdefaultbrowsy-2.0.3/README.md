
# macdefaultbrowsy

A command-line tool and package (written in Python) for macOS that allows you to view installed browsers and set the default web browser, with automatic dialog confirmation.

## Features

- List all installed web browsers with the current default marked with `*`
- Set any browser as the default with a simple command
- Automatically confirms the system dialog (no manual clicking required)
- Built as a universal binary (Intel + Apple Silicon)
- Simple installation via Homebrew or manual install

## Installation

```bash
uv pip install --system macdefaultbrowsy
```

or

```bash
pip install git+https://github.com/twardoch/macdefaultbrowsy
```

## Usage

### Command Line

#### List all browsers

```bash
macdefaultbrowsy
```

Output example:
```
  chrome
  firefox
* safari
  edge
```

#### Set default browser

```bash
macdefaultbrowsy chrome
```

The tool will automatically set Chrome as your default browser and confirm the system dialog.

### Python API

```python
from macdefaultbrowsy import macdefaultbrowsy

# Get the current default browser
current = macdefaultbrowsy.read_default_browser()
print(f"Current default browser: {current}")

# List all available browsers
browsers = macdefaultbrowsy._get_available_browsers()
print("Available browsers:")
for name in sorted(browsers.keys()):
    print(f"  {name}")

# Set a new default browser
success = macdefaultbrowsy.set_default_browser("chrome")
if success:
    print("Successfully set Chrome as default browser")
else:
    print("Failed to set default browser")
```


## How it Works

The tool uses the macOS Launch Services API to:
1. Query all installed applications that can handle HTTP/HTTPS URLs
2. Get the current default browser
3. Set a new default browser for both HTTP and HTTPS schemes

When setting a new default browser, the tool also uses AppleScript automation to automatically click the confirmation button in the system dialog, providing a seamless experience.

## Development

To capture a snapshot of the codebase:

```bash
npx repomix -i ".giga,.cursorrules,.cursor,*.md" -o llms.txt .
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## References

- Check [macdefaultbrowser](https://github.com/twardoch/macdefaultbrowser) for a similar tool written in Swift.