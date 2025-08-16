import Foundation

enum AIService: String, Codable, CaseIterable, Equatable {
    case chatgpt
    case bard
    case claude
}

enum Language: String, Codable, CaseIterable, Equatable {
    case en, es, de, sv, tr

    var displayName: String {
        switch self {
        case .en: return "English"
        case .es: return "Spanish"
        case .de: return "German"
        case .sv: return "Swedish"
        case .tr: return "Turkish"
        }
    }
}

struct SettingsModel: Codable, Equatable {
    var keyboardShortcut: String = "⌃⌘D"
    var aiService: AIService = .chatgpt
    var language: Language = .en
    var launchAtLogin: Bool = false
}


