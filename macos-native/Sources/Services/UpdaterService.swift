import Foundation
import Sparkle

final class UpdaterService: NSObject, SPUUpdaterDelegate {
    static let shared = UpdaterService()
    private override init() {}

    private var updaterController: SPUStandardUpdaterController?

    func start() {
        updaterController = SPUStandardUpdaterController(startingUpdater: true, updaterDelegate: self, userDriverDelegate: nil)
    }
}


