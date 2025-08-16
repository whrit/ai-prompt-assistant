import Foundation

final class SettingsStore {
    static let shared = SettingsStore()
    private init() {}

    private let userDefaultsKey = "co.raspiska.aipromptassistant.settings"

    func load() -> SettingsModel {
        if let data = UserDefaults.standard.data(forKey: userDefaultsKey),
           let decoded = try? JSONDecoder().decode(SettingsModel.self, from: data) {
            return decoded
        }
        return SettingsModel()
    }

    func save(_ settings: SettingsModel) {
        if let data = try? JSONEncoder().encode(settings) {
            UserDefaults.standard.set(data, forKey: userDefaultsKey)
        }
    }
}


