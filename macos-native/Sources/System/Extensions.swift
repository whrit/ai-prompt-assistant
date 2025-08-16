import Foundation

extension Encodable {
    func jsonData() -> Data? { try? JSONEncoder().encode(self) }
}


