import AppKit
import SwiftUI

final class HistoryWindowController: NSWindowController {
    static let shared = HistoryWindowController()
    private init() {
        let view = HistoryView()
        let hosting = NSHostingView(rootView: view)
        let window = NSWindow(contentRect: NSRect(x: 0, y: 0, width: 800, height: 500),
                              styleMask: [.titled, .closable, .resizable],
                              backing: .buffered,
                              defer: false)
        window.isReleasedWhenClosed = false
        window.title = "Prompt History"
        window.center()
        window.contentView = hosting
        super.init(window: window)
    }

    required init?(coder: NSCoder) { fatalError("init(coder:) has not been implemented") }

    func open() { window?.makeKeyAndOrderFront(nil); NSApp.activate(ignoringOtherApps: true) }
}

private struct HistoryEntryViewModel: Identifiable {
    let id: Int64
    let date: Date
    let input: String
    let service: AIService
}

private struct HistoryView: View {
    @State private var entries: [HistoryEntryViewModel] = []
    @State private var selected: HistoryEntryViewModel?
    @State private var preview: String = ""

    var body: some View {
        VStack(spacing: 0) {
            HStack {
                Text("Prompt History").font(.headline)
                Spacer()
                Button("Clear All") { Task { await HistoryStore.shared.clear(); await load() } }
            }.padding(.horizontal).padding(.top, 12)
            Divider()
            HStack(spacing: 0) {
                Table(entries, selection: Binding(get: { selected?.id }, set: { newId in
                    selected = entries.first(where: { $0.id == newId })
                    Task { await updatePreview() }
                })) {
                    TableColumn("Date") { e in Text(e.date.formatted(date: .abbreviated, time: .shortened)) }
                    TableColumn("Prompt") { e in Text(e.input).lineLimit(1) }
                    TableColumn("AI Service") { e in Text(e.service.rawValue.capitalized) }
                }
                .frame(minWidth: 350)
                Divider()
                VStack(alignment: .leading) {
                    Text("Preview:").font(.subheadline).bold()
                    ScrollView { Text(preview).frame(maxWidth: .infinity, alignment: .leading) }
                    HStack {
                        Button("Reuse Prompt") {
                            if let s = selected { InputWindowController.shared.open(prefill: s.input) }
                        }
                        Button("Delete") {
                            Task { if let s = selected { await HistoryStore.shared.delete(id: s.id); await load() } }
                        }
                        Spacer()
                        Button("Close") { NSApp.keyWindow?.close() }
                    }
                }.padding().frame(maxWidth: .infinity, maxHeight: .infinity)
            }.frame(minHeight: 380)
        }
        .onAppear { Task { await load() } }
    }

    private func load() async {
        let rows = await HistoryStore.shared.fetch(limit: 200)
        entries = rows.map { .init(id: $0.id, date: Date(timeIntervalSince1970: TimeInterval($0.timestamp)), input: $0.inputText, service: $0.aiService) }
        selected = nil
        preview = ""
    }

    private func updatePreview() async {
        if let s = selected, let entry = await HistoryStore.shared.get(id: s.id) {
            preview = entry.inputText
        } else { preview = "" }
    }
}


