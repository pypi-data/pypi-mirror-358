from nonebot import require
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    MessageEvent,
)

from .utils import (
    fetch_vv_list,
    structure_forward_msg,
)

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import (  # noqa: E402
    Alconna,
    Args,
    CommandMeta,
    Match,
    Option,
    on_alconna,
)

vv = on_alconna(
    Alconna(
        "vv",
        Option("content", Args["content", str]),
        meta=CommandMeta(
            compact=True,
            description="搜索vv语录",
            usage="vv [语录内容]",
        ),
    ),
    priority=5,
    block=True,
)


@vv.handle()
async def handle_vv(bot: Bot, event: MessageEvent, content: Match[str]):
    content_get = None
    if (
        hasattr(event, "reply")
        and event.reply
        and getattr(event.reply, "message", None)
    ):
        # 获取被回复消息的内容
        content_get = str(event.reply.message).strip()
    elif content.available:
        # 获取命令参数中的内容
        content_get = content.result.strip()

    if not content_get:
        await vv.finish("请输入要搜索的维维语录，或回复一条消息进行搜索")

    vvItems = await fetch_vv_list(content_get)
    nodes = await structure_forward_msg(vvItems)

    if isinstance(event, GroupMessageEvent):
        await bot.send_group_forward_msg(
            group_id=event.group_id,
            message=nodes,
        )
    else:
        await bot.send_private_forward_msg(
            user_id=event.user_id,
            message=nodes,
        )
