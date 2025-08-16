import Foundation
import AppKit

final class AIClient {
    static let shared = AIClient()
    private init() {}

    private var apiKey: String? { Keychain.shared.openAIKey }

    func testKey() async {
        guard let key = apiKey else { return }
        var req = URLRequest(url: URL(string: "https://api.openai.com/v1/models")!)
        req.httpMethod = "GET"
        req.addValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        _ = try? await URLSession.shared.data(for: req)
    }

    func rephrase(_ text: String) async -> String {
        guard let key = apiKey else { return text }
        var req = URLRequest(url: URL(string: "https://api.openai.com/v1/chat/completions")!)
        req.httpMethod = "POST"
        req.addValue("application/json", forHTTPHeaderField: "Content-Type")
        req.addValue("Bearer \(key)", forHTTPHeaderField: "Authorization")
        let body: [String: Any] = [
            "model": "gpt-3.5-turbo",
            "messages": [
                ["role": "system", "content": "You are a helpful assistant that rephrases 'how to' queries concisely. Only return the rephrased query."],
                ["role": "user", "content": "Rephrase this query to make it more effective: '\(text)'"]
            ],
            "temperature": 0.7,
            "max_tokens": 150
        ]
        req.httpBody = try? JSONSerialization.data(withJSONObject: body)
        do {
            let (data, _) = try await URLSession.shared.data(for: req)
            if let json = try JSONSerialization.jsonObject(with: data) as? [String: Any],
               let choices = json["choices"] as? [[String: Any]],
               let msg = choices.first?["message"] as? [String: Any],
               let content = msg["content"] as? String {
                return content.trimmingCharacters(in: .whitespacesAndNewlines)
            }
            return text
        } catch {
            return text
        }
    }

    func openInPreferredService(_ prompt: String) {
        let encoded = prompt.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? prompt
        let service = AppState.shared.settings.aiService
        let urlString: String
        switch service {
        case .chatgpt: urlString = "https://chat.openai.com/?prompt=\(encoded)"
        case .bard: urlString = "https://bard.google.com/?prompt=\(encoded)"
        case .claude: urlString = "https://claude.ai/chat?prompt=\(encoded)"
        }
        if let url = URL(string: urlString) { NSWorkspace.shared.open(url) }
    }
}


