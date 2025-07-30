from typing import Callable
import webview
from .py_ts import convert_to_ts, output_ts_file
from .log import logger


def out_ts_file(out_ts_file: str, *args: Callable):
    """
    输出ts文件
    """
    for func in args:
        if out_ts_file:
            convert_to_ts(func)

    if len(args) >0:
        try:
            output_ts_file(out_ts_file, "_api")
            # 向out_ts_file文件尾部写入
            with open(out_ts_file, "a", encoding="utf-8") as f:
                s0 = "export const api: typeof _api;"
                s = "\n\n\ndeclare namespace pywebview {\n  " + s0 + "\n }"
                f.write(s)
        except Exception as e:
            logger.debug(e)


def expose(window: webview.Window, *args: Callable):
    """
    向js环境暴露方法
    """
    for func in args:
        window.expose(func)
