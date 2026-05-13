# yixiu-analysis — 游戏行业与投资分析

基于雪球博主**逸修1**（2017-2026）知识体系构建的项目，包含 **Claude Code Skill** + **修佬说 Web 应用**。

- **Skill**：在 Claude Code 中调用 `/yixiu-analysis`，自动检索知识库并以逸修视角分析问题
- **Web 应用**：独立部署的聊天对话服务，用户通过浏览器与逸修知识体系对话

> 修佬说在线地址：https://xiulao-shuo.onrender.com

## 功能

- **游戏行业分析**：游戏公司 vs 游戏平台的商业模式差异、产品矩阵思维、长线运营能力评估
- **TapTap 平台分析**：tap+adn+pc+mk 组合逻辑、收入增长驱动、利润率结构
- **财报深度拆解**：通过少数股东权益反推业务利润、识别会计处理影响、季度环比分析
- **估值方法**：游戏公司估值基准、利润质量评估、成长性分析
- **投资决策框架**：基本面驱动、预期管理（悲观/中性/乐观三情景）、错误修正机制
- **AI 与游戏行业**：tap maker 的意义、ADN 业务模式、AI 时代的平台价值

## 与普通 Skill 的区别

本项目不仅包含分析框架（SKILL.md），还内置了一个**可检索帖文知识库**：来自雪球数据库（E:/project/xueqiu/xueqiu_stock.db），包含逸修1原始帖文约1270篇 + 专栏文章约90篇。Skill 和 Web 应用均通过 `knowledge/search_kb.py` 实时检索并融入回复。

## 安装

### 1. 克隆仓库

```bash
git clone https://github.com/as167888/yixiu-analysis-skill.git
cd yixiu-analysis-skill
```

### 2. 安装 Skill

**macOS / Linux：**
```bash
mkdir -p ~/.claude/skills/yixiu-analysis
cp SKILL.md ~/.claude/skills/yixiu-analysis/
```

**Windows（PowerShell）：**
```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills\yixiu-analysis"
Copy-Item SKILL.md "$env:USERPROFILE\.claude\skills\yixiu-analysis\"
```

### 3. 配置知识库路径

SKILL.md 中知识库检索命令的路径默认为项目根目录。如果你克隆到不同位置，请编辑 `~/.claude/skills/yixiu-analysis/SKILL.md`，将 `E:/project/yixiu1/knowledge/search_kb.py` 替换为你实际的路径。

### 4. 添加权限（可选）

在项目的 `.claude/settings.local.json` 中添加知识库搜索命令，避免每次手动确认：

```json
{
  "permissions": {
    "allow": [
      "Bash(python <你的路径>/knowledge/search_kb.py *)"
    ]
  }
}
```

### 5. 重启 Claude Code

## 使用方式

安装后，在 Claude Code 中输入：

```
/yixiu-analysis 分析一下心动公司的 TapTap 业务
```

```
/yixiu-analysis 对心动小镇 2026 年流水怎么看？
```

```
/yixiu-analysis 游戏公司和游戏平台的商业模式有什么本质区别？
```

回答时会自动：
1. 先搜索知识库中相关帖文
2. 引用帖文日期和关键观点
3. 结合分析框架给出结构化答案
4. 对涉及具体数字的问题，会交叉验证最近帖文是否有修正

## 项目结构

```
yixiu-analysis-skill/
├── SKILL.md                              # Claude Code skill 定义（分析框架 + 检索指令）
├── main.py                               # 交互式管理主程序（启动入口）
├── knowledge/
│   └── search_kb.py                      # 帖文知识库检索脚本
├── web_app/                              # 修佬说 Web 应用
│   ├── main.py                           # FastAPI 后端（SSE 流式、DeepSeek API）
│   ├── search_engine.py                  # 知识库检索引擎（可独立 import）
│   ├── prompt_builder.py                 # System prompt 构建器
│   ├── static/
│   │   └── index.html                    # 聊天 UI（暗色主题、Markdown 渲染）
│   ├── data/
│   │   └── xueqiu_stock.db               # SQLite 知识库（Docker 构建时嵌入）
│   ├── Dockerfile                        # Docker 镜像定义
│   ├── requirements.txt                  # Python 依赖
│   └── .env.example                      # 环境变量模板
├── render.yaml                           # Render.com 部署配置
├── examples/
│   ├── 心动公司深度分析报告.md
│   └── 美团深度分析报告.md
└── README.md
```

数据源：雪球数据库 E:/project/xueqiu/xueqiu_stock.db
- user_posts：逸修1 帖文（约1270篇，2017-2026）
- column_articles：逸修1 专栏文章（约90篇）
- 不读取 stock_posts（心动公司个股卡页贴文）

## 修佬说 Web 应用

独立的聊天对话应用，用户输入问题后，后端自动检索知识库并结合 DeepSeek API，以逸修的语气和知识体系生成回复。

### 技术栈

- **后端**：FastAPI + SSE 流式响应
- **AI**：DeepSeek v4-pro（reasoning + thinking mode）
- **知识库**：SQLite 全文检索（与 Skill 共用同一数据源）
- **前端**：纯 HTML/CSS/JS（marked.js 渲染 Markdown）
- **部署**：Docker + Render.com

### 本地启动

```bash
cd web_app
pip install -r requirements.txt
set DEEPSEEK_API_KEY=your-api-key
uvicorn main:app --reload
# 打开 http://localhost:8000
```

### 部署

通过 `render.yaml` 在 Render.com 一键部署：
1. 连接 GitHub 仓库到 Render Dashboard
2. Blueprint → New Blueprint → 选择本仓库
3. 设置环境变量 `DEEPSEEK_API_KEY`
4. 自动构建并上线

每次 push 到 master 自动触发更新部署。

## 知识库检索

`knowledge/search_kb.py` 从雪球数据库实时检索，支持：
- 中文关键词搜索（含 bigram 分词）
- 短语匹配加分
- 时间衰减排序（新帖优先）
- `--silent` 模式输出 JSON，供 skill 内部调用
- `--stats` 查看数据库统计信息

```bash
# 静默检索
python knowledge/search_kb.py "心动公司 TapTap ADN 估值" 5 --silent

# 查看数据库统计
python knowledge/search_kb.py --stats

# 启动交互式管理程序
python main.py
```

## 示例报告

`examples/` 目录下包含使用本 skill 生成的完整研究报告。

### 心动公司深度分析报告

逸修1的核心研究标的，包括 TapTap 平台质变逻辑、tap+adn+pc+mk 组合、游戏业务矩阵、组织能力蜕变分析。

### 美团深度分析报告

展示将逸修1的分析框架迁移到其他公司的效果（本地生活 vs 游戏行业）。

## 知识来源

- **贴文**：2017-2026 年间约 3900 篇雪球帖文
- **专栏文章**：约 90 篇深度分析文章

核心覆盖领域：心动公司（02400.HK）、TapTap 平台、游戏行业投资方法论、港股中概互联。

## 知识时效性

skill 中的**分析框架和方法论**具有长期价值，知识库中的帖文支持按时间衰减排序检索。具体财务数据基于截至 2026 年 5 月的信息，使用时请结合最新财报自行判断。

## 免责声明

- 本 skill 基于公开内容蒸馏，仅供学习和研究使用
- 不构成任何投资建议
- 投资有风险，决策需谨慎
- 本项目与逸修1本人无关联，如有侵权请提 Issue

## License

MIT
