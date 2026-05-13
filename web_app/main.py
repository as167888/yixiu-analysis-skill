"""修佬说 - FastAPI 后端服务"""

import json
import re
import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from openai import OpenAI

from search_engine import search_multiple, format_results_for_prompt
from prompt_builder import build_system_prompt, build_user_prompt

app = FastAPI(title="修佬说", description="基于逸修1知识体系的游戏行业投资分析AI助手")

# 挂载静态文件目录
static_dir = Path(__file__).parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# DeepSeek API 客户端
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-v4-pro"

if DEEPSEEK_API_KEY:
    client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)
else:
    client = None


def _extract_keywords(text: str) -> list[str]:
    """从用户消息中提取搜索关键词"""
    keywords = []

    # 公司名
    companies = {
        "心动": "心动公司",
        "腾讯": "腾讯",
        "网易": "网易",
        "米哈游": "米哈游",
        "哔哩哔哩": "哔哩哔哩",
        "b站": "哔哩哔哩",
        "B站": "哔哩哔哩",
        "美团": "美团",
        "三七": "三七互娱",
        "吉比特": "吉比特",
        "完美": "完美世界",
        "巨人": "巨人网络",
        "金山": "金山软件",
        "汇量": "汇量科技",
    }
    for name, kw in companies.items():
        if name in text:
            keywords.append(kw)

    # 产品名
    products = {
        "taptap": "TapTap",
        "TapTap": "TapTap",
        "tap": "TapTap",
        "小镇": "小镇",
        "火炬": "火炬之光",
        "麦芬": "麦芬",
        "香肠": "香肠派对",
        "铃兰": "铃兰之剑",
        "伊瑟": "伊瑟",
        "ro": "RO",
        "RO": "RO",
        "异环": "异环",
    }
    for name, kw in products.items():
        if name in text:
            keywords.append(kw)

    # 概念
    concepts = {
        "adn": "ADN",
        "ADN": "ADN",
        "估值": "估值",
        "财报": "财报",
        "利润率": "利润率",
        "利润": "利润",
        "pe": "PE",
        "PE": "PE",
        "pc版": "PC版",
        "PC": "PC版",
        "tap maker": "tap maker",
        "dirichlet": "dirichlet",
        "股价": "股价",
        "大跌": "大跌",
        "流水": "流水",
        "营收": "收入",
        "收入": "收入",
        "少数股东": "少数股东权益",
        "回购": "回购",
        "港股通": "港股通",
        "机构": "机构",
    }
    for name, kw in concepts.items():
        if name in text:
            keywords.append(kw)

    # 如果提到了"怎么看"、"分析"等，加上通用关键词
    analysis_triggers = ["怎么看", "分析", "如何看", "点评", "评价", "如何理解"]
    if any(t in text for t in analysis_triggers):
        # 用整个问题文本做一次搜索
        pass

    # 去重
    seen = set()
    unique = []
    for k in keywords:
        if k not in seen:
            seen.add(k)
            unique.append(k)

    return unique


def _search_knowledge_base(user_message: str) -> str:
    """搜索知识库并返回格式化的文本"""
    keywords = _extract_keywords(user_message)

    # 至少用原始消息中的核心词搜索
    if not keywords:
        # 提取中文关键词作为fallback
        chinese = re.findall(r"[一-鿿]+", user_message)
        if chinese:
            keywords = [user_message]  # 直接用整句搜索

    if not keywords:
        return "（未触发知识库检索）"

    # 多个关键词组合搜索
    if len(keywords) >= 3:
        # 组合搜索：如 "心动公司 TapTap ADN"
        combined = " ".join(keywords)
        results = search_multiple([combined] + keywords, top_n_per_query=3)
    elif len(keywords) >= 1:
        results = search_multiple(keywords, top_n_per_query=5)
    else:
        results = search_multiple([user_message], top_n_per_query=8)

    # 额外搜索最近3个月的帖文（如果涉及数字相关）
    number_triggers = ["流水", "收入", "利润", "估值", "pe", "PE", "亿", "万", "股价"]
    if any(t in user_message for t in number_triggers):
        for kw in keywords[:2]:
            recent_results = search_multiple([f"{kw} 2026"], top_n_per_query=3)
            for r in recent_results:
                if r["id"] not in {x["id"] for x in results}:
                    results.append(r)

    results.sort(key=lambda x: x["score"], reverse=True)
    return format_results_for_prompt(results[:10])


@app.get("/", response_class=HTMLResponse)
async def index():
    """返回聊天 UI 页面"""
    html_path = static_dir / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>修佬说</h1><p>index.html not found</p>", status_code=404)


@app.post("/api/chat")
async def chat(request: Request):
    """聊天 API - SSE 流式返回"""
    if client is None:
        async def error_stream():
            yield f"data: {json.dumps({'error': 'DeepSeek API key not configured. Set DEEPSEEK_API_KEY environment variable.'})}\n\n"
        return StreamingResponse(error_stream(), media_type="text/event-stream")

    try:
        body = await request.json()
    except Exception:
        # Handle encoding issues (e.g., Windows curl with GBK encoding)
        raw = await request.body()
        body = json.loads(raw.decode("utf-8", errors="replace"))
    user_message = body.get("message", "").strip()
    if not user_message:
        async def empty_stream():
            yield f"data: {json.dumps({'error': 'Empty message'})}\n\n"
        return StreamingResponse(empty_stream(), media_type="text/event-stream")

    # 1. 搜索知识库
    search_results_text = _search_knowledge_base(user_message)

    # 2. 构建 prompts
    system_prompt = build_system_prompt(search_results_text)
    user_prompt = build_user_prompt(user_message)

    # 3. 调用 DeepSeek API (streaming)
    async def stream_response():
        full_text = ""

        try:
            response = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                stream=True,
                reasoning_effort="high",
                extra_body={"thinking": {"type": "enabled"}},
            )

            for chunk in response:
                if chunk.choices and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if delta and delta.content:
                        full_text += delta.content
                        yield f"data: {json.dumps({'content': delta.content})}\n\n"

            # 发送完成信号
            yield f"data: {json.dumps({'done': True, 'search_count': search_results_text.count('[', 1) if search_results_text else 0})}\n\n"

        except Exception as e:
            error_msg = str(e)
            yield f"data: {json.dumps({'error': error_msg})}\n\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")


@app.get("/api/health")
async def health():
    """健康检查"""
    db_exists = (Path(__file__).parent / "data" / "xueqiu_stock.db").exists()
    return {
        "status": "ok",
        "deepseek_configured": client is not None,
        "database_exists": db_exists,
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
