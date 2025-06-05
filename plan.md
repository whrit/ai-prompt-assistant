# AI Prompt Assistant - Development Plan

## Project Overview

AI Prompt Assistant is a macOS menubar application that allows users to quickly input prompts, have them rephrased, and submit them to their preferred AI service (default: ChatGPT). The application stays in the menubar, provides keyboard shortcut access, and maintains input history.

## Technical Stack

- **Language**: Python
- **UI Framework**: rumps (for menubar functionality) + PyQt6/PySide6 (for custom input dialog)
- **Packaging**: py2app (for creating standalone macOS application)
- **Dependencies**: requests, json, webbrowser, keyring (for secure storage)

## Project Structure

```free
ai-prompt-assistant/
├── src/
│   ├── __init__.py
│   ├── main.py              # Application entry point
│   ├── menubar.py           # Menubar implementation
│   ├── input_dialog.py      # Custom input dialog
│   ├── settings_manager.py  # Settings management
│   ├── history_manager.py   # History management
│   ├── api_client.py        # API client for rephrasing
│   ├── version_checker.py   # Version checking functionality
│   └── utils.py             # Utility functions
├── resources/
│   ├── icons/               # Application icons
│   └── localization/        # Localization files (en, es, de, sv, tr)
├── tests/                   # Unit tests
├── setup.py                 # py2app setup script
├── requirements.txt         # Project dependencies
└── README.md                # Project documentation
```

## Development Phases

### Phase 1: Basic Structure (Week 1)

- [x] Set up project structure
- [x] Create menubar app with icon
- [x] Implement settings manager
- [x] Create keyboard shortcut registration (using pynput)
- [x] Build input dialog

### Phase 2: Core Functionality (Week 2)

- [x] Implement prompt rephrasing API client
- [x] Connect input dialog to API client
- [x] Implement browser opening with rephrased prompt
- [x] Create history manager for storing past inputs
- [x] Implement settings UI (language selection)

### Phase 3: Advanced Features (Week 3)

- [x] Add localization support (English, Spanish, German, Swedish, Turkish)
- [x] Implement version checking
- [x] Add startup item functionality
- [x] Implement language selection UI
- [x] Implement global keyboard shortcut (⌘ZX) with pynput
- [x] Add accessibility permissions detection and alert
- [ ] Create about dialog
- [ ] Implement history management UI

### Phase 4: Testing and Packaging (Week 4)

- [ ] Write unit tests
- [ ] Perform integration testing
- [ ] Package application with py2app
- [ ] Create installer
- [ ] Prepare for distribution

## API Endpoints

### Rephrase API

- **Endpoint**: `https://api.example.com/rephrase`
- **Method**: POST
- **Request Body**:

  ```json
  {
    "text": "User input text",
    "target_ai": "chatgpt"
  }
  ```

- **Response**:

  ```json
  {
    "rephrased_text": "Optimized prompt text"
  }
  ```

### Version Check API

- **Endpoint**: `https://api.example.com/version`
- **Method**: GET
- **Response**:

  ```json
  {
    "version": "1.1.0",
    "title": "New Version Available",
    "text": "Version 1.1.0 includes bug fixes and new features."
  }
  ```

## User Interface Design

### Menubar Icon

- Simple AI icon that fits with macOS design
- Context menu with 4 main options

### Input Dialog

- Centered on screen
- Multi-line text input
- Submit button
- Character counter
- Minimalist design

### Settings Dialog

- Tabbed interface with sections for:
  - General (keyboard shortcut, startup)
  - History (view, clear)
  - AI Selection
  - Language
  - Updates

## Data Storage

- Settings: JSON file in user's application data directory (Implemented)
- History: SQLite database for efficient storage and querying (Implemented)
- Secure data: keyring/keychain for any sensitive information (Implemented)

## Future Enhancements (v2.0)

- Multiple AI service support
- Custom templates for different AI services
- Cloud sync of history and settings
- Advanced prompt engineering features
- Direct API integration (no browser required)
