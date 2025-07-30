# nonebot-plugin-vv

基于 NoneBot2 的维维语录搜索插件，支持通过命令或引用消息快速检索维维语录，并返回相似语录及视频截图。

## 介绍

- 支持通过命令 `vv [语录内容]` 搜索维维语录
- 支持回复消息直接搜索
- 返回相似度、匹配比例、截图等详细信息
- 群聊自动以合并转发形式展示结果

## 安装

使用nb-cli安装插件

```shell
nb plugin install nonebot_plugin_vv
```

使用pip安装插件

```shell
pip install nonebot_plugin_vv
```

## 使用

- `vv [内容]`：搜索与内容相关的维维语录
- 引用消息并发送 `vv`：搜索被回复消息的内容

## 配置

无需额外配置，开箱即用。

## 相关链接

- [项目主页](https://github.com/StillMisty/nonebot_plugin_vv)
- [NoneBot2 文档](https://v2.nonebot.dev/)
- [VV](https://github.com/Cicada000/VV)

## 协议

[Apache-2.0](LICENSE)
