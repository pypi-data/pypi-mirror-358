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

    logger.debug(f"MAKE_REQUEST: {method.upper()} => {base_url}{path}")

    if method.upper() == 'GET':
        try:
            response = await client.get(path, options=options, cast_to=object)
            return response
        except Exception as e:
            logger.error(e)

            if api_key:
                headers = {
                    "authorization": f"Bearer {api_key}",
                    "Authorization": f"Bearer {api_key}",
                    **(headers or {})
                }

            async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=timeout or 100) as client:
                response = await client.get(f"{base_url}{path}", params=params)
                return response.json()

    elif method.upper() == 'POST':
        response = await client.post(path, body=payload, options=options, files=files, cast_to=object)
        return response


if __name__ == '__main__':
    from meutils.io.files_utils import to_bytes

    base_url = "https://api.chatfire.cn/tasks/kling-57751135"
    base_url = "https://httpbin.org"

    # arun(make_request(base_url=base_url, path='/ip'))

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
    #
    # arun(make_request(base_url=base_url,
    #                   path=path,
    #                   method="post",
    #                   files=files,
    #                   payload=payload,
    #
    #                   api_key="WPCSA3ZYD8KBQQ2ZKTAPVUA059J2Q47TLWGB2ZMQ"))

    base_url = "https://queue.fal.run/fal-ai/kling-video/lipsync/audio-to-video"
    payload = {
        "video_url": "https://fal.media/files/koala/8teUPbRRMtAUTORDvqy0l.mp4",
        "audio_url": "https://storage.googleapis.com/falserverless/kling/kling-audio.mp3"
    }

    # arun(make_request(
    #     base_url=base_url,
    #     payload=payload,
    #     headers=headers,
    #     method="post"
    # ))

    FAL_KEY = "56d8a95e-2fe6-44a6-8f7d-f7f9c83eec24:537f06b6044770071f5d86fc7fcd6d6f"
    REQUEST_ID = "f05a3542-0e60-4ba3-aefb-e570f4078d14"
    base_url = "https://queue.fal.run/fal-ai"
    path = f"/kling-video/requests/{REQUEST_ID}"
    # path=f"/kling-video/requests/{REQUEST_ID}/status"

    headers = {
        "Authorization": f"key {FAL_KEY}"
    }
    arun(make_request(
        base_url=base_url,
        path=path,
        headers=headers,
        method="get"
    ))

    # arun(make_request(
    #     base_url=base_url,
    #     path=path,
    #     headers=headers,
    #     method="post"
    # ))

    # 'detail': 'Request is still in progress',
