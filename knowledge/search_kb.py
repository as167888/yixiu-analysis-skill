#!/usr/bin/env python
"""逸修知识库检索工具 - 搜索 merged_posts.json 并返回相关帖文"""

import json
import math
import re
import sys
import os
from datetime import datetime

# 强制 UTF-8 输出
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')

KB_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(os.path.dirname(KB_DIR), "merged_posts.json")

# 中文常见停用词
STOP_WORDS = set('的了吗呢吧啊是和在有不这也人被为对会可以及或但而因所以如果虽然然而从到上去下来着之说看让把向与及及其不都就也还只')

def clean_html(text):
    text = re.sub(r'<[^>]+>', '', text)
    text = re.sub(r'\{[^}]*\}', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    """简单分词：空格分隔 + 中文字符级 n-gram"""
    tokens = []
    # 英文/数字词
    words = re.findall(r'[a-zA-Z0-9]+', text)
    tokens.extend(w.lower() for w in words)
    # 中文连续字符 -> 做 bi-gram 和 uni-gram
    chinese_chars = re.findall(r'[一-鿿]+', text)
    for seg in chinese_chars:
        tokens.append(seg)
        # bi-gram
        for i in range(len(seg) - 1):
            tokens.append(seg[i:i+2])
            tokens.append(seg[i])  # uni-gram
    return tokens

def extract_snippet(text, query_terms, window=200):
    text_clean = clean_html(text)
    best_pos = -1
    best_score = 0
    query_lower = [t.lower() for t in query_terms]

    for term in query_lower:
        pos = text_clean.lower().find(term)
        if pos == -1:
            continue
        score = sum(1 for t in query_lower if t in text_clean[max(0, pos - window):pos + window].lower())
        if score > best_score:
            best_score = score
            best_pos = pos

    if best_pos == -1:
        return text_clean[:window * 2], False

    start = max(0, best_pos - window)
    end = min(len(text_clean), best_pos + window)
    snippet = text_clean[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(text_clean):
        snippet += "..."
    return snippet, True

REFERENCE_DATE = datetime(2026, 5, 7)  # 知识库参考日期，可按需调整

def parse_date(date_str):
    """解析日期字符串，失败返回 None"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str[:10], "%Y-%m-%d")
    except (ValueError, TypeError):
        return None

def recency_boost(post_date_str, half_life_days=365):
    """时间衰减加分：越新的帖文加分越多，半衰期默认 1 年"""
    dt = parse_date(post_date_str)
    if dt is None:
        return 0.0
    days_ago = (REFERENCE_DATE - dt).days
    if days_ago < 0:
        days_ago = 0
    # 指数衰减：今天 = +2.0，半衰期后 = +1.0，很久以前 → 0
    decay = 0.5 ** (days_ago / half_life_days)
    return 2.0 * decay

def search(query, top_n=10):
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    query_terms = [t for t in query.strip().split() if t not in STOP_WORDS]
    if not query_terms:
        return []

    # 额外生成中文字查询词
    chinese_query = ''.join(re.findall(r'[一-鿿]+', query))
    if chinese_query:
        for i in range(len(chinese_query) - 2):
            bigram = chinese_query[i:i+2]
            if bigram not in query_terms:
                query_terms.append(bigram)

    scored = []
    for post in data:
        text = post.get('text', '')
        if not text:
            continue
        text_clean = clean_html(text)
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

        # 短语匹配加分
        if query.strip().lower() in text_lower:
            score += 5.0

        # 长度惩罚（避免长文本霸榜）
        score = score / (1 + math.log(1 + len(text_clean) / 500))

        # 时间衰减加分（让新帖优先）
        score += recency_boost(post.get('created_at', ''))

        scored.append((score, post, text_clean))

    scored.sort(key=lambda x: x[0], reverse=True)

    results = []
    for score, post, text_clean in scored[:top_n]:
        snippet, _ = extract_snippet(post['text'], query_terms)
        results.append({
            "id": post.get("id"),
            "created_at": post.get("created_at", ""),
            "score": round(score, 2),
            "snippet": snippet,
        })
    return results

def format_output(results):
    if not results:
        return "未找到相关内容。"
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"--- 结果 {i} (相关度: {r['score']}) ---")
        lines.append(f"日期: {r['created_at']}")
        lines.append(f"内容片段: {r['snippet']}")
        lines.append("")
    return "\n".join(lines)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python search_kb.py <查询关键词> [返回数量]")
        print("示例: python search_kb.py \"心动公司 TapTap 估值\" 5")
        sys.exit(1)

    query = sys.argv[1]
    top_n = int(sys.argv[2]) if len(sys.argv) > 2 else 8

    # 静默模式：只输出 JSON，用于 skill 内部调用
    silent = "--silent" in sys.argv or "-s" in sys.argv

    results = search(query, top_n)

    if "--json" in sys.argv or silent:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        print(f"查询: {query}")
        print(f"找到 {len(results)} 条相关结果\n")
        print(format_output(results))
