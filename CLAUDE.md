# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Common Development Commands

### Running the Application
```bash
# Development mode (PyQt6-based implementation)
python src/main.py

# Alternative entry point (wrapper)
python run_app.py

# Run the newer rumps-based implementation directly
python -c "from src.app import run; run()"
```

### Building and Packaging
```bash
# Build standalone macOS app using py2app
python setup.py py2app

# Use the build script (includes environment setup)
./build_app.sh

# Create DMG installer (after building)
./create_dmg.sh
```

### Testing
```bash
# Run tests with pytest (no specific test runner configured)
python -m pytest tests/

# Run specific test file
python -m pytest tests/test_redaction.py
```

### Virtual Environment Setup
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Architecture Overview

### Dual Implementation Structure
The application has two main implementations:

1. **Legacy Implementation** (`src/menubar.py`): Original PyQt6-based menubar app with separate dialog components
2. **Current Implementation** (`src/app.py`): Modern rumps-only implementation with enhanced features

The entry points route to different implementations:
- `src/main.py` → `MenuBarApp` (PyQt6-based)
- `src/app.py` → `AIPromptAssistant` (rumps-based)

### Core Architecture Layers

#### 1. Menubar Interface Layer
- **rumps**: Provides macOS menubar integration
- **MenuBarApp** / **AIPromptAssistant**: Main application classes
- Handles global keyboard shortcuts via `pynput`

#### 2. AI Service Layer (`src/services.py`)
- Multi-provider support: ChatGPT Web, OpenAI API, Anthropic, Ollama
- Cost estimation and latency prediction
- Model validation and availability checking
- Streaming response handling

#### 3. Prompt Processing Pipeline
- **Input**: Raw user text or clipboard/selection content
- **Redaction** (`src/redaction.py`): Removes sensitive data (emails, phones, API keys)
- **Optimization** (`src/prompt_optimizer.py`): Enhances prompts for better AI responses
- **Templates** (`src/templates.py`): Pre-defined prompt templates
- **Output**: Processed text sent to AI service

#### 4. Data Management
- **Settings** (`src/settings_manager.py`): User preferences with keyring security
- **History** (`src/history_manager.py`): Prompt history tracking
- **Storage** (`src/storage.py`): Configuration and favorites management
- **Pricing** (`src/pricing.py`): Service cost and model configurations

#### 5. UI Components (PyQt6-based)
- **Input Dialog**: Main prompt entry interface
- **Settings Dialog**: Multi-tab configuration interface
- **History Dialog**: Prompt history browser
- **About Dialog**: Application information
- **Streaming Popover**: Real-time AI responses

### Key Design Patterns

#### Configuration Management
- JSON-based settings stored in `~/Library/Application Support/AI Prompt Assistant/`
- Secure API key storage via macOS keyring
- Per-template A/B testing preferences
- Multi-language localization support

#### Service Provider Architecture
- Pluggable AI service providers
- Unified cost estimation across providers
- Provider-specific validation and requirements
- Browser-based (ChatGPT Web) vs API-based services

#### Security Features
- Automatic PII redaction (emails, phones, API keys)
- Secure credential storage in macOS keychain
- Accessibility permission handling
- No sensitive data in configuration files

## File Organization

### Entry Points
- `src/main.py`: PyQt6-based application entry
- `src/app.py`: Rumps-based application entry  
- `run_app.py`: Wrapper script for proper Python path

### Core Services
- `src/services.py`: AI service provider abstraction
- `src/api_client.py`: OpenAI API communication
- `src/prompt_optimizer.py`: Prompt enhancement logic
- `src/redaction.py`: Sensitive data removal

### Data Layer
- `src/storage.py`: Configuration persistence
- `src/settings_manager.py`: Settings with keyring integration
- `src/history_manager.py`: Prompt history management
- `src/pricing.py`: Service cost configurations

### UI Layer
- `src/menubar.py`: Legacy menubar implementation
- `src/input_dialog.py`: Main input interface
- `src/settings_dialog.py`: Configuration interface
- `src/ui_*.py`: Specialized UI components

### Build System
- `setup.py`: py2app configuration for macOS packaging
- `build_app.sh`: Complete build automation script
- `create_dmg.sh`: DMG installer creation

### Resources
- `resources/icons/`: Application icons
- `resources/localization/`: Multi-language JSON files

## Development Notes

### Keyboard Shortcut Implementation
The app uses a complex keyboard shortcut system due to macOS security requirements:
- Requires accessibility permissions
- Uses notification-based triggers to open dialogs
- Separate thread management for shortcut handlers

### AI Service Integration
- **ChatGPT Web**: Browser-based, no API key required
- **OpenAI/Anthropic**: API-based with streaming responses
- **Ollama**: Local model support with daemon validation

### Testing Strategy
- Limited test coverage in `tests/` directory
- Focus on redaction and localization functionality
- No comprehensive test framework configuration

### Localization System
- JSON-based translation files in `resources/localization/`
- Hierarchical key structure (e.g., `menubar.open_input`)
- Fallback to English for missing translations