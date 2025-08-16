import SwiftUI

@main
struct AIPromptAssistantApp: App {
    @NSApplicationDelegateAdaptor(AppDelegate.self) var appDelegate

    var body: some Scene {
        MenuBarExtra("AI Prompt Assistant", systemImage: "sparkles") {
            Button("Open Input…") { InputWindowController.shared.open() }
            Button("History") { HistoryWindowController.shared.open() }
            Divider()
            Button("Preferences…") { NSApp.sendAction(#selector(NSApplication.showPreferencesWindow(_:)), to: nil, from: nil) }
            Divider()
            Button("Quit", role: .quit) {}
        }
        Settings {
            PreferencesView()
        }
        .commands {
            CommandGroup(after: .appSettings) {
                Button("Preferences…") {
                    NSApp.sendAction(#selector(NSApplication.showPreferencesWindow(_:)), to: nil, from: nil)
                }.keyboardShortcut(",", modifiers: .command)
            }
        }
    }
}

final class AppDelegate: NSObject, NSApplicationDelegate {
    private let hotKeyManager = HotKeyManager()

    func applicationDidFinishLaunching(_ notification: Notification) {
        AppState.shared.load()
        UpdaterService.shared.start()
        hotKeyManager.registerDefault()
    }
}


