from typing import TYPE_CHECKING
from logging import info
from .findskel import FindSkel
from .main import Main, flag
from . import add_file, get_linker, link_duplicates, list_uniques

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from typing import Sequence, Union


def filesizef(s):
    # type: (Union[int, float]) -> str
    if not s and s != 0:
        return "-"
    for x in "bkMGTPEZY":
        if s < 1000:
            break
        s /= 1024.0
    return ("%.1f" % s).rstrip("0").rstrip(".") + x


class Counter(object):
    def __getattr__(self, name):
        return self.__dict__.setdefault(name, 0)

    def __contains__(self, name):
        return name in self.__dict__

    def __iter__(self):
        return iter(self.__dict__)

    def __getitem__(self, name):
        return self.__dict__.setdefault(name, 0)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __str__(self):
        return " ".join(
            sorted(self._format_entry(k, v) for (k, v) in self.__dict__.items())
        )

    def _format_entry(self, key, value):
        return str(key) + " " + self._format_value(value, key) + ";"

    def _format_value(self, value, key):
        # type: (object, str) -> str
        if key in ("size", "disk_size"):
            return filesizef(value)
        return str(value)


class Stat(FindSkel):
    carry_on: bool = flag("carry-on", "Continue on file errors", default=False)

    def __init__(self) -> None:
        super().__init__()
        self._glob_includes = []
        self._glob_excludes = []
        self._dir_depth = ()
        self._file_sizes = []
        self._paths_from = []
        self._paths = []
        self.total = Counter()
        self.db = dict()

    def ready(self):
        from logging import basicConfig
        from os import environ

        format = environ.get("LOG_FORMAT", "%(levelname)s: %(message)s")
        level = environ.get("LOG_LEVEL", "INFO")
        basicConfig(format=format, level=level)

        #####
        def accept(e, **kwargs):
            # print(e.path)
            return e.is_file()

        self.on_check_accept(accept)
        #####
        return super().ready()

    def run(self, db: dict, total: object):
        link_duplicates(db, None, total, self.carry_on)

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"Stats about linked files under given directory"
        return super().init_argparse(argp)

    def start(self):
        self._walk_paths()
        try:
            self.run(self.db, self.total)
        finally:
            self.total and info("Total {}".format(self.total))

    def process_entry(self, de):
        st = de.stat()
        # print(de.path)
        add_file(self.db, de.path, st.st_size, st.st_ino, st.st_dev, st.st_mtime)


class Link(Stat):
    linker: str = flag(
        "The linker to use",
        choices=("os.link", "ln", "lns", "os.symlink"),
        default="os.link",
    )

    def run(self, db: dict, total: object):
        link_duplicates(db, get_linker(self.linker), total, self.carry_on)

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"Link files under given directory"
        return super().init_argparse(argp)


class Uniques(Stat):

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"List unique files under given directory"
        return super().init_argparse(argp)

    def run(self, db: dict, total: object):
        # print("Uniques:run")
        list_uniques(db, total, print)


class Duplicates(Stat):
    human_sizes: bool = flag("human", "human readable file sizes", default=False)

    def init_argparse(self, argp: "ArgumentParser"):
        argp.description = r"List duplicates files under given directory"
        return super().init_argparse(argp)

    def run(self, db: dict, total: object):
        from . import list_duplicates

        if self.human_sizes:
            _size_f = filesizef
        else:
            _size_f = str

        def found(ino: int = 0, size: int = 0, dev: int = 0, paths: list[str] = []):
            n = len(paths)
            print(f"iNode:{ino} Links:{n} Size:{_size_f(size)}")
            for p in paths:
                print(f" - {p}")

        list_duplicates(db, total, found=found)


class App(Main):

    def add_arguments(self, argp: "ArgumentParser"):
        argp.prog = f"python -m {__package__}"
        argp.description = r"This command-line application scans a specified directory for duplicate files and replaces duplicates with hard links to a single copy of the file. By doing so, it conserves storage space while preserving the file structure and accessibility."
        return super().add_arguments(argp)

    def sub_args(self):
        yield Stat(), {"name": "stat"}
        yield Link(), {"name": "link"}
        yield Uniques(), {"name": "uniques"}
        yield Duplicates(), {"name": "duplicates"}


def main():
    App().main()


(__name__ == "__main__") and main()
