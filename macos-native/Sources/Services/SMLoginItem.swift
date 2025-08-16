import ServiceManagement

enum SMLoginItem {
    private static let identifier = "co.raspiska.aipromptassistant.LoginItem"

    static var isEnabled: Bool {
        (try? SMAppService.mainApp.status) == .enabled
    }

    @discardableResult
    static func setEnabled(_ enabled: Bool) -> Bool {
        do {
            if enabled {
                try SMAppService.mainApp.register()
            } else {
                try SMAppService.mainApp.unregister()
            }
            return true
        } catch {
            return false
        }
    }
}


