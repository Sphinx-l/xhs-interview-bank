# 虾皮-后端Agent工程师面经2

- 来源：[虾皮-后端Agent工程师面经2](https://www.xiaohongshu.com/explore/6afaf99a000000002a01bd0e)（小红书笔记快照，公司/岗位/轮次为发帖人自述，未核实；直链可能触发风控 404，可站内搜标题定位）
- 公司：虾皮（渠道：实习）｜ 岗位：后端Agent工程师 ｜ 轮次：面经2(轮次未注明)
- 题目 23 条（题目顺序为原帖顺序）

## 正文题面

- 实习面经
- 项目
- 负责什么，什么角色，做出什么贡献？（粗糙提问）
- 手撕1
- 模拟大数据的 MapReduce 工作方式，写两个函数，一个 map，一个 reduce，进行 word counting，统计每个单词的出现频次。
- 按照文章的段落数量（段以一个或者多个换行符分割），启动相应数量的 thread 去调用 map 函数去计算每段中 word count。
- 然后通过 reduce 函数汇总，最后输出。
- 例如，输入如下英文文字：
- This is a short test line.
- This is a long test line , It is designed for the MapReduce problem. and MapReduce should go 3 times in this line, so here goes another MapReduce.
- This is a test line too designed for MapReduce.
- 由于该段文字有三个段落，因此可以启动三个线程，每个线程各自调用 map 统计一个段落。最后将统计数据发送到 reduce 函数中汇总。
- 比如，上述文章中，单词“MapReduce”在第一段出现 0 次，第二代出现 3 次，第三段出现 1 次，那么“MapReduce”一共出现了 4 次。
- 最后汇总后，应输出：
- MapReduce:4
- 依次类推
- This:3
- this:1
- a:3
- ....
- 注：可以将这些字符串写死在代码内，不用输入。
- 手撕2
- 平方根，牛顿二分法，2位小数，python做
