import Foundation

struct HistoryRow: Codable, Equatable {
    let id: Int64
    let inputText: String
    let rephrasedText: String?
    let aiService: AIService
    let timestamp: Int64
}

final class HistoryStore {
    static let shared = HistoryStore()
    private init() { try? FileManager.default.createDirectory(at: folder, withIntermediateDirectories: true) }

    private let folder: URL = {
        let base = FileManager.default.urls(for: .applicationSupportDirectory, in: .userDomainMask)[0]
            .appendingPathComponent("AI Prompt Assistant", isDirectory: true)
            .appendingPathComponent("history", isDirectory: true)
        return base
    }()
    private var dbURL: URL { folder.appendingPathComponent("input_history.json") }

    private func readAll() -> [HistoryRow] {
        guard let data = try? Data(contentsOf: dbURL) else { return [] }
        return (try? JSONDecoder().decode([HistoryRow].self, from: data)) ?? []
    }

    private func writeAll(_ rows: [HistoryRow]) {
        if let data = try? JSONEncoder().encode(rows) {
            try? data.write(to: dbURL, options: [.atomic])
        }
    }

    func fetch(limit: Int = 50) async -> [HistoryRow] {
        let rows = readAll().sorted(by: { $0.timestamp > $1.timestamp })
        return Array(rows.prefix(limit))
    }

    func get(id: Int64) async -> HistoryRow? {
        readAll().first(where: { $0.id == id })
    }

    func add(input: String, rephrased: String?, service: AIService) async {
        var rows = readAll()
        let id = (rows.map(\.id).max() ?? 0) + 1
        let ts = Int64(Date().timeIntervalSince1970)
        rows.append(.init(id: id, inputText: input, rephrasedText: rephrased, aiService: service, timestamp: ts))
        writeAll(rows)
    }

    func delete(id: Int64) async {
        var rows = readAll()
        rows.removeAll { $0.id == id }
        writeAll(rows)
    }

    func clear() async { writeAll([]) }
}


