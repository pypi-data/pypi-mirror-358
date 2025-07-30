import asyncio
import json
import re
from typing import TypedDict

import httpx
from nonebot.adapters.onebot.v11 import MessageSegment
from nonebot.log import logger


class VVItem(TypedDict):
    """
    用于描述 VV 接口返回的每一项数据。
    """

    filename: str  # 文件名
    timestamp: str  # 时间戳
    similarity: float  # 相似度
    text: str  # 匹配到的文本
    match_ratio: float  # 匹配比例
    exact_match: bool  # 是否完全匹配


async def fetch_vv_list(query: str) -> list[VVItem]:
    """
    根据查询内容从 VV 接口获取匹配结果列表。

    :param query: 查询字符串
    :return: 包含每一项结果的 VVItem 字典列表
    """
    search_url = r"https://vvapi.cicada000.work/search"

    async with httpx.AsyncClient() as client:
        params = {
            "query": query,  # 搜索内容
            "max_results": 4,  # 返回的结果最多的个数
            "min_ratio": 0.5,  # 关键词在句子中的最小匹配度
            "min_similarity": 0.5,  # 最小的人脸识别匹配度，一般认为0.5以上为VV
        }

        response = await client.get(search_url, params=params)
        response.raise_for_status()
        # 将返回的多行 JSON 字符串转为列表
        return [json.loads(line) for line in response.text.strip().splitlines()]


async def fetch_vv_img_preview(item: VVItem) -> str | bytes:
    """
    获取 VVItem 的图片预览链接。

    :param item: VVItem 对象
    :return: 图片预览的字节内容，如果无法获取则返回 None
    """
    # 假设图片链接是通过文件名生成的
    preview_bash_url = r"https://vv-indol.vercel.app/api/preview"
    episode_match = re.search(r"\[P(\d+)\]", item["filename"])
    time_match = re.search(r"^(\d+)m(\d+)s$", item["timestamp"])
    if not episode_match or not time_match:
        return "无法获取到图片预览"

    episode = episode_match.group(1)
    minutes, seconds = time_match.group(1, 2)
    total_seconds = int(minutes) * 60 + int(seconds)
    preview_url = f"{preview_bash_url}/{episode}/{total_seconds}"

    async with httpx.AsyncClient() as client:
        response = await client.get(preview_url)
        if response.status_code != 200:
            logger.error(f"获取图片预览失败: {response.status_code} - {response.text}")
            return "无法获取到图片预览"
        return response.content


def structure_node(message: list[MessageSegment]) -> dict:
    return {
        "type": "node",
        "data": {
            "content": message,
        },
    }


async def structure_forward_msg(vvItems: list[VVItem]) -> list:
    async def build_node(item: VVItem):
        msg = MessageSegment.text(
            f"匹配文本: {item['text']}\n"
            f"视频名: {item['filename']}\n"
            f"时间戳: {item['timestamp']}\n"
            f"维维相似度: {item['similarity']:.2f}\n"
            f"匹配比例: {item['match_ratio']:.2f}\n"
            f"完全匹配: {'是' if item['exact_match'] else '否'}\n"
        )
        preview = await fetch_vv_img_preview(item)
        if isinstance(preview, str):
            return structure_node([msg, MessageSegment.text(preview)])
        else:
            return structure_node([msg, MessageSegment.image(preview)])

    tasks = [build_node(item) for item in vvItems]
    return await asyncio.gather(*tasks)


if __name__ == "__main__":
    # 测试
    import asyncio

    async def main():
        results = await fetch_vv_list("测试")
        print(results[0])
        await fetch_vv_img_preview(results[0])

    asyncio.run(main())
