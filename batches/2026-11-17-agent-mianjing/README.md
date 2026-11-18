# 批次 2026-11-17-agent-mianjing

关键词「Agent 面经」的小红书面经采集批次。

## 统计

| 口径 | 数量 |
|---|---|
| 可见笔记 | 425 |
| 标题排除 | 184（营销79 / 非Agent方向40 / 剧情日常39 / AI生成合集26，含13条人工改判） |
| 保留待复核（本批未读正文） | 196 |
| 内容复核 | 45（Top40点赞 + 5空标题） |
| 复核通过（题源） | 23（含1对转载重复已合并） |
| 复核排除 | 14 |
| 采集失败 | 7（正文1 / 图片6） |
| 画面提取 | 8 篇 / 49 图 |
| 裸题候选 | 423 |

### 编题入库（build 阶段，2026-11-17）

| 口径 | 数量 |
|---|---|
| 入库题目 | 40（low 3 / medium 21 / high 16；agent-architecture 12、agent-engineering 6、evaluation-reliability 6、rag-retrieval 5、agent-performance 4、model-adaptation 4、agent-cost 1、data-governance 1、agent-learning 1；含场景设计题） |
| 候选并入库 | 153（含主源与追问维度并入） |
| 判重并入已有题 | 35（duplicate_of） |
| 拒绝（非教学价值） | 88（自我介绍/项目叙述/软素质 50、项目强绑定 14、通用八股 12、纯手撕 13，四维计分记于 reason） |
| 留待后续批次 | 147（pending，框架族细节、后端工程题、场景设计题等） |
| 独立审核 | 8 个独立审核 Agent 分批审核，40 份审核记录（reviews/content-Q001..Q040.json），多题经 round-2 复审 |

## 目录

- `manifest.json` — 批次清单与统计（45 篇复核笔记的状态、理由、公司/岗位/轮次、产出题目）
- `candidates.json` — **交接产物**：423 条裸题候选，状态全部 `pending`，待 build-interview-bank 编题入库
- `screening_log.md` — 筛选过程日志（初筛规则、人工改判、复核结论、失败记录）
- `cards_frozen.json` / `cards_screened.json` — 冻结清单（425）与标题初筛结果（逐条状态与理由）
- `details_collected.json` / `image_downloads.json` / `img_state_results.json` — 采集中间记录
- `notes/<note_id>/` — 每篇笔记：`note.json`（正文快照与元数据）、`images/`（原图 webp）、`image-extract.md`（画面提取，远程视觉模型逐图转写，用户 2026-11-17 批准）
- `reviews/` — 编题阶段写入：40 份独立审核记录（content-Q001..Q040.json，含 SHA-256 与逐维评语）
- `mianjing/` — **面经原文版（教研侧）**：每篇笔记按原帖顺序完整保留全部题目并标注题库去向，附按公司汇总的索引（`mianjing/README.md`）

## 说明

- 公司/岗位/轮次一律为发帖人自述，未推断核实；值为空记 `unspecified`。
- 7 篇采集失败（正文 1 篇、图片 6 篇）已如实记录，未做猜测性补录；196 篇 `retained_deferred` 留待后续批次复核。
- 转载重复：6ae07d4b 与 6adf46d4 为同一面经，题面合并至 6adf46d4。
- 编题阶段说明：题目 provenance 的公司/岗位/轮次一律以 note.json 为准；个别候选在 candidates.json 中的 round（如字节帖记「一面」）与 note.json（「三轮技术面+HR面（2-2）」）不一致，系采集期初记差异，不改采集原档。
- 留待后续批次的 147 条 pending 候选以框架族细节（LangChain/LangGraph）、后端工程题（消息队列/限流/会话状态/异步）、剩余场景设计题（会议转写 Skill、游戏 NPC、平台从 0 到 1、状态机幂等等）为主。
