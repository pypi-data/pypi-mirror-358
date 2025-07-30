import win32con
import win32gui
from pathlib import Path
from watchdog.observers import Observer  # type: ignore
from watchdog.events import FileSystemEventHandler

from .win_tray import SystemTrayIcon, Win32Window


class IconFileEventHandler(FileSystemEventHandler):
    """Watches for modifications to the icon file and triggers an update."""

    def __init__(self, icon_path: Path, update_callback):
        super().__init__()
        self._icon_path_str = str(icon_path.resolve())
        self._update_callback = update_callback

    def on_modified(self, event):
        if not event.is_directory and event.src_path == self._icon_path_str:
            print(f"Icon file changed: {event.src_path}. Updating tray icon.")
            self._update_callback()


class MainWindow:
    """
    The main application class that coordinates the tray icon,
    window, and file watchers.
    """

    def __init__(self, icon_path: Path, krita_handler: Observer):
        self.icon_path = icon_path
        self.krita_watcher = krita_handler
        self.tooltip = "Krita Tray Icon"

        # Setup window message handlers
        msg_TaskbarRestart = win32gui.RegisterWindowMessage("TaskbarCreated")
        message_map = {
            msg_TaskbarRestart: self.on_restart,
            win32con.WM_DESTROY: self.on_destroy,
            win32con.WM_COMMAND: self.on_command,
            win32con.WM_USER + 20: self.on_taskbar_notify,
        }

        # Create a unique window class for each instance to support multiple icons
        class_name = f"KritaTrayIconWindowClass_{id(self)}"
        window_name = f"Krita Tray Icon - {self.icon_path.name}"
        self._window = Win32Window(class_name, window_name, message_map)
        self._tray_icon = SystemTrayIcon(self._window.hwnd, self.icon_path, self.tooltip)

        # Setup the observer for the .ico file itself to update the tray icon
        self.observer = Observer()
        event_handler = IconFileEventHandler(
            self.icon_path, self._tray_icon.update_icon
        )
        self.observer.schedule(
            event_handler, str(self.icon_path.parent.resolve()), recursive=False
        )

        # Setup the context menu
        self.menu = self._create_menu()

    def _create_menu(self):
        """Creates the right-click context menu for the tray icon."""
        menu = win32gui.CreatePopupMenu()
        self.menu_item_exit_id = 1024  # Unique ID for the "Exit" item

        win32gui.AppendMenu(
            menu, win32con.MF_STRING, self.menu_item_exit_id, "Exit"
        )
        return menu

    def show_menu(self):
        """Displays the context menu at the current cursor position."""
        pos = win32gui.GetCursorPos()
        win32gui.SetForegroundWindow(self._window.hwnd)
        win32gui.TrackPopupMenu(
            self.menu,
            win32con.TPM_LEFTALIGN,
            pos[0],
            pos[1],
            0,
            self._window.hwnd,
            None,
        )
        win32gui.PostMessage(self._window.hwnd, win32con.WM_NULL, 0, 0)

    def on_restart(self, hwnd, msg, wparam, lparam):
        """Handles the TaskbarCreated message, sent when explorer.exe restarts."""
        self._tray_icon.add_icon()
        return 0

    def on_destroy(self, hwnd, msg, wparam, lparam):
        """Handles the WM_DESTROY message to clean up resources."""
        self._tray_icon.remove_icon()
        return 0

    def on_taskbar_notify(self, hwnd, msg, wparam, lparam):
        """Handles mouse events on the tray icon."""
        if lparam == win32con.WM_RBUTTONUP:
            self.show_menu()
        return True

    def on_command(self, hwnd, msg, wparam, lparam):
        """Handles commands from the context menu."""
        item_id = win32gui.LOWORD(wparam)
        if item_id == self.menu_item_exit_id:
            print("Exit command received, shutting down application.")
            win32gui.PostQuitMessage(0)
        return 0

    def shutdown(self):
        """Stops this instance's file watcher and destroys its window."""
        self.observer.stop()
        self.observer.join()
        win32gui.DestroyWindow(self._window.hwnd)

    def run(self):
        """Prepares the window for running by adding the icon to the tray."""
        self._tray_icon.add_icon()
