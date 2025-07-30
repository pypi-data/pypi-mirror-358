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
    # This will block until a WM_QUIT message is received (e.g., from PostQuitMessage)
    win32gui.PumpMessages()

    # --- Shutdown ---
    print("Application quitting. Cleaning up all resources...")
    krita_watcher.stop()
    krita_watcher.join()
    for tray_window in tray_windows:
        tray_window.shutdown()

if __name__ == "__main__":
    main()
