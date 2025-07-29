#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : qwen
# @Time         : 2025/1/17 16:45
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  :
"""
 File "/usr/local/lib/python3.10/site-packages/meutils/llm/completions/qwenllm.py", line 47, in create
    yield response.choices[0].message.content
AttributeError: 'str' object has no attribute 'choices'

"""

from openai import AsyncOpenAI

from meutils.pipe import *
from meutils.decorators.retry import retrying
from meutils.io.files_utils import to_bytes, guess_mime_type
from meutils.caches import rcache

from meutils.llm.openai_utils import to_openai_params

from meutils.config_utils.lark_utils import get_next_token_for_polling
from meutils.schemas.openai_types import chat_completion, chat_completion_chunk, CompletionRequest, CompletionUsage, \
    ChatCompletion

FEISHU_URL = "https://xchatllm.feishu.cn/sheets/Bmjtst2f6hfMqFttbhLcdfRJnNf?sheet=PP1PGr"

base_url = "https://chat.qwen.ai/api"

from fake_useragent import UserAgent

ua = UserAgent()

thinking_budget_mapping = {
    "low": 1000,
    "medium": 8000,
    "high": 24000
}

COOKIE = """
cna=KP9DIEqqyjUCATrw/+LjJV8F; _bl_uid=LXmp28z7dwezpmyejeXL9wh6U1Rb; cnaui=310cbdaf-3754-461c-a3ff-9ec8005329c9; aui=310cbdaf-3754-461c-a3ff-9ec8005329c9; x-ap=ap-southeast-1; sca=43897cb0; acw_tc=0a03e53417483123807755658e597c5e3685457054f2ca60a0a8d87b657874; _gcl_au=1.1.106229673.1748312382; xlly_s=1; token=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjMxMGNiZGFmLTM3NTQtNDYxYy1hM2ZmLTllYzgwMDUzMjljOSIsImV4cCI6MTc1MDkwNDU2MH0.nV7I1sp6rAE0QnqXYKNm4I0vLZmA-TdOKWEHg_37_tw; SERVERID=1e5b6792fa61468bae321990103ad502|1748312579|1748312380; atpsida=0450727e7c9d8a7299a0b2bd_1748312579_5; ssxmod_itna=iqGxRDuQqWqxgDUxeKYI5q=xBDeMDWK07DzxC5750CDmxjKidKDUGQN0bFP=jhWOGxDkYCA+UQSD0HPKmDA5DnGx7YDtr4FN4SeKhDwIa78YRwwHQiGoh=LTX90w=3qflZqcj1T3xoD==hYDmeDUxD1GDDkS0PDxOPD5xDTDWeDGDD3t4DCCfYYD0RpiboIVxRhTABpDYPYPR4YDY56DAqEz4SpVaxXTDDzw4iaPf4vwDi8D7FRG0RpD7P6fmQDXaYDEAWmFk=Dv6Lh+QwI1/oYOyyDc=DoCO0Km0DTVj2qPGGiU5eiBdnNC4490i+yte+in2MWYHDDW=4=5rzqDxKGe1qC+LimweRk5yxmLhdYY4KGYqOqIheUk5ZB5x2QgohQBxN7spmxFezNiDD; ssxmod_itna2=iqGxRDuQqWqxgDUxeKYI5q=xBDeMDWK07DzxC5750CDmxjKidKDUGQN0bFP=jhWOGxDkYCA+UQmDDpU3qY6obeDLWr7pfFyiDDsa7QaIhEVl4FKFerBUoQiRQlSzS+caiWpDOqz2HrsO6xFOwpKsSOYH0Q0WwhDs0Ye1mah+b99w34Im3AYwt4oztFoQ7xBhThYqatKQWcgkRDBDCOiLViK62z51rnpzpbHH7pFpS=Y4zfHiWfozYCf+9FcGmRMsMEYFGRP+TgG9EbEi3Khm0lQmt2AL=quK6RomKnFmmpjzYzxHQ/QEK0AAa3qGPOl3crGu7DDpQnxjfEEgWD/oEHaE4l6jOpKp6DI6P=vQa39gN6h5i3R5eInP2Gob9pY7DKDr3lYiTZrC3R2Yiz/rsFIG1j5n=2=DD3=obLGPQsWnOZWSinlZ=KjKGpIwRPKn3jpohCU+2PciIEehVxTSnioeIx6xdp91zK29tHtN2Zcgi0clGNaY4jIenYlnw+/Qlapjg6Qho=3E/2v3mIjaYygren01ebwPI4EKgDY+4NyiTXYmU+o/lGSogI=GT/38rPOnA5mjuDg2Ub=+HtTjKnpYoEaTvwj3K0GI7FKARVAv=Wojxe0nHRBwhrQIa1vMpv5pfQ8LGCXGp=lZ3Q8v+6=lSfexroPjNP9MvyNVAXQhnKvyAwT/KEsgh/eOdqx0YiHaP1kwxzsu54i4eGiQDshEOQoiRlPBqiDiSRDQay2k1x4xWDhpBTjqZ0Neer0qlDK0YbDpBYKxSGDD; tfstk=gy8S5jal7pL47z_LOgc4laG38cQQOjuaeW1psBUz9aQRdW9e6MCzzbxBcpJ5eU7-ZoUBQpYrZMdRRipBCgUKqMCvlpJBzkd82-QvQ1KUpv4LH-C1yMxPLTWCRBvsgAuZ7QAl-akZQVyg4ccA76BdpJPAkw5IYeMoXQAl-SDk9fRkZW1NLUsRJpQAD1CRJkB8yjsAs1bLyMU8D-BcHwCdvTQAk61dpkIJpIhfttBdJgpdkj1n_yV1O06kNbzD-uH4ifA5hyUplsHhpQig5_8lNgW9wUwzUXf5VOdRhAjyDMIBFgTqPRfWDC9PNp0graIB2hQJRAg5kCx2es9KCk6vfUYCbUM_jTLlKd_JcxU5JaK95wQIf7f2PILGAUD7kT9DMh7kWx4BBIRwriYIC-BH41bANnGLDTId4azNCak3ASsgRs6ZGjZ3xSw1l2pVr0vc2sf50jGbeHjRis1mGjZ3xgCcN_GjG8Kh.; isg=BOrqXB6_dpCyTPX0tTuBOG9yO1aMW261hQXS_3ShLD3Op4xhWOtyxWGRN9O7V-ZN
""".strip()


