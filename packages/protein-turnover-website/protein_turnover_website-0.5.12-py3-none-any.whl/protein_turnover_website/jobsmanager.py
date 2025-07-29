from __future__ import annotations

import os
import random
import shutil
import signal
import string
import sys
from datetime import datetime
from os import walk
from pathlib import Path
from typing import Iterator
from typing import NamedTuple
from typing import Sequence
from typing import TypedDict
from uuid import uuid4

from flask import abort
from flask import current_app
from protein_turnover.exts import RESULT_EXT
from protein_turnover.jobs import slugify
from protein_turnover.jobs import TurnoverJob


class Locator:
    """Given a dataid and a root jobsdir locate all files for this dataid"""

    def __init__(self, jobid: str, manager: JobsManager, dir_index: int):
        self.jobid = jobid
        self.manager = manager
        self.dir_index = dir_index

    def stem(self) -> str:
        return self.manager.stem(self.jobid)

    def locate_data_file(self) -> Path:
        # *** important function! ***
        # given a dataid find the sqlite file
        return self.locate_directory().joinpath(f"{self.stem()}{RESULT_EXT}")

    def locate_log_file(self) -> Path:
        return self.locate_directory().joinpath(f"{self.stem()}.log")

    def locate_config_file(self) -> Path:
        return self.locate_directory().joinpath(f"{self.stem()}.toml")

    def locate_pid_file(self) -> Path:
        return self.locate_directory().joinpath(f"{self.stem()}.toml.pid")

    def locate_all_files(self) -> list[Path]:
        return [
            self.locate_pid_file(),
            self.locate_config_file(),
            self.locate_data_file(),
            self.locate_log_file(),
        ]

    def locate_directory(self) -> Path:
        return self.manager.locate_directory(self.jobid, self.dir_index)

    def is_in_use(self) -> bool:
        return self.locate_directory().exists()

    def kill_pid(self) -> str | None:
        pidfile = self.locate_pid_file()
        if not pidfile.exists():
            return f"job {self.jobid} not running"

        try:
            with pidfile.open() as fp:
                pid = int(fp.read())
            os.kill(pid, signal.SIGINT)
        except (TypeError, OSError):
            return f"no such job: {self.jobid}"
        return None

    def remove(self) -> bool:
        directory = self.locate_directory()
        if not directory.exists():
            return False
        shutil.rmtree(directory)
        return True

    def remove_all_files(self) -> None:
        for f in self.locate_all_files():
            try:
                f.unlink(missing_ok=True)
            except OSError:
                pass


def check_path(dataid: str, root: Path) -> tuple[Path, bool]:
    """dataid is from the web, root is from us (so trusted)"""

    dataid = dataid + ".toml"
    if ".." in dataid:
        return Path(dataid), False
    jobfile = Path(dataid)
    if jobfile.is_absolute():
        return jobfile, False
    jobfile = (root / jobfile).resolve()
    if not jobfile.relative_to(root):
        return jobfile, False

    return jobfile, True


IS_WIN = sys.platform == "win32"


def url_to_path(dataid: str) -> str:
    # if IS_WIN:
    #     return dataid.replace("/", "\\")
    return dataid


def path_to_url(path: str) -> str:
    if IS_WIN:
        return path.replace("\\", "/")
    return path


class SimpleLocator(Locator):
    def __init__(self, jobid: str, manager: JobsManager, dir_index: int):
        """dataid is an encoded file path from the web (so untrustworth!)"""

        # dataid = url_to_path(dataid)
        jobfile, ok = check_path(jobid, manager.jobsdir_list[dir_index])
        if not ok:
            self.bad_file(jobfile)
        if jobfile.exists():
            job = TurnoverJob.restore(jobfile)
            jobid = job.jobid

        super().__init__(jobid, manager, dir_index)
        self.jobfile = jobfile

    def bad_file(self, jobfile: Path) -> None:
        current_app.logger.error("bad dataid: %s", jobfile)
        abort(404)

    def locate_directory(self) -> Path:
        return self.jobfile.parent

    def locate_config_file(self) -> Path:
        return self.jobfile

    def is_in_use(self) -> bool:
        return self.jobfile.exists()

    def remove(self) -> bool:
        self.remove_all_files()
        return True


