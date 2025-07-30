import win32api
import win32con
from .tray_icons import MainWindow
from .watchdog import KritaFileWatcher, convert_to_ico
from .config import get_config_path, Config
import win32gui


def main():
    config_file = get_config_path()
    try:
        config_data = Config.from_toml(config_file)
    except ValueError as e:
        print(f"Error loading configuration: {e}")
        return

    if not config_data.icons:
        print("No icons configured in 'icons.toml'. Exiting.")
        return

    # A single watcher for all Krita source files.
    krita_watcher = KritaFileWatcher()

    for config in config_data.icons:
        src = config.src
        dst = config.dst
        if not dst.exists():
            convert_to_ico(src, dst)
        krita_watcher.add_watch(src, dst)

    # --- Application Setup ---
    tray_windows = []
    for config in config_data.icons:
        tray_window = MainWindow(icon_path=config.dst, krita_handler=krita_watcher)
        print(f"Preparing icon '{config.dst}'...")
        tray_window.observer.start()
        tray_windows.append(tray_window)

    # Start the shared watcher for Krita files
    krita_watcher.start()

    # Add all icons to the system tray
    for tray_window in tray_windows:
        tray_window.run()

    # --- Main Message Loop ---
    # Get the current thread ID for the signal handler
    main_thread_id = win32api.GetCurrentThreadId()

    def console_handler(ctrl_type):
        """A handler for console control events (like Ctrl+C)."""
        if ctrl_type == win32con.CTRL_C_EVENT:
            print("\nCtrl+C detected. Requesting application shutdown...")
            win32gui.PostThreadMessage(main_thread_id, win32con.WM_QUIT, 0, 0)
            return True  # We've handled the event
        return False # Pass other signals to the next handler

    # Register the console control handler.
    win32api.SetConsoleCtrlHandler(console_handler, True)

    print("Application started. Press Ctrl+C or use the tray icon's Exit menu to quit.")

    # The main message loop. This blocks until a WM_QUIT message is received.
    # WM_QUIT can be posted by the tray icon's "Exit" menu or by our Ctrl+C handler.
    win32gui.PumpMessages()

    # --- Shutdown ---
    # This code runs after PumpMessages() returns.
    print("Application quitting. Cleaning up all resources...")
    krita_watcher.stop()
    krita_watcher.join()
    for tray_window in tray_windows:
        tray_window.shutdown()

if __name__ == "__main__":
    main()