@retrying()
async def to_file(file, api_key, cookie: Optional[str] = None):
    qwen_client = AsyncOpenAI(
        base_url="https://all.chatfire.cn/qwen/v1",
        api_key=api_key,
        default_headers={
            'User-Agent': ua.random,
            'Cookie': cookie or COOKIE
        }
    )
    filename = Path(file).name if isinstance(file, str) else 'untitled'
    mime_type = guess_mime_type(file)
    file_bytes: bytes = await to_bytes(file)
    file = (filename, file_bytes, mime_type)
    file_object = await qwen_client.files.create(file=file, purpose="file-extract")
    logger.debug(file_object)
    return file_object


async def create(request: CompletionRequest, token: Optional[str] = None, cookie: Optional[str] = None):
    cookie = cookie or COOKIE

    if request.temperature > 1:
        request.temperature = 1

    token = token or await get_next_token_for_polling(feishu_url=FEISHU_URL, from_redis=True)

    logger.debug(token)

    client = AsyncOpenAI(
        base_url=base_url,
        api_key=token,
        default_headers={
            'User-Agent': ua.random,
            'Cookie': cookie,
        }
    )
    # qwen结构
    model = request.model.lower()
    if any(i in model for i in ("research",)):  # 遇到错误 任意切换
        request.model = np.random.choice({""})
        request.messages[-1]['chat_type'] = "deep_research"

        # request.messages["extra"] = {
        #     "meta": {
        #         "subChatType": "deep_thinking"
        #     }
        # }

    elif any(i in model for i in ("search",)):
        request.model = "qwen-max-latest"
        request.messages[-1]['chat_type'] = "search"

    # 混合推理
    if (request.reasoning_effort
            or request.last_user_content.startswith("/think")
            or hasattr(request, "enable_thinking")
            or hasattr(request, "thinking_budget")
    ):
        feature_config = {"thinking_enabled": True, "output_schema": "phase"}
        feature_config["thinking_budget"] = thinking_budget_mapping.get(request.reasoning_effort, 1024)

        request.messages[-1]['feature_config'] = feature_config

    if any(i in model for i in ("qwq", "qvq", "think", "thinking")):
        request.model = "qwen-max-latest"
        request.messages[-1]['feature_config'] = {"thinking_enabled": True}

    if "omni" in model:
        request.max_tokens = 2048

    # 多模态: todo
    # if any(i in request.model.lower() for i in ("-vl", "qvq")):
    #     # await to_file
    last_message = request.messages[-1]
    logger.debug(last_message)

    if last_message.get("role") == "user":
        user_content = last_message.get("content")
        if isinstance(user_content, list):
            for i, content in enumerate(user_content):
                if content.get("type") == 'file_url':  # image_url file_url video_url
                    url = content.get(content.get("type")).get("url")
                    file_object = await to_file(url, token, cookie)

                    user_content[i] = {"type": "file", "file": file_object.id}

                elif content.get("type") == 'image_url':
                    url = content.get(content.get("type")).get("url")
                    file_object = await to_file(url, token, cookie)

                    user_content[i] = {"type": "image", "image": file_object.id}

        elif user_content.startswith("http"):
            file_url, user_content = user_content.split(maxsplit=1)

            user_content = [{"type": "text", "text": user_content}]

            file_object = await to_file(file_url, token, cookie)

            content_type = file_object.meta.get("content_type", "")
            if content_type.startswith("image"):
                user_content.append({"type": "image", "image": file_object.id})
            else:
                user_content.append({"type": "file", "file": file_object.id})

        request.messages[-1]['content'] = user_content

    # logger.debug(request)

    request.incremental_output = True  # 增量输出
    data = to_openai_params(request)

    # 流式转非流
    data['stream'] = True
    chunks = await client.chat.completions.create(**data)

    idx = 0
    nostream_content = ""
    nostream_reasoning_content = ""
    chunk = None
    usage = None
    async for chunk in chunks:
        if not chunk.choices: continue

        content = chunk.choices[0].delta.content or ""
        if hasattr(chunk.choices[0].delta, "phase") and chunk.choices[0].delta.phase == "think":
            chunk.choices[0].delta.content = ""
            chunk.choices[0].delta.reasoning_content = content
            nostream_reasoning_content += content
        nostream_content += chunk.choices[0].delta.content
        usage = chunk.usage or usage

        if request.stream:
            yield chunk

        idx += 1
        if idx == request.max_tokens:
            break

    if not request.stream:
        logger.debug(chunk)
        if hasattr(usage, "output_tokens_details"):
            usage.completion_tokens_details = usage.output_tokens_details
        if hasattr(usage, "input_tokens"):
            usage.prompt_tokens = usage.input_tokens
        if hasattr(usage, "output_tokens"):
            usage.completion_tokens = usage.output_tokens

        chat_completion.usage = usage
        chat_completion.choices[0].message.content = nostream_content
        chat_completion.choices[0].message.reasoning_content = nostream_reasoning_content

        yield chat_completion


