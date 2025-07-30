"""TcEx Framework Module"""
# standard library
import gzip
import multiprocessing
import os
import queue
import shutil
import sys
import threading
import traceback
from logging.handlers import RotatingFileHandler


class RotatingFileHandlerCustom(RotatingFileHandler):
    """Logger handler for ThreatConnect Exchange File logging."""

    def __init__(
        self,
        filename: str,
        mode: str = 'a',
        maxBytes: int = 0,
        backupCount: int = 0,
        encoding: str | None = None,
        delay: bool = False,
    ):
        """Customize RotatingFileHandler to create full log path.

        Args:
            filename: The name of the logfile.
            mode: The write mode for the file.
            maxBytes: The max file size before rotating.
            backupCount: The maximum # of backup files.
            encoding: The log file encoding.
            delay: If True, then file opening is deferred until the first call to emit().
        """
        if encoding is None and os.getenv('LANG') is None:
            encoding = 'UTF-8'
        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename), exist_ok=True)
        RotatingFileHandler.__init__(self, filename, mode, maxBytes, backupCount, encoding, delay)

        self.queue = multiprocessing.Queue(-1)
        self.t = threading.Thread(target=self.receive, daemon=True)
        self.t.name = 'RotatingFileHandlerCustom'
        self.t.start()

        # set namer
        self.namer = self.custom_gzip_namer
        self.rotator = self.custom_gzip_rotator

    def receive(self):
        """."""
        while True:
            try:
                record = self.queue.get()
                print('From Queue', record.message)
                super().emit(record)
            except (KeyboardInterrupt, SystemExit):
                raise
            except EOFError:
                break
            except Exception:
                traceback.print_exc(file=sys.stderr)

    def send(self, record):
        """."""
        print('Send', record.message)
        self.queue.put(record)

    def emit(self, record):
        """."""
        try:
            print('Emit', record.message)
            self.send(record)
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.handleError(record)

    def flush(self):
        """."""
        print('flush')
        while not self.queue.empty():
            record = self.queue.get()
            super().emit(record)
        # self.receive()

        # self.queue.close()
        # self.queue.join_thread()
        print('after receive')
        # super().close()

    @staticmethod
    def custom_gzip_namer(name):
        """Namer for rotating log handler with gz extension.

        Args:
            name: The current name of the logfile.
        """
        return name + '.gz'

    @staticmethod
    def custom_gzip_rotator(source: str, dest: str):
        """Rotate and compress log file.

        Args:
            source: The source filename.
            dest: The destination filename.
        """
        with open(source, 'rb') as f_in:
            with gzip.open(dest, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        os.remove(source)
