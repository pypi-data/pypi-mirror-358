import time
import win32api
import win32con
import win32gui
import winerror
from pathlib import Path


class SystemTrayIcon:
    """
    Manages a system tray icon using the Win32 API.
    It handles adding, updating, and removing the icon.
    """

    def __init__(self, hwnd, icon_path: Path, tooltip: str):
        self.hwnd = hwnd
        self.icon_path = icon_path
        self.tooltip = tooltip
        self._hicon = None

    def _load_icon(self):
        """
        Loads the icon from its path, with retries for file locks.
        Returns an icon handle (hicon) or None on failure.
        """
        hinst = win32api.GetModuleHandle(None)
        icon_path_str = str(self.icon_path.resolve())

        if not self.icon_path.is_file():
            print(f"Error: Icon file not found at '{icon_path_str}'")
            return None

        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE

        # Retry a few times to handle file access issues (e.g., file being written)
        for i in range(5):
            try:
                hicon = win32gui.LoadImage(
                    hinst, icon_path_str, win32con.IMAGE_ICON, 0, 0, icon_flags
                )
                return hicon
            except win32gui.error as e:
                print(f"Warning: Could not load icon (attempt {i+1}/5). Retrying... Error: {e}")
                time.sleep(0.2)

        print(f"Error: Failed to load icon from '{icon_path_str}' after multiple retries.")
        return None

    def add_icon(self):
        """Adds the icon to the system tray."""
        self._hicon = self._load_icon()
        if not self._hicon:
            return

        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, self._hicon, self.tooltip)
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        except win32gui.error as e:
            print(f"Failed to add tray icon: {e}")

    def update_icon(self):
        """Updates the existing tray icon with the image from the file."""
        new_hicon = self._load_icon()
        if not new_hicon:
            return

        flags = win32gui.NIF_ICON
        nid = (self.hwnd, 0, flags, 0, new_hicon, "")  # Only need to update the icon
        try:
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)
            # If successful, destroy the old icon and store the new one
            if self._hicon:
                win32gui.DestroyIcon(self._hicon)
            self._hicon = new_hicon
        except win32gui.error as e:
            print(f"Failed to update tray icon: {e}")
            win32gui.DestroyIcon(new_hicon)  # Clean up the newly loaded icon

    def remove_icon(self):
        """Removes the icon from the system tray."""
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        if self._hicon:
            win32gui.DestroyIcon(self._hicon)
            self._hicon = None


class Win32Window:
    """A basic, hidden Win32 window class required for hosting a tray icon."""

    def __init__(self, class_name: str, window_name: str, message_map: dict):
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = class_name
        wc.lpfnWndProc = message_map
        try:
            win32gui.RegisterClass(wc)
        except win32gui.error as err_info:
            if err_info.winerror != winerror.ERROR_CLASS_ALREADY_EXISTS:
                raise

        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(class_name, window_name, style, 0, 0,
            win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, 0, 0, hinst, None)