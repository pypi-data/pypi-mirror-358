#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
from pathlib import Path
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Literal,
    Mapping,
    Optional,
    Union,
    get_args,
    overload,
)

from pythonwrench.csv import Orient
from pythonwrench.csv import dump_csv as _dump_csv_base
from pythonwrench.csv import load_csv as _load_csv_base
from pythonwrench.importlib import Placeholder
from pythonwrench.io import _setup_output_fpath
from pythonwrench.warnings import warn_once

from torchwrench.core.packaging import _PANDAS_AVAILABLE

from .common import as_builtin

if _PANDAS_AVAILABLE:
    import pandas as pd  # type: ignore

    DataFrame = pd.DataFrame  # type: ignore
else:

    class DataFrame(Placeholder): ...


CSVBackend = Literal["csv", "pandas", "auto"]


def dump_csv(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]], Iterable],
    fpath: Union[str, Path, None] = None,
    *,
    overwrite: bool = True,
    to_builtins: bool = False,
    make_parents: bool = True,
    backend: CSVBackend = "auto",
    header: Union[bool, Literal["auto"]] = "auto",
    **backend_kwds,
) -> str:
    """Dump content to csv format."""
    if backend == "auto":
        if isinstance(data, DataFrame):
            backend = "pandas"
        else:
            backend = "csv"

    if backend == "csv":
        return _dump_csv_base(
            data,
            fpath,
            overwrite=overwrite,
            make_parents=make_parents,
            to_builtins=to_builtins,
            header=header,
            **backend_kwds,
        )

    elif backend == "pandas":
        if to_builtins:
            if isinstance(data, DataFrame):
                msg = f"Inconsistent combinaison of arguments: {to_builtins=}, {backend=} and {type(data)=}."
                warn_once(msg)
            data = as_builtin(data)

        header = header if header != "auto" else True
        return _dump_csv_with_pandas(
            data,
            fpath,
            overwrite=overwrite,
            make_parents=make_parents,
            header=header,
            **backend_kwds,
        )

    else:
        msg = f"Invalid argument {backend=}. (expected one of {get_args(CSVBackend)})"
        raise ValueError(msg)


@overload
def load_csv(
    fpath: Union[str, Path],
    /,
    *,
    orient: Literal["dict"],
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    backend: CSVBackend = "csv",
    # CSV reader kwargs
    delimiter: Optional[str] = None,
    **backend_kwds,
) -> Dict[str, List[Any]]: ...


@overload
def load_csv(
    fpath: Union[str, Path],
    /,
    *,
    orient: Literal["list"] = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    backend: CSVBackend = "csv",
    # CSV reader kwargs
    delimiter: Optional[str] = None,
    **backend_kwds,
) -> List[Dict[str, Any]]: ...


def load_csv(
    fpath: Union[str, Path],
    /,
    *,
    orient: Orient = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    backend: CSVBackend = "csv",
    # CSV reader kwargs
    delimiter: Optional[str] = None,
    **backend_kwds,
) -> Union[List[Dict[str, Any]], Dict[str, List[Any]]]:
    if backend == "auto":
        if _PANDAS_AVAILABLE:
            backend = "pandas"
        else:
            backend = "csv"

    if backend == "csv":
        return _load_csv_base(
            fpath,
            orient=orient,
            header=header,
            comment_start=comment_start,
            strip_content=strip_content,
            delimiter=delimiter,
            **backend_kwds,
        )

    elif backend == "pandas":
        return _load_csv_with_pandas(
            fpath,
            orient=orient,
            header=header,
            comment_start=comment_start,
            strip_content=strip_content,
            delimiter=delimiter,
            **backend_kwds,
        )

    else:
        msg = f"Invalid argument {backend=}. (expected one of {get_args(CSVBackend)})"
        raise ValueError(msg)


def _dump_csv_with_pandas(
    data: Union[Iterable[Mapping[str, Any]], Mapping[str, Iterable[Any]]],
    fpath: Union[str, Path, None] = None,
    *,
    overwrite: bool = True,
    make_parents: bool = True,
    **kwargs,
) -> str:
    backend = "pandas"
    if not _PANDAS_AVAILABLE:
        msg = f"Invalid argument {backend=} without pandas installed."
        raise ValueError(msg)

    df = pd.DataFrame(data)  # type: ignore

    # set index to False by default
    kwargs.setdefault("index", False)

    file = io.StringIO()
    df.to_csv(file, **kwargs)
    content = file.getvalue()
    file.close()

    fpath = _setup_output_fpath(fpath, overwrite, make_parents)
    if fpath is not None:
        fpath.write_text(content)

    return content


def _load_csv_with_pandas(
    fpath: Union[str, Path],
    /,
    *,
    orient: Orient = "list",
    header: bool = True,
    comment_start: Optional[str] = None,
    strip_content: bool = False,
    # CSV reader kwargs
    delimiter: Optional[str] = None,
    **backend_kwds,
) -> Union[List[Dict[str, Any]], Dict[str, List[Any]]]:
    backend = "pandas"

    if not _PANDAS_AVAILABLE:
        msg = f"Invalid argument {backend=} without pandas installed."
        raise ValueError(msg)

    if strip_content:
        msg = f"Invalid argument {strip_content=} with {backend=}."
        raise ValueError(msg)

    if comment_start is not None:
        msg = f"Invalid argument {comment_start=} with {backend=}."
        raise ValueError(msg)

    if len(backend_kwds) > 0:
        msg = f"Invalid arguments {backend_kwds=} with {backend=}."
        raise ValueError(msg)

    df = pd.read_csv(fpath, delimiter=delimiter)  # type: ignore

    if orient == "list":
        return df.to_dict("records")  # type: ignore
    elif orient == "dict":
        return df.to_dict("list")  # type: ignore
    else:
        msg = f"Invalid argument {orient=}. (expected one of {get_args(Orient)})"
        raise ValueError(msg)