class TurnoverJobFiles(NamedTuple):
    # found a job file i.e. a recognised
    # .toml file with a dataid .etc
    # NB: note that dataid is used to by the website to
    # map data to files using => dataid  =>  dataid[:2]/dataid/ datadir
    # see Locator
    job: TurnoverJob
    directory: Path
    name: str  # filename of jobfile
    full_path: str
    mtime: datetime
    size: int | None = None
    is_running: bool = False
    has_result: bool = False
    dir_index: int = 0

    @property
    def status(self) -> str:
        if self.is_running:
            return "running"
        return self.job.status or "stopped"

    @property
    def dataid(self) -> str:
        return f"{self.dir_index}---{self.job.jobid}"


class PersonalJobFiles(TurnoverJobFiles):
    @property
    def dataid(self) -> str:
        """Use full path as dataid"""
        path = path_to_url(self.full_path)
        return f"{self.dir_index}---{path}"


class Jobs(TypedDict):
    running: list[TurnoverJobFiles]
    queued: list[TurnoverJobFiles]
    finished: list[TurnoverJobFiles]


class Finder:
    TurnoverJobFilesClass: type[TurnoverJobFiles] = TurnoverJobFiles

    def _data_from_jobfile(
        self,
        jobfile: Path,
        jobdir: Path,
        *,
        use_jobid: bool = True,
        dir_index: int = 0,
    ) -> TurnoverJobFiles | None:
        # needs to be quick
        try:
            job = TurnoverJob.restore(jobfile)
        except (TypeError, UnicodeDecodeError) as e:
            current_app.logger.error("can't open: %s, reason: %s", jobfile, e)
            return None
        # TODO: tomlfile -> sqlite... convention
        directory = jobfile.parent
        stem = job.jobid if use_jobid else jobfile.stem
        data = directory.joinpath(stem + RESULT_EXT)

        has_result = data.exists()

        st = data.stat() if has_result else jobfile.stat()

        is_running = directory.joinpath(jobfile.name + ".pid").exists()

        def full_path() -> str:
            return str(directory.relative_to(jobdir) / jobfile.stem)

        return self.TurnoverJobFilesClass(
            job=job,
            directory=directory,
            name=jobfile.name,
            mtime=datetime.fromtimestamp(st.st_mtime),
            size=st.st_size,
            is_running=is_running,
            has_result=has_result,
            full_path=full_path(),
            dir_index=dir_index,
        )

    def _find_all_jobs(self, root: Path, dir_index: int) -> Iterator[TurnoverJobFiles]:
        for d, _, files in walk(str(root)):
            for f in files:
                if f.endswith(".toml"):
                    ret = self._data_from_jobfile(
                        Path(d).joinpath(f),
                        root,
                        dir_index=dir_index,
                    )
                    if ret is None:
                        continue
                    yield ret

    def find_job_files(self, jobsdir_list: Sequence[Path]) -> Jobs:
        # Maybe turn this into a database?

        running: list[TurnoverJobFiles] = []
        finished: list[TurnoverJobFiles] = []
        queued: list[TurnoverJobFiles] = []
        for dir_index, jobsdir in enumerate(jobsdir_list):
            for r in self._find_all_jobs(jobsdir, dir_index=dir_index):
                if r.status == "running":
                    target = running
                elif r.status == "pending":
                    target = queued
                else:  # stopped or failed
                    target = finished
                target.append(r)

        def bymtime(t: TurnoverJobFiles) -> datetime:
            return t.mtime

        return Jobs(
            running=sorted(running, key=bymtime, reverse=False),
            queued=sorted(queued, key=bymtime, reverse=False),  # oldest first
            finished=sorted(finished, key=bymtime, reverse=True),  # newest first
        )


class SimpleFinder(Finder):
    TurnoverJobFilesClass = PersonalJobFiles
    """use full_path as dataid"""


CFG = ".turnover-layout.cfg"


