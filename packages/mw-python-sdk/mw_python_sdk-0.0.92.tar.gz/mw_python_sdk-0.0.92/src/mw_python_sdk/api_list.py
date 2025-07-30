"""
API for listing or searching datasets.
"""

from typing import List, Optional
import os

from datetime import datetime
import requests  # type: ignore


from mw_python_sdk.api import HEYWHALE_SITE
from mw_python_sdk.core import Dataset, DatasetCommit, DatasetList
from mw_python_sdk.utils import parse_datetime, convert_to_dataset_file, logger


def _list_datasets(
    title: str = "",
    limit: int = 10,
    page: int = 1,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: Optional[str] = None,
):
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    headers = {
        "x-kesci-token": token,
    }

    url = f"{HEYWHALE_SITE}/api/user/datasets"
    params = {
        "perPage": limit,
        "page": page,
        "Title": title,
        "startDate": start_date,
        "endDate": end_date,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10,
    )
    if response.status_code == 200:
        document = response.json()
        datasets: List[Dataset] = []
        for d in document.get("data"):
            files = convert_to_dataset_file(d.get("Files"))
            files_with_subpath = convert_to_dataset_file(d.get("FilesStructure"))
            if len(files) > 0:
                files_key_set = set([file.key for file in files])
                for file in files:
                    if file.key not in files_key_set:
                        files_with_subpath.append(file)
            commits = []
            if d.get("DatasetVersions") is not None:
                commits = [
                    DatasetCommit(
                        commit.get("_id"),
                        commit.get("CommitMessage"),
                        parse_datetime(commit.get("CreateDate")),
                    )
                    for commit in d.get("DatasetVersions")
                ]
            datasets.append(
                Dataset(
                    _id=d.get("_id"),
                    title=d.get("Title"),
                    short_description=d.get("ShortDescription"),
                    folder_name=d.get("FolderName"),
                    files=files_with_subpath,
                    commits=commits,
                    created_at=parse_datetime(d.get("CreateDate")),
                    updated_at=parse_datetime(d.get("UpdateDate")),
                )
            )
        return DatasetList(
            datasets=datasets,
            total=document.get("totalNum"),
            page=document.get("page"),
            limit=document.get("perPage"),
        )
    else:
        print(response.text)
        response.raise_for_status()
        return None


class DatasetIterator:
    """
    DatasetIterator 类

    该类提供了一个迭代器接口，用于遍历数据集。
    它封装了数据集加载、预处理和迭代的逻。
    """

    def __init__(self, title, page=1, limit=10):
        self.title = title
        self.limit = limit
        self.page = page
        self.total = 0
        self.processed_count = 0
        self.current_batch = []
        self.finished = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self.current_batch and not self.finished:
            # Fetch the next page of datasets
            dataset_list = _list_datasets(
                title=self.title,
                page=self.page,
                limit=self.limit,
            )
            self.total = dataset_list.total

            if not dataset_list.datasets:
                self.finished = True
                raise StopIteration

            self.current_batch = dataset_list.datasets
            self.processed_count += len(self.current_batch)
            logger.debug("Processed: %d / Total: %d", self.processed_count, self.total)
            # If all items have been processed, mark as finished
            if self.processed_count >= self.total:
                self.finished = True
            else:
                self.page += 1

        if not self.current_batch:
            raise StopIteration

        # Return the next dataset in the current batch
        return self.current_batch.pop(0)


def list_all_datasets(title: str = "") -> List[Dataset]:
    """
    列出所有满足给定标题的数据集

    Args:
        title (str, optional): 数据集标题，默认为空字符串。

    Returns:
        List[Dataset]: 包含所有满足给定标题的数据集的列表。

    """
    datasets = list()
    for dataset in DatasetIterator(title):
        datasets.append(dataset)
    return datasets


def list_datasets(
    title: str = "",
    limit: int = 10,
    page: int = 1,
) -> DatasetIterator:
    """
    返回数据集的迭代器对象，可指定数据集标题、返回数据条数及页数

    Args:
        title (str, optional): 数据集标题. Defaults to "".
        limit (int, optional): 每页返回的数据条数. Defaults to 10.
        page (int, optional): 页码. Defaults to 1.

    Returns:
        DatasetIterator: 数据集的迭代器对象.

    """
    return DatasetIterator(title, page, limit)
