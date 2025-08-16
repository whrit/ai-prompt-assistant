import Foundation
import Carbon

final class HotKeyManager {
    private var hotKeyRef: EventHotKeyRef?
    private var handlerRef: EventHandlerRef?

    func registerDefault() {
        // Default ⌃⌘D
        register(keyCode: UInt32(kVK_ANSI_D), modifiers: UInt32(cmdKey | controlKey))
    }

    func register(keyCode: UInt32, modifiers: UInt32) {
        var eventSpec = EventTypeSpec(eventClass: OSType(kEventClassKeyboard), eventKind: UInt32(kEventHotKeyPressed))
        InstallEventHandler(GetApplicationEventTarget(), hotKeyEventHandler, 1, &eventSpec, nil, &handlerRef)

        var hotKeyID = EventHotKeyID(signature: OSType(0x41495041), id: 1)
        RegisterEventHotKey(keyCode, modifiers, hotKeyID, GetApplicationEventTarget(), 0, &hotKeyRef)
    }
}

private func hotKeyEventHandler(_ nextHandler: EventHandlerCallRef?, _ theEvent: EventRef?, _ userData: UnsafeMutableRawPointer?) -> OSStatus {
    InputWindowController.shared.open()
    return noErr
}


