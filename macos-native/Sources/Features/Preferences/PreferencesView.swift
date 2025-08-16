import SwiftUI

struct PreferencesView: View {
    @ObservedObject private var state = AppState.shared

    var body: some View {
        TabView {
            GeneralTab()
                .tabItem { Label("General", systemImage: "gearshape") }
            AITab()
                .tabItem { Label("AI", systemImage: "brain") }
            LanguageTab()
                .tabItem { Label("Language", systemImage: "globe") }
        }
        .padding(20)
        .frame(width: 520, height: 380)
    }
}

private struct GeneralTab: View {
    @ObservedObject private var state = AppState.shared
    @State private var launchAtLogin = SMLoginItem.isEnabled

    var body: some View {
        Form {
            LabeledContent("Keyboard Shortcut") {
                TextField("⌃⌘D", text: Binding(
                    get: { state.settings.keyboardShortcut },
                    set: { state.settings.keyboardShortcut = $0; AppState.shared.save() }
                ))
                .textFieldStyle(.roundedBorder)
                .frame(width: 140)
            }

            Toggle("Launch at Login", isOn: Binding(
                get: { state.settings.launchAtLogin },
                set: {
                    state.settings.launchAtLogin = $0
                    _ = SMLoginItem.setEnabled($0)
                    AppState.shared.save()
                }
            ))
        }
        .padding()
    }
}

private struct AITab: View {
    @ObservedObject private var state = AppState.shared
    @State private var apiKey: String = Keychain.shared.openAIKey ?? ""

    var body: some View {
        Form {
            Picker("AI Service", selection: Binding(
                get: { state.settings.aiService },
                set: { state.settings.aiService = $0; AppState.shared.save() }
            )) {
                Text("ChatGPT").tag(AIService.chatgpt)
                Text("Google Bard").tag(AIService.bard)
                Text("Claude").tag(AIService.claude)
            }

            SecureField("OpenAI API Key", text: $apiKey)
                .textFieldStyle(.roundedBorder)

            HStack {
                Button("Save Key") {
                    Keychain.shared.openAIKey = apiKey
                }
                Button("Test Key") {
                    Task { await AIClient.shared.testKey() }
                }
            }
        }
        .padding()
        .onAppear { apiKey = Keychain.shared.openAIKey ?? "" }
    }
}

private struct LanguageTab: View {
    @ObservedObject private var state = AppState.shared
    var body: some View {
        Form {
            Picker("Language", selection: Binding(
                get: { state.settings.language },
                set: { state.settings.language = $0; AppState.shared.save() }
            )) {
                ForEach(Language.allCases, id: \.self) { lang in
                    Text(lang.displayName).tag(lang)
                }
            }
        }.padding()
    }
}

struct PreferencesView_Previews: PreviewProvider {
    static var previews: some View {
        PreferencesView()
    }
}


