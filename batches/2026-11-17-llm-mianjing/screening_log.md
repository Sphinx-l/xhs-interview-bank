# 筛选日志 · 批次 2026-11-17-llm-mianjing

关键词「大模型面试」，搜索结果滚动到底（页面高度 151725px 不再增长），冻结 974 张唯一卡片（`cards_frozen.json`，含 xsec_token 链接 `href_map.json`）。与旧批次（2026-11-16 / 2026-11-17-agent-mianjing）note_id 重合 10 张。

## 标题初筛（cards_screened.json）

规则（正则 + 人工抽查）：

- `excluded_marketing`（141）：背完/通过率/八股文/资料/押题/一次性整理/高频题/必问/必考/速记/存下吧/刷完/题单/答案解析类标题。
- `excluded_non_agent` / `excluded_story`：沿用上一批口径（本批自动排除 4 + 53，多含在 marketing 规则里）。
- `review_candidate`（598）：标题含真实面经信号（面经/一面/二面/凉经/已offer/全过程/被问/问到）或具体公司名。
- `retained_empty_title`（19）：空标题待内容复核。
- `retained_deferred`（216）：弱信号，留待后续批次。

复核顺序：面经信号强的优先（chunk 01-08），公司名信号次之，空标题最后。

## 内容复核

- 逐篇打开带 xsec_token 的详情页，抽取标题/正文/作者/日期/图片/评论（`_chunk_NN_result.json` → 汇总 `details_collected.json`）。
- 发现：部分笔记正文只有话题标签，题面在图片或评论区；首轮选择器漏抓，二轮补采（轮播翻页收图，_refetch_result.json）。

## 内容复核结论（2026-11-18 完成）

617 篇复核笔记逐篇判定（自动规则 + 人工逐条改判，见 manifest.json）：

- `retained` 160：正文含题面 76 + 题面在图片 84（待画面提取）。图片 URL 已通过轮播翻页全部抓取（_refetch_result.json）。
- `excluded` 396：营销卖课/AI 生成合集、方法论/备考杂谈、非技术方向（含按 2026-11-18 用户范围规则排除的 AI 产品经理/运营岗）、前端/Java 八股岗、叙事无题面。
- `duplicate_repost` 3：字节 TikTok Agent 一面同题面四帖（6a7dc3af / 6a75b222 / 6a7704fc / 6a75b23e），题源合并至 6a7dc3af。
- `fetch_failed` 43：正文与图片均未取到（部分为评论区补面经、部分图片加载失败），标题为真实面经，留待后续批次重试。
- `out_of_scope_video` 15：视频笔记。

人工改判要点：

1. **AI 生成模板假面经**：淘天（69bb6bac）与携程（6a323ec1）「AI Agent 12 题」Q1-Q12 完全同文、仅换公司名，判定教学号批量产出，均排除。
2. **教学号合集 vs 真实面经**：按考频整理/高频题清单/「整理成清单查漏补缺」类排除；带具体公司+轮次+日期的逐题帖保留。
3. **范围规则**（用户 2026-11-18）：AI 产品经理/产品运营等非技术岗面经不采。
4. 评论区加载失败（独立详情页评论容器选择器未命中），题面在评论的笔记按实际取到的内容判定，未猜测补录。

## 裸题候选

- 从 76 篇正文题面笔记提取 928 条裸题候选（candidates.json，extraction=note_text，全部 pending）。
- 图片题面 84 篇的画面提取（视觉读题）与 43 篇 fetch_failed 的重试留待下一阶段。
