# DDNet Gores 地图包

[中文](README.md) | [English](README.en.md)

该仓库包含了个人收集的 gores 地图。

> metadata 可能不是 100% 准确。

## 内容

- `maps/`
  按难度分层的原始 `.map` 地图文件。
- `maplists/`
  按难度分类的 JSON 列表文件。
- `metadata/all-metadata.json`
  汇总后的全部地图元信息。
- `metadata/stats.json`
  各难度地图数量统计。

## 目录结构规范

本仓库已经把 `maps/` 从单个大目录迁移为按难度分层的目录，同时保持 vote 菜单只显示地图基础名。例如 `maps/insane/example.map` 在游戏内仍显示为 `example`，不会显示为 `insane/example`。

校验入口：

```bash
./scripts/validate_mappack.py
```

按需同步属于游戏服仓职责，由 `ddnet-spacegores/ops/scripts/sync_mappack.sh`
在子服 agent 收到中心 dashboard 指令后执行。

详见：

- [难度目录与子服同步规范](docs/difficulty-layout-and-sync.md)

## 统计

- 地图总数：`1172`
- 极限：`89`
- 疯狂：`280`
- 困难：`337`
- 普通：`347`
- 简单：`34`
- 模组：`43`
- 单人：`42`