if __name__ == '__main__':
    # [
    #     "qwen-plus-latest",
    #     "qvq-72b-preview",
    #     "qwq-32b-preview",
    #     "qwen2.5-coder-32b-instruct",
    #     "qwen-vl-max-latest",
    #     "qwen-turbo-latest",
    #     "qwen2.5-72b-instruct",
    #     "qwen2.5-32b-instruct"
    # ]

    user_content = [
        {
            "type": "text",
            "text": "一句话总结"
        },
        {
            "type": "image_url",
            "image_url": {
                "url": "https://fyb-pc-static.cdn.bcebos.com/static/asset/homepage@2x_daaf4f0f6cf971ed6d9329b30afdf438.png"
            }
        }
    ]

    user_content = "1+1"
    # user_content = "/think 1+1"

    # user_content = [
    #     {
    #         "type": "text",
    #         "text": "总结下"
    #     },
    #     {
    #         "type": "file_url",
    #         "file_url": {
    #             "url": "https://oss.ffire.cc/files/AIGC.pdf"
    #         }
    #     }
    #
    # ]

    request = CompletionRequest(
        # model="qwen-turbo-2024-11-01",
        # model="qwen-max-latest",
        # model="qvq-max-2025-03-25",
        # model="qvq-72b-preview-0310",
        model="qwen2.5-omni-7b",

        # model="qwen-max-latest-search",
        # model="qwq-max",
        # model="qwq-32b-preview",
        # model="qwq-max-search",

        # model="qwen2.5-vl-72b-instruct",

        # model="qwen-plus-latest",
        # model="qwen3-235b-a22b",
        # model="qwen3-30b-a3b",
        # model="qwen3-32b",

        # max_tokens=1,
        max_tokens=None,

        messages=[
            {
                'role': 'user',
                # 'content': '今天南京天气',
                # 'content': "9.8 9.11哪个大",
                # 'content': 'https://oss.ffire.cc/files/AIGC.pdf 总结下',
                'content': ' 总结下',

                # "chat_type": "search", deep_research

                # 'content': user_content,

                # "content": [
                #     {
                #         "type": "text",
                #         "text": "总结下",
                #         "chat_type": "t2t",
                #         "feature_config": {
                #             "thinking_enabled": False
                #         }
                #     },
                #     {
                #         "type": "file",
                #         "file": "2d677df1-45b2-4f30-829f-0d42b2b07136"
                #     }
                # ]

                # "content": [
                #     {
                #         "type": "text",
                #         "text": "总结下",
                #         "chat_type": "t2t",
                #         "feature_config": {
                #             "thinking_enabled": False
                #         }
                #     },
                #     {
                #         "type": "file_url",
                #         "file_url": {
                #           "url": 'xxxxxxx'
                #         }
                #     }
                # ]
                # "content": [
                #     {
                #         "type": "text",
                #         "text": "总结下",
                #         # "chat_type": "t2t"
                #
                #     },
                # {
                #     "type": "image",
                #     "image": "703dabac-b0d9-4357-8a85-75b9456df1dd"
                # },
                # {
                #     "type": "image",
                #     "image": "https://oss.ffire.cc/files/kling_watermark.png"
                #
                # }
                # ]

            },

        ],
        # stream=True,

        # reasoning_effort="low",
        enable_thinking=True,
        thinking_budget=1024,
        # stream_options={"include_usage": True},

    )
    token = None

    # token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjMxMGNiZGFmLTM3NTQtNDYxYy1hM2ZmLTllYzgwMDUzMjljOSIsImV4cCI6MTc0ODQ3OTE0M30.oAIE1K0XA0YYqlxB8Su-u0UJbY_BBZa4_tvZpFJKxGY"

    arun(create(request, token))

    # arun(to_file("https://oss.ffire.cc/files/kling_watermark.png", token))
