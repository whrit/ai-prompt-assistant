# src/ui_menus.py
from AppKit import NSApp, NSMenu, NSMenuItem


def ensure_edit_menu():
    """Ensure the app has a minimal main menu with standard Edit actions.

    This enables ⌘C/⌘V/⌘X/⌘A and other first-responder actions to work
    even for status bar apps without a traditional menu bar.
    """
    app = NSApp()
    if not app:
        return
    menu = app.mainMenu()
    if menu is not None:
        # If an Edit menu already exists, do nothing
        for item in menu.itemArray() or []:
            if item.title() == "Edit":
                return
    # Create minimal main menu with an Edit submenu
    main_menu = NSMenu.alloc().initWithTitle_("Main")

    # Add Edit menu
    edit_menu_item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Edit", None, "")
    main_menu.addItem_(edit_menu_item)

    edit_menu = NSMenu.alloc().initWithTitle_("Edit")
    def _add(title, selector, key=""):
        item = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, selector, key)
        edit_menu.addItem_(item)

    # Standard first-responder actions route to the current key view
    _add("Undo", "undo:", "z")
    _add("Redo", "redo:", "Z")
    edit_menu.addItem_(NSMenuItem.separatorItem())
    _add("Cut", "cut:", "x")
    _add("Copy", "copy:", "c")
    _add("Paste", "paste:", "v")
    _add("Select All", "selectAll:", "a")

    main_menu.setSubmenu_forItem_(edit_menu, edit_menu_item)
    app.setMainMenu_(main_menu)


