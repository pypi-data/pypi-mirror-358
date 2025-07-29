#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : utils
# @Time         : 2024/12/20 16:38
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :

from meutils.pipe import *
from openai import AsyncClient


async def make_request(
        base_url: str,
        api_key: Optional[str] = None,
        headers: Optional[dict] = None,

        path: Optional[str] = None,

        params: Optional[dict] = None,
        payload: Optional[dict] = None,
        files: Optional[dict] = None,

        method: str = "POST",

        timeout: Optional[int] = None,
):
    client = AsyncClient(base_url=base_url, api_key=api_key, default_headers=headers, timeout=timeout)

    options = {}
    if params:
        options["params"] = params

    path = path or "/"
    path = f"""/{path.removeprefix("/")}"""

    if method.upper() == 'GET':
        response = await client.get(path, options=options, cast_to=object)
        return response
    elif method.upper() == 'POST':
        response = await client.post(path, body=payload, options=options, files=files, cast_to=object)
        return response


if __name__ == '__main__':
    from meutils.io.files_utils import to_bytes

    base_url = "https://api.chatfire.cn/tasks/kling-57751135"
    base_url = "https://httpbin.org"

    arun(make_request(base_url=base_url, path='/ip'))

    base_url = "https://ai.gitee.com/v1"
    path = "/images/mattings"
    headers = {
        "Authorization": "Bearer WPCSA3ZYD8KBQQ2ZKTAPVUA059J2Q47TLWGB2ZMQ",
        "X-Package": "1910"
    }
    payload = {
        "model": "RMBG-2.0",
        "image": "path/to/image.png"
    }
    files = {
        "image": ('path/to/image.png', to_bytes("https://oss.ffire.cc/files/kling_watermark.png"))
    }

    arun(make_request(base_url=base_url,
                      path=path,
                      method="post",
                      files=files,
                      payload=payload,

                      api_key="WPCSA3ZYD8KBQQ2ZKTAPVUA059J2Q47TLWGB2ZMQ"))