class JobsManager:
    LocatorClass: type[Locator] = Locator
    FinderClass: type[Finder] = Finder

    def __init__(
        self,
        jobsdir_list: Sequence[Path],
        check_dir: bool = True,
        method: int = 0,
        sub_directories: int = 2,
        max_length: int = 20,
    ):
        self.jobsdir_list = jobsdir_list
        self.check_dir = check_dir
        self.method = method
        self.sub_directories = sub_directories
        self.max_length = max_length

    def find_jobs(self) -> Jobs:
        return self.FinderClass().find_job_files(self.jobsdir_list)

    def locate_from_url(self, data_url: str) -> Locator:
        if "---" not in data_url:
            abort(404)
        n, jobid = data_url.split("---", maxsplit=1)
        if not n.isdigit():
            abort(404)
        dir_index = int(n)
        return self.LocatorClass(
            jobid,
            self,
            dir_index,
        )

    def locate_from_new(self, jobid: str) -> Locator:
        return self.LocatorClass(
            jobid,
            self,
            0,
        )

    def stem(self, jobid: str) -> str:
        method = self.method
        if method == -1:
            return "project"
        if method == 0:
            return jobid
        return jobid[:method]

    def locate_directory(self, jobid: str, dir_index: int) -> Path:
        jobsdir = self.jobsdir_list[dir_index]
        if self.sub_directories <= 0:
            return jobsdir.joinpath(jobid)
        return jobsdir.joinpath(jobid[: self.sub_directories], jobid)

    def _new_jobid(self, possible_id: str | None = None) -> str:
        # find a unique job id based on user input first
        # the randomly generate new ones
        jobid = (
            self._create_jobid()
            if possible_id is None or not self.check_dir
            else slugify(possible_id)
        )
        if self.check_dir:
            locate = self.locate_from_new(jobid)
            while locate.is_in_use():
                jobid = self._create_jobid()
                locate = self.locate_from_new(jobid)
        return jobid

    def prefix_jobid(self, prefix: str, ext: int = 6) -> str:
        prefix = chop(slugify(prefix), self.max_length)
        # pad out with random string
        # ext = self.max_length - len(prefix) + ext
        jobid = prefix + "-" + self._create_short_jobid(ext)
        if self.check_dir:
            locate = self.locate_from_new(jobid)
            while locate.is_in_use():
                jobid = prefix + "-" + self._create_short_jobid(ext)
                locate = self.locate_from_new(jobid)
        return jobid

    @classmethod
    def _create_jobid(cls) -> str:
        return create_jobid()

    @classmethod
    def _create_short_jobid(cls, n: int = 8) -> str:
        return create_short_jobid(n)

    @classmethod
    def read_cfg(cls, cfg: Path) -> tuple[int, int] | None:
        try:
            with cfg.open(encoding="utf8") as fp:
                method, sub_directories = map(int, fp.read().strip().split(","))
                return method, sub_directories
        except Exception:
            return None

    def write_config(self) -> None:
        jobsdir = self.jobsdir_list[0]
        cfg = jobsdir / CFG
        with cfg.open("wt", encoding="utf8") as fp:
            fp.write(f"{self.method},{self.sub_directories}")

    def check_config(self) -> bool:
        """Returns False is there is a prexisting layout"""
        jobsdir = self.jobsdir_list[0]
        cfg = jobsdir / CFG
        if cfg.exists():
            ret = self.read_cfg(cfg)
            if ret is not None:
                self.method = ret[0]
                self.sub_directories = ret[1]
            return False

        return True


class PersonalJobsManager(JobsManager):
    LocatorClass: type[Locator] = SimpleLocator
    FinderClass: type[Finder] = SimpleFinder


def chop(prefix: str, max_length: int) -> str:
    # take letters from front and back of string
    # to a maximum of max_length
    if len(prefix) > max_length:
        s = prefix[: (max_length * 2) // 3]
        e = max_length - len(s)
        prefix = s + prefix[-e:]
    return prefix


def create_jobid() -> str:
    return str(uuid4())


# this has to form both a filename (on case preserving filesystems)
# *and* a url
ALPHABET = string.ascii_lowercase + string.digits


def create_short_jobid(n: int = 8) -> str:
    return "".join(random.choices(ALPHABET, k=n))
