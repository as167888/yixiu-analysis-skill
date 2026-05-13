"""逸修知识库检索引擎 - 从 SQLite 数据库搜索帖文和专栏文章"""

import math
import re
import os
import sqlite3
from datetime import datetime

DB_FILE = os.path.join(os.path.dirname(__file__), "data", "xueqiu_stock.db")

STOP_WORDS = set(
    "的了吗呢吧啊是和在有不这也人被为对会可以及或但而因所以如果虽然然而从到上去下来着之说看让把向与及及其不都就也还只"
)

REFERENCE_DATE = datetime(2026, 5, 7)


def _clean_html(text):
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\{[^}]*\}", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _extract_snippet(text, query_terms, window=200):
    text_clean = _clean_html(text)
    best_pos = -1
    best_score = 0
    query_lower = [t.lower() for t in query_terms]

    for term in query_lower:
        pos = text_clean.lower().find(term)
        if pos == -1:
            continue
        scope = text_clean[max(0, pos - window) : pos + window].lower()
        score = sum(1 for t in query_lower if t in scope)
        if score > best_score:
            best_score = score
            best_pos = pos

    if best_pos == -1:
        return text_clean[: window * 2]

    start = max(0, best_pos - window)
    end = min(len(text_clean), best_pos + window)
    snippet = text_clean[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text_clean):
        snippet += "..."
    return snippet


def _parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def _recency_boost(post_date_str, half_life_days=365):
    dt = _parse_date(post_date_str)
    if dt is None:
        return 0.0
    days_ago = (REFERENCE_DATE - dt).days
    if days_ago < 0:
        days_ago = 0
    return 2.0 * (0.5 ** (days_ago / half_life_days))


def _load_posts():
    """从数据库加载逸修帖文和专栏文章（不读取个股卡页贴文）"""
    if not os.path.exists(DB_FILE):
        return []

    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    posts = []

    cursor.execute(
        "SELECT id, created_at, text FROM user_posts WHERE text IS NOT NULL AND text != ''"
    )
    for row in cursor.fetchall():
        posts.append(
            {"id": row[0], "created_at": row[1] or "", "text": row[2], "source": "post"}
        )

    cursor.execute(
        "SELECT id, created_at, title, text FROM column_articles WHERE text IS NOT NULL AND text != ''"
    )
    for row in cursor.fetchall():
        title = row[2] or ""
        text = row[3] or ""
        posts.append(
            {
                "id": row[0],
                "created_at": row[1] or "",
                "text": title + " " + text,
                "source": "column",
            }
        )

    conn.close()
    return posts


def search(query: str, top_n: int = 8) -> list[dict]:
    """搜索知识库，返回 top_n 条最相关的结果"""
    data = _load_posts()
    if not data:
        return []

    query_terms = [t for t in query.strip().split() if t not in STOP_WORDS]
    if not query_terms:
        return []

    chinese_query = "".join(re.findall(r"[一-鿿]+", query))
    if chinese_query:
        for i in range(len(chinese_query) - 1):
            bigram = chinese_query[i : i + 2]
            if bigram not in query_terms:
                query_terms.append(bigram)

    scored = []
    for post in data:
        text = post.get("text", "")
        if not text:
            continue
        text_clean = _clean_html(text)
        text_lower = text_clean.lower()

        score = 0.0
        matched = False
        for term in query_terms:
            term_lower = term.lower()
            count = text_lower.count(term_lower)
            if count > 0:
                matched = True
                score += 1.0 + math.log(1 + count)

        if not matched:
            continue

        if query.strip().lower() in text_lower:
            score += 5.0

        score = score / (1 + math.log(1 + len(text_clean) / 500))
        score += _recency_boost(post.get("created_at", ""))
        scored.append((score, post, text_clean))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, post, text_clean in scored[:top_n]:
        snippet = _extract_snippet(post["text"], query_terms)
        results.append(
            {
                "id": post.get("id"),
                "created_at": post.get("created_at", ""),
                "source": "专栏" if post.get("source") == "column" else "帖文",
                "score": round(score, 2),
                "snippet": snippet,
                "text": post.get("text", ""),
            }
        )
    return results


def search_multiple(queries: list[str], top_n_per_query: int = 5) -> list[dict]:
    """多关键词搜索，合并去重按分数排序"""
    seen = set()
    all_results = []
    for q in queries:
        for r in search(q, top_n_per_query):
            if r["id"] not in seen:
                seen.add(r["id"])
                all_results.append(r)
    all_results.sort(key=lambda x: x["score"], reverse=True)
    return all_results[: 2 * top_n_per_query]


def format_results_for_prompt(results: list[dict]) -> str:
    """将搜索结果格式化为可注入 system prompt 的文本（自然融入，不做编号引用）"""
    if not results:
        return "（知识库中未找到相关内容）"

    lines = []
    for i, r in enumerate(results, 1):
        date_str = r["created_at"][:10] if r["created_at"] else "未知日期"
        snippet_clean = r["snippet"].replace("$心动公司(02400)$", "心动公司").replace("$", "")
        lines.append(f"--- 参考观点 {i} ({date_str}) ---")
        lines.append(snippet_clean)
        lines.append("")
    return "\n".join(lines)
