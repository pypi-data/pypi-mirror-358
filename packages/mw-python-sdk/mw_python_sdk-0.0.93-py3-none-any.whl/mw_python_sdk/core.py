"""
This module defines data classes to represent various entities involved in dataset management,
including dataset files, commits, and metadata. The classes are designed to encapsulate information
related to datasets, their commits, and associated files in a structured format.

Classes:
    - UploadInfo: Holds the necessary information for uploading files.
    - DatasetCommit: Represents a commit within a dataset, including metadata such as commit message and creation date.
    - DatasetFile: Represents a file within a dataset, including its storage key, size, and optional sub-path.
    - Dataset: Represents an entire dataset, including metadata, files, and commits.
    - DatasetList: Represents a list of datasets, including pagination information.
"""

from dataclasses import dataclass
from datetime import datetime
import os
from typing import List


@dataclass(frozen=True)
class UploadInfo:
    """
    UploadInfo represents the information required for uploading.
    """

    ak: str
    sk: str
    token: str  # upload token
    endpoint: str  # endpoint
    region: str  # region
    bucket: str  # bucket for uploading
    prefix_to_save: str  # file upload directory structure: dataset / user ID /
    s3ForcePathStyle: bool  # whether to use path style for S3


@dataclass(frozen=True)
class DatasetCommit:
    """
    DatasetCommit represents a dataset commit.
    """

    _id: str
    commit_message: str
    created_at: datetime

    def get_id(self):
        """
        Returns the ID of the dataset commit.
        Returns:
            str: The ID of the dataset commit.
        """
        return self._id


@dataclass
class DatasetFile:
    """
    DatasetFile represents a file on S3.
    格式说明：
    数据集有两种形式：
    第一种：没有sub_path，在数据集中的字段Files
    第二种：有sub_path，在数据集中的字段FilesStructure，并且Files需要对等的存在（没有sub_path)
    处理逻辑应该是优先FilesStructure，然后Files，这样可以兼容两种形式。
    key共有云上的组成是 prefix/timestamp_version/filename
    其中 prefix 是 datasets/$user_id，例如 dataset/59ad0f2e21100106622a1f0c/
    timestamp_version 是时间戳和版本号 1722846915864_1
    filename 是文件名
    注意：sub_path自目录的信息并不存在于key中，而是通过FileStructure的SubPath保存，
    所以要表示一个有目录的文件是这样的folder_a/b.txt，其中 filename是b.txt
    SubPath是folder_a，在没有FileStructure的老数据集中，SubPath是空字符串。
    新数据集会同时存在Files FilesStructure，老数据集只有Files，所以
    相关处理都按照上述的处理逻辑喝顺序兼容。
    """

    _id: str
    key: str
    size: int
    sub_path: str = ""

    def path_in_dataset(self):
        """
        Returns the path of the file within the dataset.

        If the `sub_path` attribute is set, the path will be constructed by appending the `sub_path`
        and the base name of the `key` attribute. Otherwise, only the base name of the `key` attribute
        will be returned.

        Returns:
            str: The path of the file within the dataset.
        """
        if self.sub_path:
            return os.path.join(self.sub_path, os.path.basename(self.key))
        else:
            return os.path.basename(self.key)


@dataclass(frozen=True)
class Dataset:
    """
    Dataset represents a dataset.
    """

    _id: str
    title: str
    short_description: str
    folder_name: str
    files: List[DatasetFile]
    commits: List[DatasetCommit]
    created_at: datetime
    updated_at: datetime

    def __repr__(self):
        return f"Dataset(_id={self._id}, title={self.title})"

    def get_id(self):
        """
        Returns the ID of the dataset.
        Returns:
            str: The ID of the dataset.
        """
        return self._id

    def latest_commit_id(self):
        return self.commits[-1]._id

@dataclass(frozen=True)
class DatasetList:
    """
    DatasetList represents a list of datasets.
    """

    datasets: List[Dataset]
    total: int
    page: int
    limit: int
