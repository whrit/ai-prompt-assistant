import AppKit
import SwiftUI

final class InputWindowController: NSWindowController, NSWindowDelegate {
    static let shared = InputWindowController()
    private init() {
        let view = InputView()
        let hosting = NSHostingView(rootView: view)
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 520, height: 240),
                              styleMask: [.titled, .closable],
                              backing: .buffered,
                              defer: false)
        window.isReleasedWhenClosed = false
        window.title = "AI Prompt Assistant"
        window.center()
        window.contentView = hosting
        super.init(window: window)
        self.window?.delegate = self
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    func open(prefill: String? = nil) {
        if let prefill { NotificationCenter.default.post(name: .prefillInput, object: prefill) }
        window?.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }
}

private struct InputView: View {
    @State private var text: String = ""
    @State private var charCount: Int = 0
    @State private var wordCount: Int = 0

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            HStack {
                Text("Enter your prompt").font(.headline)
                Spacer()
                Button(action: { NSApp.keyWindow?.close() }) { Image(systemName: "xmark") }
                    .buttonStyle(.borderless)
            }
            TextEditor(text: $text)
                .font(.system(size: 14))
                .frame(minHeight: 120)
                .onChange(of: text) { _ in
                    charCount = text.count
                    wordCount = text.split(whereSeparator: { $0.isWhitespace }).count
                }
            HStack {
                Spacer()
                Text("\(charCount) characters | \(wordCount) words").foregroundStyle(.secondary)
            }
            HStack {
                Spacer()
                Button("Ask") {
                    Task { await handleSubmit() }
                }.keyboardShortcut(.return, modifiers: [])
            }
        }
        .padding(16)
        .onReceive(NotificationCenter.default.publisher(for: .prefillInput)) { note in
            if let s = note.object as? String { text = s }
        }
    }

    private func handleSubmit() async {
        let trimmed = text.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { return }
        let prefixed = trimmed.lowercased().hasPrefix("how to") ? trimmed : "how to \(trimmed)"
        let rephrased = await AIClient.shared.rephrase(prefixed)
        await HistoryStore.shared.add(input: trimmed, rephrased: rephrased, service: AppState.shared.settings.aiService)
        AIClient.shared.openInPreferredService(rephrased)
        NSApp.keyWindow?.close()
    }
}

extension Notification.Name { static let prefillInput = Notification.Name("prefillInput") }


