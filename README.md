# IELTS Writing Trainer · 雅思写作训练 Skill

面向 AI coding agents 的雅思写作教练。支持 **Academic / General Training** 的 Task 1 与 Task 2：审题、基于证据的四维估分、逐句讲解、自行修改、示范作文、复练和本地记录。

> **成绩声明**：本项目仅提供非官方训练估分；没有获得 IELTS 官方认证，也不保证模型评估与考官一致或保证提分。

## 核心功能

| 场景 | 行为 |
| --- | --- |
| 只有题目 | 拆解要求、审题与提纲，不替用户假设正文 |
| 题目 + 原稿 | 检查 TR/TA、CC、LR、GRA；引用真实原句、识别优先改进项 |
| 正常训练 | 先让学习者尝试修改，再反馈答案和迁移练习 |
| 要求完整精批/范文 | 跳过等待，提供局部改写和独立标记的示范范文 |
| Task 1 图表 | 必须看到图表才能确认 overview、数据和关键趋势 |
| Word 文档 | 按环境可用文档工具做真实批注与验证，缺能力时说明限制 |
| 复练 | 区分独立稿、修改稿、AI 辅助稿及示范稿；不虚构长期成绩 |

四维评分依据：<https://ielts.org/take-a-test/your-results/ielts-scoring-in-detail>。

## 安装

将仓库下载并把整个文件夹放到 Agent 对应的 Skill 目录。注意保留 `references/` 和 `agents/`。

```bash
git clone https://github.com/tsuntungngaing-jtn/ielts-writing-trainer.git
```

常见目录：

- Cursor 项目级：`.cursor/skills/ielts-writing-trainer/`
- Codex：`~/.codex/skills/ielts-writing-trainer/`
- Claude Code：`~/.claude/skills/ielts-writing-trainer/`

使用前检查你的 Agent 版本支持 Skill 文件夹及 `SKILL.md`；不同环境的触发方式可能不同。使用本项目不需要额外注册 IELTS 评分账号。

## 使用示例

**基础评测**

> 使用 ielts-writing-trainer 帮我批改 IELTS Academic Task 2。先按四项标准分析我原文中的证据，给估分区间和最值得先改的三个问题。题目：[粘贴题目]；原文：[粘贴作文]。

**独立训练**

> 我想先自己改，请只给 3 个关键问题与提示，不要提前泄露改写答案。

**直接精批**

> 直接精批全文，给原句—建议—理由对照，再给一篇保留我立场的目标 Band 8.0 示例作文。请明确区分我的表现和 AI 范文。

**Task 1**

> 请先读取我上传的图表，再核对 overview、数据与比较；如果看不到图表，不要推测数值或给 TA 综合分。

## 目录

```text
SKILL.md                      # 入口与交互流程
agents/openai.yaml            # Agent 展示信息
references/assessment.md      # 官方标准、评分边界
references/model-essays.md    # 局部改写与范文策略
references/docx.md            # Word 批注流程与限制
references/practice.md        # 专项复练和真实记录
references/evaluation.md      # 质量评测与校准方案
references/sources.md         # 来源和设计参考
evals/behavioral_cases.json   # 人工验收案例（原创模拟）
evals/example_feedback.json   # 可自动验证的结构化报告示例
scripts/validate_feedback.py  # 结构和引用一致性检查（标准库）
tests/                       # 本地回归测试
.github/workflows/quality.yml # GitHub Actions 自动运行测试
```

## 自动化检查（可选）

训练对话仍然使用自然语言；只有需要测试时，才让 Agent 按 `references/evaluation.md` 的 JSON 字段输出评测副本：

```bash
python scripts/validate_feedback.py evals/example_feedback.json
python -m unittest discover -s tests -v
```

**检查器能做什么**：检查估分字段、半分网格、证据引用是否出现在学生原文、是否缺少题目/图表仍给了任务分、改进项是否包含可执行动作。

**检查器不能做什么**：判断作文内容是否真的切题、图表数据是否准确、某分数与真实考官差距多大。需要独立人工核对与官方公开样本校准。`evals/behavioral_cases.json` 是测试计划，不是“模型已经通过”的成绩报告。

## 数据与版权

- 作文默认不发送到额外的第三方批改服务；但使用云端 AI Agent 时，文本仍受该 Agent 提供商的数据处理规则约束。
- 本地记录仅在实际训练及运行环境允许写入时建立，详情见 `references/practice.md`。
- 不打包剑桥雅思真题、官方评分全文或第三方仓库的代码与完整提示词。
- 第三方项目仅作为设计参考，具体列于 `references/sources.md`。