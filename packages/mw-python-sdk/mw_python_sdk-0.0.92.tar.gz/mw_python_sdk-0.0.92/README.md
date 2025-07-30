# mw-sdk-python

## 简介
`mw-sdk-python` 是一个用于与 Heywhale 平台交互的 Python SDK，提供了简单易用的接口来管理和获取数据集。

## 安装方式

```bash
pip install mw-sdk-python
```

## 快速开始

下面是一个简单示例，展示如何使用 SDK 根据数据集ID下载数据集：

```python
from mw_python_sdk import download_dir
download_dir("66b08ec9898e74a8232bb2d1")
```

## 配置说明

SDK 支持以下环境变量配置：

- `MW_TOKEN`: 身份验证令牌。若代码中未直接提供 token 参数，将使用此环境变量的值
- `HEYWHALE_HOST`: Heywhale 平台地址（可选），默认为 `https://www.heywhale.com`

## 开发指南

### 本地开发安装

```bash
# 基础安装
pip install -e .

# 安装 LLM 相关功能（可选）
pip install -e '.[llm]'
```

### 发布打包

以 0.1.0 版本为例：

```bash
python -m build
python -m twine upload dist/mw_python_sdk-0.1.0*
```
可以用一些uv或者其他的包管理工具来上传，这里只是一个示例，因为llm子模块的一些依赖支持不到Python3.7，
而Python又没有分子模块的版本支持的功能，所以没有用包管理工具，这里面其实llm子模块要求python大于3.8。

### API 文档

* 数据集 API 在[这里](http://dev-v5z6xn18uw.modelwhale.com/docs/org_admin/api/dataset/dataset-upload-token.html)
* RAG API 在[这里](http://dev-v5z6xn18uw.modelwhale.com/docs/org_admin/api/rag/search.html)

### Python 版本兼容性

当前支持 Python 3.7 及以上版本。开发时需注意以下限制：

1. `dataclass` 装饰器仅支持 Python 3.7+
2. Union 类型的 `|` 语法糖仅支持 Python 3.10+，请使用传统写法
3. 参数分隔符 `/` 仅支持 Python 3.8+，请避免使用

### 类型注解说明

根据 PEP 585，Python 的类型注解系统正在经历以下演进：

1. Python 3.7: 引入 `from __future__ import annotations`，支持 `list[str]` 形式的标准库泛型注解
2. Python 3.9: 默认支持 `list[str]` 语法，无需 future import
3. typing 模块中的冗余泛型类型已被弃用
4. Python 3.14 (预计): 移除 typing 模块中的冗余类型

请在开发时考虑上述变化，合理使用类型注解。
