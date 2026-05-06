# yixiu-analysis — 游戏行业与投资分析 Claude Code Skill

一个用于游戏行业和互联网投资分析的 Claude Code skill，知识体系蒸馏自雪球博主**逸修1**在 2017-2026 年间发布的贴文和专栏文章。

## 能做什么

调用 `/yixiu-analysis` 后，Claude 会以逸修1的分析框架和视角回答问题，包括：

- **游戏行业分析**：游戏公司 vs 游戏平台的商业模式差异、产品矩阵思维、长线运营能力评估
- **TapTap 平台分析**：tap+adn+pc+mk 组合逻辑、收入增长驱动、利润率结构
- **财报深度拆解**：通过少数股东权益反推业务利润、识别会计处理影响、季度环比分析
- **估值方法**：游戏公司估值基准、利润质量评估、成长性分析
- **投资决策框架**：基本面驱动、预期管理（悲观/中性/乐观三情景）、错误修正机制
- **AI 与游戏行业**：tap maker 的意义、ADN 业务模式、AI 时代的平台价值

## 安装

将 `SKILL.md` 复制到 Claude Code 的 skills 目录：

**macOS / Linux：**
```bash
mkdir -p ~/.claude/skills/yixiu-analysis
curl -o ~/.claude/skills/yixiu-analysis/SKILL.md \
  https://raw.githubusercontent.com/as167888/yixiu-analysis-skill/main/SKILL.md
```

**Windows（PowerShell）：**
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\yixiu-analysis"
Invoke-WebRequest -Uri "https://raw.githubusercontent.com/as167888/yixiu-analysis-skill/main/SKILL.md" `
  -OutFile "$env:USERPROFILE\.claude\skills\yixiu-analysis\SKILL.md"
```

**手动安装：**

1. 下载 `SKILL.md`
2. 将文件放到 `~/.claude/skills/yixiu-analysis/SKILL.md`
3. 重启 Claude Code

## 使用方式

安装后，在 Claude Code 中输入：

```
/yixiu-analysis 分析一下心动公司的 TapTap 业务
```

```
/yixiu-analysis 游戏公司和游戏平台的商业模式有什么本质区别？
```

```
/yixiu-analysis 如何通过财报分析一家游戏公司的真实盈利能力？
```

也可以直接提问，Claude 会在相关话题上自动应用这套分析框架。

## 示例报告

`examples/` 目录下包含两篇使用本 skill 生成的完整研究报告，可以直接查看效果。

### [心动公司深度分析报告](examples/心动公司深度分析报告.md)

逸修1的核心研究标的，也是本 skill 知识最深厚的领域。报告覆盖：

- 游戏行业"赢家通吃"误区的破解——为什么 1% 市场份额的游戏公司仍然值得投资
- TapTap 平台从受限安卓平台到 tap+adn+pc+mk 跨端生态的质变逻辑
- 通过少数股东权益反推 tap+adn 业务利润的财报拆解方法
- 2025 年收入 57.6 亿、扣非归母净利润 16.3 亿的财务结构分析
- 2026 年 20-22 亿利润的增长路径与估值区间

> 这篇报告展示了 skill 在其核心覆盖领域的最高水准——逸修1对心动有长达数年的深度跟踪，报告中的数据和判断来自大量一手研究积累。

### [美团深度分析报告](examples/美团深度分析报告.md)

美团并非逸修1的核心研究标的，这篇报告展示的是**将其分析框架迁移到其他公司**的效果。报告覆盖：

- 本地生活赛道的网络效应与"赢家通吃"逻辑（与游戏行业的对比）
- 外卖→到店酒旅→新业务三层商业模式的拆解
- 骑手网络、用户心智、商家生态三重护城河的深度与边界
- 抖音冲击的本质：为什么外卖基本盘安全，但到店业务承压
- AI 对美团的双面影响：调度优化的机会 vs 搜索入口的威胁

> 这篇报告同时说明了 skill 的边界：对于非核心覆盖领域，框架和方法论仍然有效，但数据深度和判断精度不及心动报告。使用时请结合最新财报数据。

## 知识来源

本 skill 的知识体系蒸馏自雪球博主**逸修1**的公开内容：

- **贴文**：2017-2026 年间发布的约 3900 篇帖子
- **专栏文章**：90 篇深度分析文章

核心覆盖领域：心动公司（02400.HK）、TapTap 平台、游戏行业投资方法论、港股中概互联。

> 本 skill 仅蒸馏了公开发布的观点和分析框架，不包含任何原始数据文件。

## 知识时效性

skill 中的**分析框架和方法论**具有长期价值，但**具体财务数据**（利润数字、估值区间等）基于截至 2026 年 5 月的信息，使用时请结合最新财报自行更新。

## 免责声明

- 本 skill 基于公开内容蒸馏，仅供学习和研究使用
- 不构成任何投资建议
- 投资有风险，决策需谨慎
- 本项目与逸修1本人无关联，如有侵权请提 Issue

## License

MIT
