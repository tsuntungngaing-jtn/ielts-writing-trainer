# Evaluation and calibration · 评测验证

本文件说明如何测试 **Skill 输出的可靠性**，而不把静态规范等同于雅思真实评分准确率。官方标准优先于本文件。

## 两层测试

### A. 可自动检查（确定性）

`scripts/validate_feedback.py` 接收一份 JSON 评测副本，校验：
1. 标记为 `unofficial_training_estimate`，不得声称官方认证。
2. 正确使用 `TA`（Task 1）或 `TR`（Task 2），以及 `CC`、`LR`、`GRA`。
3. 估分为空或属于 0–9、0.5 步长；材料不完整时任务分与综合分留空。
4. 有分数的每个维度必须提供 **逐字存在于学生正文** 的引文、判断与改进动作。
5. 改进项至多三个；引用内容必须确实出现在学生正文，且每项有可执行的下一步。
6. 有任何维度未估分，不允许给完整单篇 overall。

限制：这些检查只能排除部分格式错误与虚构原句；**不能验证引文是否足以支撑评价**，也不能评价 IELTS 评分是否正确。

### B. 需要人工评审（行为质量）

运行 `evals/behavioral_cases.json` 的原创模拟案例；用同一模型/设置运行至少两遍。针对每个案例记录：

- 是否正确识别主要问题，且不编造不存在的错误；
- 是否正确处理缺少题目、图表、旧稿等情况；
- 是否保留学生原立场，且不把 AI 范文计入学生进步；
- 是否给出最多三个可执行的改进方向；
- 是否提供可复练的任务，而不是堆砌高级词汇。

人工记录模型版本、日期、案例 ID、重复次数、是否满足每项要求、典型失败；**未实测不得声称通过**。

## 校准到 IELTS Band 的要求

优先使用 IELTS 官方发布、带考官评语且明确分数的公开样本。必须先盲评再查看考官结果；没有公布四维成绩时不能编造四维金标准。至少记录题型、考官可见分数、Skill 估分、差距、版本、日期、限制。样本数量不足时不要宣称 MAE、准确率或“与官方考官一致”。

**评分分档与真实作文质量之间不是简单语法阈值或字数扣分公式。**

## JSON 评测副本协议

仅在用户要求评测/调试时生成 JSON，不改变正常中文批改体验。示例：`evals/example_feedback.json`。

必填字段：
- `task_type`：`academic_task1`、`general_task1`、`task2`。
- `prompt`：完整题目；未知用空字符串。
- `essay`：学生当前原文，不含题目、范文、旧批注。
- `visual_available`：布尔值；仅 Academic Task 1 用于判定图表有无。
- `scores`：维度名到数字或 `null` 的映射，另外含 `overall`。
- `evidence`：记录数组，每项有 `criterion`、`quote`、`finding`、`next_action`；quote 必须为学生原文的连续子串。
- `priorities`：0–3 个对象，每项含 `issue`、`action`；可选 `quote`，存在时须为学生原文子串。
- `score_label`：必须为 `unofficial_training_estimate`。
- `draft_kind`：`independent`、`revision`、`assisted`、`model` 或 `unknown`，不能把 AI 模型稿说成独立成绩。

当缺题目时，相关 TA/TR 与 overall 应为 `null`；Academic Task 1 缺图时同理。允许对可见语言现象单独诊断，但不能用它推断完整写作水平。

## 运行

```bash
python scripts/validate_feedback.py evals/example_feedback.json
python -m unittest discover -s tests -v
```

如果收到无效报告，调整评测输出，不要修改学生原文使其“匹配”伪造的引文。