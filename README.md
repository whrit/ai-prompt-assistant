# AI Prompt Assistant

A macOS menubar application that enhances your AI interactions by optimizing prompts and providing quick access to AI services.

![AI Prompt Assistant Logo](resources/icons/logo.png)

## Features

- **Always Available**: Lives in your menubar for instant access
- **Keyboard Shortcut**: Quickly open the input dialog with a customizable shortcut
- **Prompt Optimization**: Automatically rephrases your prompts for better AI responses
- **Multiple AI Services**: Works with ChatGPT and other AI platforms (default: ChatGPT)
- **Input History**: Keeps track of your previous prompts for easy reuse
- **Localization**: Supports multiple languages
- **Automatic Updates**: Checks for new versions to keep you up to date

## Installation

### Requirements

- macOS 10.14 or later
- Python 3.8 or later (for development)

### User Installation

1. Download the latest release from the [Releases](https://github.com/username/ai-prompt-assistant/releases) page
2. Open the DMG file
3. Drag AI Prompt Assistant to your Applications folder
4. Launch the application

### Development Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/username/ai-prompt-assistant.git
   cd ai-prompt-assistant
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run the application in development mode:

   ```bash
   python src/main.py
   ```

## Usage

### Quick Start

1. Click on the AI Prompt Assistant icon in your menubar
2. Select "Open Input" or use the keyboard shortcut (default: ⌘⇧Space)
3. Type your prompt in the input dialog
4. Click "Ask" or press Enter
5. Your optimized prompt will be sent to your selected AI service in your default browser

### API Key Setup

1. Click on the AI Prompt Assistant icon in your menubar
2. Select "Settings"
3. Go to the "AI Selection" tab
4. Enter your OpenAI API key in the provided field
5. Click "Test Key" to verify your API key works correctly
6. Click "OK" to save your settings

Your API key will be securely stored in your system's keychain and will be used for prompt optimization.

### Settings

Access settings by clicking on the menubar icon and selecting "Settings":

- **Keyboard Shortcut**: Change the default shortcut
- **Input History**: View and manage your previous prompts
- **AI Selection**: Choose your preferred AI service and set up your OpenAI API key
- **Language**: Change the application language
- **Startup**: Configure the app to launch at login
- **Updates**: Check for updates or enable automatic update checks
- **About**: View application information, version, and credits

## Building from Source

To build a standalone application:

```bash
python setup.py py2app
```

The built application will be available in the `dist` directory.

## Project Structure

```free
ai-prompt-assistant/
├── src/                  # Source code
├── resources/            # Icons and localization files
├── tests/                # Unit tests
├── setup.py              # py2app setup script
├── requirements.txt      # Project dependencies
└── README.md             # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [rumps](https://github.com/jaredks/rumps) - Ridiculously Uncomplicated Mac OS X Python Statusbar apps
- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - Python bindings for the Qt application framework
- [py2app](https://github.com/ronaldoussoren/py2app) - Create standalone Mac OS X applications with Python
