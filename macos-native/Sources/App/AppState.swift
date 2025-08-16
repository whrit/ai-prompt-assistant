import Foundation

final class AppState: ObservableObject {
    static let shared = AppState()
    private init() {}

    @Published var settings = SettingsModel()

    func load() {
        settings = SettingsStore.shared.load()
    }

    func save() {
        SettingsStore.shared.save(settings)
    }
}


