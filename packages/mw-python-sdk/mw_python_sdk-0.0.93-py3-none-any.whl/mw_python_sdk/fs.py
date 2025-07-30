import logging
from datetime import datetime, timezone
from io import BytesIO
from fsspec import AbstractFileSystem
from fsspec.spec import AbstractBufferedFile
from typing import Optional, Union, Dict, Any
import os
from mw_python_sdk.api import get_dataset, _get_download_url, _init_token, Dataset
from pathlib import Path
import requests
from requests import Response

logger = logging.getLogger("mwfs")


class MwFileSystem(AbstractFileSystem):
    """A filesystem based on a dict of BytesIO objects

    This is a global filesystem so instances of this class all point to the same
    in memory filesystem.
    """

    protocol = "mw"
    root_marker = ""
    dataset_id = ""
    commit = None
    token = ""

    def __init__(
        self,
        *args,
        dataset_id: str,
        token: Union[str, None] = None,
        commit: Union[str, None] = None,
        **storage_options,
    ):
        super().__init__(*args, **storage_options)
        self.token = _init_token(token)
        self.dataset_id = dataset_id
        dataset_detail = get_dataset(
            self.dataset_id, commit=self.commit, token=self.token
        )
        logger.debug(dataset_detail.files)
        if dataset_detail is None:
            raise ValueError(f"Dataset '{self.dataset_id}' not found.")
        if commit is None:
            self.commit = dataset_detail.latest_commit_id()
        else:
            self.commit = commit
        self.dataset_detail = dataset_detail

    def ls(self, path, detail=True, **kwargs):
        # print("ls")
        path = self._strip_protocol(path)

        logger.debug(f"Listing files in {path} in dataset '{self.dataset_id}'")

        out = []
        for file in self.dataset_detail.files:
            # 子目录和访问目录一致，返回文件列表
            if file.sub_path.rstrip("/") == path.lstrip("/"):
                logger.debug(
                    f"compare {file.sub_path.rstrip('/')} == {path.lstrip('/')}"
                )
                out.append(
                    {
                        "name": os.path.join(file.sub_path, os.path.basename(file.key)),
                        "size": file.size,
                        "type": "file",
                    }
                )
            elif file.sub_path.rstrip("/").startswith(path.lstrip("/")) and Path(
                file.sub_path.rstrip("/")
            ).parent == Path(path.lstrip("/")):
                out.append(
                    {
                        "name": file.sub_path.rstrip("/"),
                        "size": None,
                        "type": "directory",
                    }
                )
        logger.debug(f"Found {len(out)} files")
        if detail:
            return out
        return sorted([f["name"] for f in out])

    def mkdir(self, path, create_parents=True, **kwargs):
        pass

    def makedirs(self, path, exist_ok=False):
        try:
            self.mkdir(path, create_parents=True)
        except FileExistsError:
            if not exist_ok:
                raise

    def pipe_file(self, path, value, **kwargs):
        """Set the bytes of given file

        Avoids copies of the data if possible
        """
        self.open(path, "wb", data=value)

    def rmdir(self, path):
        raise NotImplementedError

    def info(self, path: str, **kwargs) -> Dict[str, Any]:
        logger.debug("Getting info for %s in dataset '%s'", path, self.dataset_id)
        path = self._strip_protocol(path)
        logger.debug("Getting info for %s in dataset '%s'", path, self.dataset_id)
        out = None
        if path == "/" or path == "":
            out = {"name": "", "size": None, "type": "directory"}
        else:
            parent_path = self._parent(path)
            if parent_path in self.dircache:
                out1 = [o for o in self.dircache[parent_path] if o["name"] == path]
                if not out1:
                    raise FileNotFoundError(f"Path {path} not found in cache")
                out = out1[0]
            out_files = self.ls(parent_path)
            for out_file in out_files:
                if out_file.get("name") == path:
                    out = out_file
            if out is None:
                raise FileNotFoundError(f"Path {path} not found")
        return out

    def _open(
        self,
        path,
        mode="rb",
        block_size=None,
        autocommit=True,
        cache_options=None,
        **kwargs,
    ):
        if "a" in mode:
            raise NotImplementedError("Appending to remote files is not yet supported.")
        if "w" in mode:
            raise NotImplementedError("Writing to remote files is not yet supported.")
        return MwFileSystemFile(
            self,
            path,
            mode=mode,
            block_size=block_size,
            cache_options=cache_options,
            **kwargs,
        )

    def _rm(self, path):
        raise NotImplementedError

    def modified(self, path):
        raise NotImplementedError

    def created(self, path):
        raise NotImplementedError

    def rm(self, path, recursive=False, maxdepth=None):
        raise NotImplementedError


class MwFileSystemFile(AbstractBufferedFile):
    url: str

    def __init__(self, fs: MwFileSystem, path: str, mode: str = "rb", **kwargs):
        self.url = _get_download_url(
            fs.dataset_id, path, str(fs.commit), token=fs.token
        )
        logger.debug(f"======== MwFileSystemFile: {self.url}")
        # self.details = fs.info(path)
        super().__init__(fs, path, mode=mode, **kwargs)
        self.fs: MwFileSystem

    def _fetch_range(self, start: int, end: int) -> bytes:
        headers = {
            "range": f"bytes={start}-{end - 1}",
        }
        r = requests.get(self.url, headers=headers, timeout=500)
        if int(r.status_code / 100) != 2:
            raise IOError(
                f"Failed to fetch range {start}-{end}: {r.text}, status code: {r.status_code}"
            )
        return r.content
