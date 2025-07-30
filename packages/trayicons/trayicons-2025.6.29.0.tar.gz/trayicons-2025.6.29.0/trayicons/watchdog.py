import io
import zipfile
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from PIL import Image


def convert_to_ico(krita_filepath: str | Path, output_file: Path):
    """
    Converts a Krita image to an ICO file using pure Python libraries.

    It works by extracting 'mergedimage.png' from the .kra (zip) file
    and converting it to an .ico file in memory.
    """
    try:
        # KRA files are zip archives. We extract the preview image.
        with zipfile.ZipFile(krita_filepath, "r") as kra_zip:
            if "mergedimage.png" not in kra_zip.namelist():
                print(f"Error: 'mergedimage.png' not found in '{krita_filepath}'.")
                return

            png_data = kra_zip.read("mergedimage.png")

        # Convert the PNG data (in memory) to an ICO file
        with io.BytesIO(png_data) as png_stream:
            with Image.open(png_stream) as img:
                # You can specify different sizes for the ICO file
                icon_sizes = [
                    (16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (256, 256)
                ]
                img.save(output_file, format="ICO", sizes=icon_sizes)

    except FileNotFoundError:
        print(f"Error: Krita file not found at '{krita_filepath}'")
    except zipfile.BadZipFile:
        print(f"Error: '{krita_filepath}' is not a valid Krita (zip) file.")
    except Exception as e:
        print(f"An unexpected error occurred during conversion of '{krita_filepath}': {e}")


class KritaEventHandler(FileSystemEventHandler):
    """Dispatches file modification events to the correct conversion function."""

    def __init__(self):
        super().__init__()
        # A map from full source path (str) to destination path (Path)
        self.watched_files: dict[str, Path] = {}

    def add_watch(self, src_path: Path, dst_path: Path):
        """Adds a file to watch."""
        self.watched_files[str(src_path.resolve())] = dst_path

    def on_modified(self, event):
        if event.is_directory:
            return

        # Check if the modified file is one we are watching
        if event.src_path in self.watched_files:
            print(f"Detected change in: {event.src_path}")
            output_file = self.watched_files[event.src_path]
            convert_to_ico(event.src_path, output_file)


class KritaFileWatcher:
    """
    Manages a single watchdog Observer to monitor multiple Krita source files
    for changes and trigger conversions.
    """

    def __init__(self):
        self._observer = Observer()
        self._event_handler = KritaEventHandler()
        self._watched_dirs = set()

    def add_watch(self, src_path: Path, dst_path: Path):
        """
        Adds a source Krita file to watch.

        It schedules the parent directory for watching if it's not already
        being monitored.
        """
        # Ensure the destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)

        self._event_handler.add_watch(src_path, dst_path)

        # Watch the parent directory, but only schedule one watch per directory
        watch_dir = src_path.parent
        if watch_dir not in self._watched_dirs:
            self._observer.schedule(self._event_handler, watch_dir, recursive=False)
            self._watched_dirs.add(watch_dir)
            print(f"Watching directory '{watch_dir}' for Krita file changes...")

    def start(self):
        """Starts the file observer."""
        self._observer.start()

    def stop(self):
        """Stops the file observer."""
        self._observer.stop()

    def join(self):
        """Waits until the observer thread terminates."""
        self._observer.join()
