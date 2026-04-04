#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse
import urllib.parse
import urllib.request
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DAYS_DIR = ROOT / "days"
TRANSLATION_CACHE_PATH = ROOT / "translation-cache.json"
SKILL_SCRIPT = Path("/root/.openclaw/workspace-tg-group-5075638349/skills/openclaw-tavily-search/scripts/tavily_search.py")
TZ = ZoneInfo("America/Los_Angeles")
TRANSLATION_CACHE = {}

SITE_CONFIGS = {
    "ai": {
        "site_name": "情報哈狗 AI NEWS",
        "page_title": "AI 每日新聞",
        "hero_title": "AI 新聞熱點",
        "hero_subtitle": "先看今日頭條，再用分類區塊快速掃描模型、硬體、應用、研究、產業與網路安全動態",
        "hero_tags": ["AI 頭條", "模型動態", "產品應用", "研究產業", "網安新聞"],
        "ticker_label": "AI 新聞精選 10 則",
        "footer_title": "情報哈狗 AI News 首頁",
        "footer_subtitle": "北加州時間每日 08:00 自動更新 · 新聞內容以中文整理呈現 · 支援搜尋與日期分頁",
        "theme_class": "theme-ai",
        "home_label": "AI",
        "home_href": "index.html",
        "home_desc": "模型、產品、研究與產業脈動",
    },
    "security": {
        "site_name": "情報哈狗 SECURITY NEWS",
        "page_title": "網安每日新聞",
        "hero_title": "網安新聞熱點",
        "hero_subtitle": "聚焦資安大廠、威脅情報、漏洞事件與企業安全產品動態",
        "hero_tags": ["資安頭條", "廠商動態", "威脅情報", "漏洞事件", "企業防禦"],
        "ticker_label": "網安新聞精選 10 則",
        "footer_title": "情報哈狗 Security News 首頁",
        "footer_subtitle": "北加州時間每日自動更新 · 聚焦企業安全、威脅研究與漏洞事件",
        "theme_class": "theme-security",
        "home_label": "網安",
        "home_href": "security.html",
        "home_desc": "廠商動態、威脅情報、漏洞事件",
    },
    "startups": {
        "site_name": "情報哈狗 STARTUP NEWS",
        "page_title": "新創每日新聞",
        "hero_title": "新創公司消息",
        "hero_subtitle": "追蹤新創融資、產品發表、創辦團隊與市場擴張動態",
        "hero_tags": ["新創頭條", "募資消息", "產品發布", "市場擴張", "創辦團隊"],
        "ticker_label": "新創新聞精選 10 則",
        "footer_title": "情報哈狗 Startup News 首頁",
        "footer_subtitle": "北加州時間每日自動更新 · 聚焦新創公司、募資、產品與市場動態",
        "theme_class": "theme-startups",
        "home_label": "新創",
        "home_href": "startups.html",
        "home_desc": "募資、產品發布、團隊與市場擴張",
    },
}

TRUSTED_DOMAINS = [
    "techcrunch.com",
    "theverge.com",
    "venturebeat.com",
    "openai.com",
    "anthropic.com",
    "googleblog.com",
    "blog.google",
    "blogs.microsoft.com",
    "microsoft.com",
    "securityweek.com",
    "thehackernews.com",
    "bleepingcomputer.com",
    "darkreading.com",
    "cyberscoop.com",
    "theregister.com",
    "forbes.com",
    "axios.com",
    "fortune.com",
    "barracuda.com",
    "fortinet.com",
    "paloaltonetworks.com",
    "checkpoint.com",
    "crowdstrike.com",
    "sentinelone.com",
    "zscaler.com",
    "okta.com",
    "cisco.com",
    "splunk.com",
    "security.googleblog.com",
    "cloud.google.com",
    "mandiant.com",
    "trendmicro.com",
    "sophos.com",
    "cloudflare.com",
    "proofpoint.com",
    "rapid7.com",
    "tenable.com",
    "qualys.com",
    "wiz.io",
    "netskope.com",
    "cyberark.com",
    "mimecast.com",
    "arcticwolf.com",
]

SECURITY_COMPANIES = [
    "Fortinet",
    "Palo Alto Networks",
    "Check Point",
    "Barracuda",
    "CrowdStrike",
    "SentinelOne",
    "Zscaler",
    "Okta",
    "Cisco Security",
    "Microsoft Security",
    "Google Cloud Security",
    "Mandiant",
    "Trend Micro",
    "Sophos",
    "Cloudflare",
    "Proofpoint",
    "Rapid7",
    "Tenable",
    "Qualys",
    "Wiz",
    "Netskope",
    "CyberArk",
    "Mimecast",
    "Arctic Wolf",
    "Splunk",
    "VMware Carbon Black",
]

DEFAULT_ITEMS = [
    {
        "title": "Nothing 傳布局 AI 穿戴裝置",
        "url": "https://techcrunch.com/2026/04/01/nothings-ai-devices-plan-reportedly-contains-smart-glasses-and-earbuds/",
        "summary": "Nothing 傳出規劃推出結合 AI 的智慧眼鏡與耳機，顯示 AI 正快速從手機助手延伸到隨身硬體。",
        "source": "TechCrunch"
    },
    {
        "title": "Cognichip 融資 6000 萬美元，用 AI 設計 AI 晶片",
        "url": "https://techcrunch.com/2026/04/01/cognichip-wants-ai-to-design-the-chips-that-power-ai-and-just-raised-60m-to-try/",
        "summary": "AI 正切入晶片設計流程，試圖降低開發成本與時間，加速 AI 基礎設施演進。",
        "source": "TechCrunch"
    },
    {
        "title": "AI 使用增加，但信任度下降",
        "url": "https://techcrunch.com/2026/03/30/ai-trust-adoption-poll-more-americans-adopt-tools-fewer-say-they-can-trust-the-results/",
        "summary": "最新民調顯示，AI 工具採用率上升，但大眾對可靠性、透明度與監管的疑慮仍高。",
        "source": "TechCrunch"
    },
    {
        "title": "Anthropic 近期聲量持續升高",
        "url": "https://techcrunch.com/video/openai-shuts-down-sora-while-meta-gets-shut-out-in-court/",
        "summary": "Anthropic 與 Claude 的市場討論度與商業能見度持續上升，模型競爭更激烈。",
        "source": "TechCrunch"
    },
    {
        "title": "Claude 付費消費者人氣攀升",
        "url": "https://techcrunch.com/video/openai-shuts-down-sora-while-meta-gets-shut-out-in-court/",
        "summary": "Claude 在付費市場的成長受到關注，反映通用 AI 助手市場競爭白熱化。",
        "source": "TechCrunch"
    },
    {
        "title": "OpenAI：Gradient Labs 用 AI 當銀行客戶經理",
        "url": "https://openai.com/index/gradient-labs/",
        "summary": "AI agent 已深入金融服務場景，朝更即時、更複雜的業務流程前進。",
        "source": "OpenAI"
    },
    {
        "title": "UT Austin 用 ChatGPT 重建研究流程",
        "url": "https://academy.openai.com/home/blogs/from-broken-pdfs-to-instant-access-how-chatgpt-rebuilds-the-research-workflow-at-ut-austin-2026-04-01",
        "summary": "教育與研究場景持續擴張，AI 正成為知識處理與文件整理的工作流基礎。",
        "source": "OpenAI Academy"
    },
    {
        "title": "Google TurboQuant 持續引發討論",
        "url": "https://techcrunch.com/2026/03/25/google-turboquant-ai-memory-compression-silicon-valley-pied-piper/",
        "summary": "提升模型效率與壓縮記憶體使用的技術，可能影響推論成本與部署門檻。",
        "source": "TechCrunch"
    },
    {
        "title": "AI 正延伸至 3D 與空間內容生成",
        "url": "https://venturebeat.com/business/stop-repairing-start-manufacturing",
        "summary": "生成式 AI 從文字、圖片跨向 3D 與空間內容，帶動製造、設計與 XR 新應用。",
        "source": "VentureBeat"
    },
    {
        "title": "今日總結：焦點轉向硬體、應用與治理",
        "url": "https://techstartups.com/2026/04/01/top-tech-news-today-april-1-2026/",
        "summary": "今日 AI 熱點顯示，市場已從模型競賽擴展到硬體、垂直應用、社會信任與法規治理。",
        "source": "TechStartups"
    }
]

CATEGORIES = [
    {
        "id": "models",
        "label": "模型與助手",
        "description": "大模型、AI 助手、代理與平台能力更新",
        "keywords": [
            "gpt", "claude", "gemini", "anthropic", "openai", "llm", "model", "assistant",
            "chatbot", "reasoning", "multimodal", "sora", "agent", "agents", "copilot"
        ],
    },
    {
        "id": "hardware",
        "label": "晶片與硬體",
        "description": "晶片、記憶體、終端裝置、機器人與基礎設施",
        "keywords": [
            "chip", "chips", "gpu", "npu", "silicon", "semiconductor", "hardware", "device",
            "devices", "glasses", "earbuds", "wearable", "memory", "quant", "robot", "robotics"
        ],
    },
    {
        "id": "products",
        "label": "產品與應用",
        "description": "企業導入、工作流、工具、服務與商業落地",
        "keywords": [
            "workflow", "customer", "bank", "banking", "tool", "tools", "platform", "startup",
            "service", "product", "products", "app", "apps", "enterprise", "productivity", "automation"
        ],
    },
    {
        "id": "research",
        "label": "研究與教育",
        "description": "研究突破、學校應用、醫療與知識工作流",
        "keywords": [
            "research", "study", "university", "academy", "education", "paper", "medical", "cancer",
            "science", "scientific", "lab", "labs", "workflow at"
        ],
    },
    {
        "id": "governance",
        "label": "監管與產業",
        "description": "信任、安全、法規、投資與產業變化",
        "keywords": [
            "trust", "adoption", "law", "legal", "policy", "regulation", "governance", "court",
            "lawsuit", "safety", "funding", "raised", "market", "investment", "enterprise value"
        ],
    },
    {
        "id": "security",
        "label": "網路安全",
        "description": "資安大廠、威脅情報、防禦產品、漏洞事件與企業安全動態",
        "keywords": [
            "cybersecurity", "cyber", "security", "threat", "threat intel", "ransomware", "breach",
            "malware", "phishing", "zero day", "zero-day", "vulnerability", "fortinet",
            "palo alto", "palo alto networks", "check point", "checkpoint", "barracuda",
            "crowdstrike", "sentinelone", "zscaler", "okta", "cisco security",
            "microsoft security", "google cloud security", "mandiant", "trend micro", "sophos",
            "cloudflare", "proofpoint", "rapid7", "tenable", "qualys", "wiz", "netskope",
            "cyberark", "mimecast", "arctic wolf", "splunk", "carbon black", "firewall", "soc", "siem",
            "xdr", "sase", "vpn", "attack"
        ],
    },
]

STARTUP_SUBCATEGORIES = [
    {
        "id": "startup-funding",
        "label": "募資動態",
        "description": "種子輪、A/B 輪、創投投資與資金消息",
        "keywords": ["funding", "fundraise", "raised", "raises", "seed", "series a", "series b", "series c", "venture", "vc", "investor", "capital"],
    },
    {
        "id": "startup-product",
        "label": "產品發布",
        "description": "新產品、功能更新、上線與發布",
        "keywords": ["launch", "launches", "launched", "product", "feature", "features", "release", "releases", "debut", "app", "platform"],
    },
    {
        "id": "startup-market",
        "label": "市場擴張",
        "description": "合作、併購、商業拓展與國際布局",
        "keywords": ["acquisition", "acquire", "merger", "partnership", "partners", "expansion", "expands", "market", "customers", "enterprise"],
    },
    {
        "id": "startup-team",
        "label": "創辦團隊",
        "description": "創辦人、管理層與公司策略調整",
        "keywords": ["founder", "founders", "ceo", "executive", "leadership", "team", "hiring", "strategy", "cofounder"],
    },
]

SECURITY_SUBCATEGORIES = [
    {
        "id": "security-vendors",
        "label": "廠商動態",
        "description": "資安大廠的產品更新、合作、財報、研究報告與策略布局",
        "keywords": [
            "fortinet", "palo alto", "palo alto networks", "check point", "checkpoint", "barracuda",
            "crowdstrike", "sentinelone", "zscaler", "okta", "cisco", "microsoft security",
            "google cloud security", "mandiant", "trend micro", "sophos", "cloudflare",
            "proofpoint", "rapid7", "tenable", "qualys", "wiz", "netskope", "cyberark",
            "mimecast", "arctic wolf", "splunk", "carbon black", "rsac", "earnings",
            "partnership", "launch", "report", "platform", "xdr", "sase", "siem"
        ],
    },
    {
        "id": "security-threats",
        "label": "威脅情報",
        "description": "APT、勒索軟體、攻擊趨勢、釣魚與威脅研究動態",
        "keywords": [
            "threat", "threat intel", "threat intelligence", "apt", "ransomware", "phishing",
            "malware", "botnet", "campaign", "attacker", "attackers", "cyberattack", "breach",
            "incident response", "unit 42", "threat actor", "stolen identities", "intrusion"
        ],
    },
    {
        "id": "security-vulns",
        "label": "漏洞事件",
        "description": "零日漏洞、漏洞利用、修補更新與重大安全事件",
        "keywords": [
            "vulnerability", "vulnerabilities", "zero day", "zero-day", "cve", "exploit",
            "patch", "patched", "security flaw", "bug", "exposure", "compromise"
        ],
    },
]

INDEX_TEMPLATE_TOP = """<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{hero_title}｜情報哈狗</title>
  <meta name="description" content="每日 AI / 網安 / 新創熱點整理，可依日期瀏覽並支援站內搜尋。" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="styles.css" />
</head>
<body class="{theme_class}">
  <div class="breaking-bar">
    <span class="breaking-label">LIVE</span>
    <div class="ticker"><span>情報哈狗每日焦點更新 · AI / 網安 / 新創 三條線同步追蹤</span></div>
  </div>
  <header class="hero">
    <div class="hero-overlay"></div>
    <div class="hero-content container">
      <p class="channel">{site_name}</p>
      <h1>{hero_title}</h1>
      <p class="subtitle">{hero_subtitle}</p>
      <div class="hero-tags">
        <span>{hero_tag_1}</span>
        <span>{hero_tag_2}</span>
        <span>{hero_tag_3}</span>
        <span>{hero_tag_4}</span>
        <span>{hero_tag_5}</span>
      </div>
      <div class="search-bar">
        <input id="searchInput" type="search" placeholder="搜尋日期、公司、主題、關鍵字..." />
      </div>
    </div>
  </header>

  <main class="container home-main">
    {topic_hub}
    <section class="home-grid">
      <article class="feature-panel">
        <div class="section-kicker">今日頭條</div>
        <div class="feature-source">{feature_source}</div>
        <h2>{feature_title}</h2>
        <p>{feature_summary}</p>
        <div class="feature-actions">
          <a class="primary-button" href="{feature_url}" target="_blank" rel="noopener">查看原文</a>
          <a class="secondary-button" href="{latest_href}">閱讀 {latest_date} 完整頁</a>
        </div>
      </article>
      <aside class="stats-panel">
        <div class="stat-card">
          <span class="stat-label">最新日期</span>
          <strong>{latest_date}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">已收錄日期</span>
          <strong>{days_count}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">新聞條目</span>
          <strong>{items_count}</strong>
        </div>
        <div class="stat-card">
          <span class="stat-label">分類數</span>
          <strong>{populated_categories}</strong>
        </div>
      </aside>
    </section>

    <section class="section-block">
      <div class="section-head">
        <div>
          <div class="section-kicker">分類總覽</div>
          <h2>今日分類速覽</h2>
        </div>
        <a class="section-link" href="{latest_href}">看完整榜單 →</a>
      </div>
      <div class="category-nav">{category_nav}</div>
      <div class="category-grid">{category_sections}</div>
    </section>

    <section id="archive" class="section-block archive-section">
      <div class="section-head">
        <div>
          <div class="section-kicker">新聞存檔</div>
          <h2>日期總覽</h2>
        </div>
        <div class="latest-banner">最新一期：<a href="{latest_href}">{latest_date}</a></div>
      </div>
      <div id="results" class="archive-list">"""

INDEX_TEMPLATE_BOTTOM = """
      </div>
    </section>
  </main>
  <footer class=\"footer\">
    <div class=\"container footer-inner\">
      <div>情報哈狗 AI News 首頁</div>
      <div>北加州時間每日 08:00 自動更新 · 新聞內容以中文整理呈現 · 支援搜尋與日期分頁</div>
    </div>
  </footer>
  <script src=\"search.js\"></script>
</body>
</html>
"""


def ensure_dirs():
    DATA_DIR.mkdir(exist_ok=True)
    DAYS_DIR.mkdir(exist_ok=True)
    (ROOT / "scripts").mkdir(exist_ok=True)


def load_translation_cache():
    global TRANSLATION_CACHE
    if TRANSLATION_CACHE_PATH.exists():
        try:
            TRANSLATION_CACHE = json.loads(TRANSLATION_CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            TRANSLATION_CACHE = {}


def save_translation_cache():
    TRANSLATION_CACHE_PATH.write_text(
        json.dumps(TRANSLATION_CACHE, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def today_str():
    return datetime.now(TZ).strftime("%Y-%m-%d")


def hostname_from_url(url: str) -> str:
    host = urlparse(url).netloc.lower().replace("www.", "")
    return host


def is_trusted_domain(url: str) -> bool:
    host = hostname_from_url(url)
    return any(host == domain or host.endswith(f".{domain}") for domain in TRUSTED_DOMAINS)


def company_bonus(text_blob: str) -> int:
    blob = text_blob.lower()
    return sum(1 for company in SECURITY_COMPANIES if company.lower() in blob)


def score_result(result: dict, query_kind: str) -> int:
    title = result.get("title", "") or ""
    snippet = result.get("snippet", "") or ""
    url = result.get("url", "") or ""
    blob = f"{title} {snippet} {url}".lower()
    host = hostname_from_url(url)

    score = 0
    if is_trusted_domain(url):
        score += 6
    if query_kind == "security":
        score += 3
    if query_kind == "startup":
        score += 3
    if any(word in blob for word in ["youtube", "podcast", "video", "linkedin"]):
        score -= 6
    if any(word in blob for word in ["april fools", "press release", "sponsored", "advertisement"]):
        score -= 5
    if any(word in blob for word in ["ai", "artificial intelligence"]):
        score += 2
    if any(word in blob for word in ["security", "cyber", "threat", "ransomware", "breach", "vulnerability"]):
        score += 3
    if any(word in blob for word in ["startup", "founder", "funding", "seed", "series a", "series b", "venture", "acquisition", "launch"]):
        score += 3
    score += company_bonus(blob) * 4
    if host in {"youtube.com", "linkedin.com"}:
        score -= 8
    return score


def run_tavily_query(query: str):
    cmd = ["python3", str(SKILL_SCRIPT), "--query", query, "--max-results", "12", "--format", "brave"]
    out = subprocess.check_output(cmd, text=True)
    data = json.loads(out)
    return data.get("results", [])


def fetch_news(date_str: str, mode: str = "ai"):
    security_query = (
        f"AI cybersecurity news {date_str} Fortinet Palo Alto Networks Check Point Barracuda CrowdStrike SentinelOne Zscaler Okta"
    )
    startup_query = (
        f"startup news {date_str} funding launch acquisition founders venture capital unicorn seed series a"
    )

    if mode == "security":
        queries = [
            (f"cybersecurity news {date_str} enterprise security threat intelligence vulnerability", "security"),
            (security_query, "security"),
            (f"security vendors news {date_str} Microsoft Security Google Cloud Security Wiz CrowdStrike Palo Alto Networks", "security"),
        ]
    elif mode == "startups":
        queries = [
            (startup_query, "startup"),
            (f"tech startups news {date_str} startup funding product launch founders", "startup"),
            (f"venture capital startup deals {date_str} seed series a series b acquisition", "startup"),
        ]
    else:
        queries = [
            (f"AI news headlines {date_str} top stories", "general"),
            (security_query, "security"),
        ]

    collected = []
    seen_urls = set()
    for query, query_kind in queries:
        for result in run_tavily_query(query):
            url = result.get("url", "#")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            result["_score"] = score_result(result, query_kind)
            collected.append(result)

    results = sorted(collected, key=lambda item: item.get("_score", 0), reverse=True)[:10]
    items = []
    for r in results:
        title = clean_title(r.get("title", "未命名新聞"))
        url = r.get("url", "#")
        snippet = clean_summary(r.get("snippet") or "")
        source = source_from_url(url)
        if source in {"youtube.com", "linkedin.com", "compliancepodcastnetwork.net"}:
            continue
        items.append({
            "title": title,
            "url": url,
            "summary": snippet,
            "source": source
        })
    return items[:10]


def source_from_url(url: str) -> str:
    host = url.split("//")[-1].split("/")[0].replace("www.", "")
    return host or "未知來源"


def normalize_text(text: str) -> str:
    text = text or ""
    text = re.sub(r"!Image\s*\d+\.?", " ", text, flags=re.IGNORECASE)
    text = re.sub(r"\[([^\]]*)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"https?://\S+", "", text)
    text = text.replace("##", " ")
    text = text.replace("**", " ")
    text = text.replace("__", " ")
    text = text.replace("•", " · ")
    text = text.replace("[", " ").replace("]", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip(" -·()[]{}.,\n\t")


def truncate(text: str, limit: int) -> str:
    if len(text) <= limit:
        return text
    shortened = text[:limit].rsplit(" ", 1)[0].strip()
    return (shortened or text[:limit]).rstrip(" ,.;:") + "…"


def clean_title(text: str) -> str:
    return truncate(normalize_text(text) or "未命名新聞", 110)


def clean_summary(text: str, limit: int = 180) -> str:
    cleaned = normalize_text(text)
    if not cleaned:
        return "尚無摘要，請點原文查看。"
    return truncate(cleaned, limit)


def contains_cjk(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text or ""))


def should_translate(text: str) -> bool:
    text = (text or "").strip()
    if not text:
        return False
    if contains_cjk(text):
        return False
    return bool(re.search(r"[A-Za-z]{4,}", text))


def translate_text(text: str) -> str:
    text = (text or "").strip()
    if not should_translate(text):
        return text

    if text in TRANSLATION_CACHE:
        return TRANSLATION_CACHE[text]

    url = (
        "https://translate.googleapis.com/translate_a/single"
        f"?client=gtx&sl=auto&tl=zh-TW&dt=t&q={urllib.parse.quote(text)}"
    )
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
        translated = "".join(part[0] for part in data[0] if part and part[0]).strip()
    except Exception:
        translated = text

    TRANSLATION_CACHE[text] = translated or text
    return TRANSLATION_CACHE[text]


def display_item(item):
    title_original = clean_title(item.get("title", "未命名新聞"))
    summary_original = clean_summary(item.get("summary", ""))
    title_zh = clean_title(translate_text(title_original))
    summary_zh = clean_summary(translate_text(summary_original), 200)

    return {
        "title": title_original,
        "title_zh": title_zh,
        "url": item.get("url", "#"),
        "summary": summary_original,
        "summary_zh": summary_zh,
        "source": normalize_text(item.get("source", "未知來源")) or "未知來源",
    }


def classify_item(item):
    blob = " ".join([
        item.get("title", ""),
        item.get("summary", ""),
        item.get("source", ""),
        item.get("url", ""),
    ]).lower()

    for category in CATEGORIES:
        if any(keyword in blob for keyword in category["keywords"]):
            return category

    return {
        "id": "other",
        "label": "其他動態",
        "description": "未明確落在單一主題、但值得快速掃描的內容",
    }


def classify_subcategory(item, subcategories):
    blob = " ".join([
        item.get("title", ""),
        item.get("summary", ""),
        item.get("source", ""),
        item.get("url", ""),
    ]).lower()

    for subcategory in subcategories:
        if any(keyword in blob for keyword in subcategory["keywords"]):
            return subcategory

    return subcategories[0]


def save_day(date_str: str, items):
    payload = {
        "date": date_str,
        "generatedAt": datetime.now(TZ).isoformat(),
        "items": [display_item(item) for item in items]
    }
    (DATA_DIR / f"{date_str}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_all_days():
    days = []
    for path in sorted(DATA_DIR.glob("*.json"), reverse=True):
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["items"] = [display_item(item) for item in payload.get("items", [])]
        days.append(payload)
    return days


def render_day_page(day, mode: str = "ai"):
    date = day["date"]
    config = SITE_CONFIGS[mode]
    display_items = [display_item(raw_item) for raw_item in day["items"]]
    items_html = []
    for i, item in enumerate(display_items, start=1):
        items_html.append(f"""
        <article class="headline-card">
          <div class="rank">{i}</div>
          <div class="headline-body">
            <div class="story-source">{escape(item['source'])}</div>
            <h3>{escape(item['title_zh'])}</h3>
            <p>{escape(item['summary_zh'])}</p>
            <a href="{item['url']}" target="_blank" rel="noopener">查看原文</a>
          </div>
        </article>
        """)

    category_nav, category_sections, _ = render_category_sections(display_items)

    html = f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>{date}｜{config['page_title']}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com"> 
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="../styles.css" />
</head>
<body>
  <div class="breaking-bar">
    <span class="breaking-label">每日</span>
    <div class="ticker"><span>{date} {config['ticker_label']}</span></div>
  </div>
  <header class="hero hero-small">
    <div class="hero-overlay"></div>
    <div class="hero-content container">
      <p class="channel">{config['site_name']}</p>
      <h1>{date}｜{config['hero_title']}</h1>
      <p class="subtitle">每日自動生成專題頁 · 手機也好讀</p>
      <p><a class="back-link" href="../{config['home_href']}">← 返回{config['home_label']}首頁 / 日期總覽</a></p>
    </div>
  </header>
  <main class="container">
    <section class="section-block day-category-block">
      <div class="section-head">
        <div>
          <div class="section-kicker">分類總覽</div>
          <h2>當日分類速覽</h2>
        </div>
      </div>
      <div class="category-nav">{category_nav}</div>
      <div class="category-grid">{category_sections}</div>
    </section>
    <section class="day-grid">
      {''.join(items_html)}
    </section>
  </main>
</body>
</html>
"""
    day_filename = f"{date}.html" if mode == "ai" else f"{date}-{mode}.html"
    (DAYS_DIR / day_filename).write_text(html, encoding="utf-8")

def render_category_sections(items):
    grouped = {}
    for category in CATEGORIES:
        grouped[category["id"]] = {**category, "items": []}
    grouped["other"] = {
        "id": "other",
        "label": "其他動態",
        "description": "未明確落在單一主題、但值得快速掃描的內容",
        "items": [],
    }

    for raw_item in items:
        item = display_item(raw_item)
        category = classify_item(item)
        grouped[category["id"]]["items"].append(item)

    ordered_groups = [grouped[category["id"]] for category in CATEGORIES] + [grouped["other"]]
    non_empty_groups = [group for group in ordered_groups if group["items"]]

    nav_html = []
    sections_html = []
    for group in non_empty_groups:
        nav_html.append(
            f'<a class="category-chip" href="#{group["id"]}">{escape(group["label"])}<span>{len(group["items"])} 則</span></a>'
        )

        if group["id"] in {"security", "products"}:
            subcategory_defs = SECURITY_SUBCATEGORIES if group["id"] == "security" else STARTUP_SUBCATEGORIES
            security_groups = {sub["id"]: {**sub, "items": []} for sub in subcategory_defs}
            for item in group["items"]:
                subcategory = classify_subcategory(item, subcategory_defs)
                security_groups[subcategory["id"]]["items"].append(item)

            subcards = []
            for sub in subcategory_defs:
                sub_group = security_groups[sub["id"]]
                if not sub_group["items"]:
                    continue
                sub_items = []
                for item in sub_group["items"][:3]:
                    sub_items.append(f"""
                    <article class=\"mini-item\">
                      <div class=\"mini-meta\">{escape(item['source'])}</div>
                      <h3><a class=\"mini-link\" href=\"{item['url']}\" target=\"_blank\" rel=\"noopener\">{escape(item['title_zh'])}</a></h3>
                      <p>{escape(item['summary_zh'])}</p>
                    </article>
                    """)
                subcards.append(f"""
                <section class=\"security-subpanel\">
                  <div class=\"security-subhead\">
                    <h4>{escape(sub_group['label'])}</h4>
                    <span>{len(sub_group['items'])} 則</span>
                  </div>
                  <p class=\"category-desc\">{escape(sub_group['description'])}</p>
                  <div class=\"mini-list\">{''.join(sub_items)}</div>
                </section>
                """)

            sections_html.append(f"""
            <article id=\"{group['id']}\" class=\"category-panel category-panel-security\">
              <div class=\"category-head\">
                <div>
                  <div class=\"section-kicker\">分類</div>
                  <h3>{escape(group['label'])}</h3>
                </div>
                <div class=\"category-count\">{len(group['items'])} 則</div>
              </div>
              <p class=\"category-desc\">{escape(group['description'])}</p>
              <div class=\"security-subgrid\">{''.join(subcards)}</div>
            </article>
            """)
            continue

        mini_items = []
        for item in group["items"][:3]:
            mini_items.append(f"""
            <article class=\"mini-item\">
              <div class=\"mini-meta\">{escape(item['source'])}</div>
              <h3><a class=\"mini-link\" href=\"{item['url']}\" target=\"_blank\" rel=\"noopener\">{escape(item['title_zh'])}</a></h3>
              <p>{escape(item['summary_zh'])}</p>
            </article>
            """)

        sections_html.append(f"""
            <article id=\"{group['id']}\" class=\"category-panel\">
          <div class=\"category-head\">
            <div>
              <div class=\"section-kicker\">分類</div>
              <h3>{escape(group['label'])}</h3>
            </div>
            <div class=\"category-count\">{len(group['items'])} 則</div>
          </div>
          <p class=\"category-desc\">{escape(group['description'])}</p>
          <div class=\"mini-list\">{''.join(mini_items)}</div>
        </article>
        """)

    return "".join(nav_html), "".join(sections_html), len(non_empty_groups)




def build_topic_hub(current_mode: str, days):
    cards = []
    for mode_key in ["ai", "security", "startups"]:
        config = SITE_CONFIGS[mode_key]
        active = " is-active" if mode_key == current_mode else ""
        date_text = days[0]["date"] if days else "尚無資料"
        item_count = len(days[0].get("items", [])) if days else 0
        cards.append(f"""
        <a class="topic-hub-card {config['theme_class']}{active}" href="{config['home_href']}">
          <div class="topic-hub-top">
            <span class="topic-hub-label">{escape(config['home_label'])}</span>
            <span class="topic-hub-count">{item_count} 則</span>
          </div>
          <h3>{escape(config['hero_title'])}</h3>
          <p>{escape(config['home_desc'])}</p>
          <div class="topic-hub-meta">最新日期：{escape(date_text)}</div>
        </a>
        """)
    return f"<section class=\"topic-hub\">{''.join(cards)}</section>"

def render_index(days, mode: str = "ai"):
    config = SITE_CONFIGS[mode]
    latest = days[0]
    latest_items = [display_item(item) for item in latest.get("items", [])]
    lead_item = latest_items[0] if latest_items else {
        "title": f"今日{config['hero_title']}整理",
        "title_zh": f"今日{config['hero_title']}整理",
        "summary": "這一期已整理最新重點，點進去看完整榜單。",
        "summary_zh": "這一期已整理最新重點，點進去看完整榜單。",
        "source": config['footer_title'],
        "url": f"days/{latest['date']}.html",
    }

    cards = []
    search_index = []
    total_items = 0
    category_nav, category_sections, populated_categories = render_category_sections(latest_items)

    for day in days:
        day_link = f"days/{day['date']}.html" if mode == "ai" else f"days/{day['date']}-{mode}.html"
        preview = clean_summary(day['items'][0].get('summary_zh') or day['items'][0]['summary'], 140) if day['items'] else ''
        total_items += len(day['items'])
        cards.append(f"""
        <article class=\"archive-card\" data-date=\"{day['date']}\">
          <div>
            <div class=\"archive-date\">{day['date']}</div>
            <h2><a href=\"{day_link}\">{day['date']}｜{config['hero_title']}</a></h2>
            <p>{escape(preview)}</p>
          </div>
          <a class=\"archive-link\" href=\"{day_link}\">閱讀當日新聞</a>
        </article>
        """)
        search_index.append({
            "date": day["date"],
            "href": day_link,
            "title": f"{day['date']}｜{config['hero_title']}",
            "text": " ".join([
                day["date"],
                *(item["title"] for item in day["items"]),
                *(item.get("title_zh", "") for item in day["items"]),
                *(item["summary"] for item in day["items"]),
                *(item.get("summary_zh", "") for item in day["items"]),
                *(item["source"] for item in day["items"]),
            ])
        })

    topic_hub = build_topic_hub(mode, days)

    html = INDEX_TEMPLATE_TOP.format(
        hero_title=escape(config['hero_title']),
        hero_subtitle=escape(config['hero_subtitle']),
        hero_tag_1=escape(config['hero_tags'][0]),
        hero_tag_2=escape(config['hero_tags'][1]),
        hero_tag_3=escape(config['hero_tags'][2]),
        hero_tag_4=escape(config['hero_tags'][3]),
        hero_tag_5=escape(config['hero_tags'][4]),
        site_name=escape(config['site_name']),
        footer_title=escape(config['footer_title']),
        footer_subtitle=escape(config['footer_subtitle']),
        feature_source=escape(lead_item['source']),
        feature_title=escape(lead_item.get('title_zh', lead_item['title'])),
        feature_summary=escape(clean_summary(lead_item.get('summary_zh', lead_item['summary']), 220)),
        feature_url=lead_item['url'],
        latest_href=(f"days/{latest['date']}.html" if mode == "ai" else f"days/{latest['date']}-{mode}.html"),
        latest_date=latest['date'],
        days_count=len(days),
        items_count=total_items,
        category_nav=category_nav,
        category_sections=category_sections,
        populated_categories=populated_categories,
        topic_hub=topic_hub,
        theme_class=escape(config['theme_class']),
    ) + "\n".join(cards) + INDEX_TEMPLATE_BOTTOM

    output_prefix = "" if mode == "ai" else f"{mode}-"
    index_name = "index.html" if mode == "ai" else f"{mode}.html"
    search_name = "search-index.json" if mode == "ai" else f"search-index-{mode}.json"
    (ROOT / index_name).write_text(html, encoding="utf-8")
    (ROOT / search_name).write_text(json.dumps(search_index, ensure_ascii=False, indent=2), encoding="utf-8")


def escape(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--date", default=today_str())
    parser.add_argument("--mode", choices=["ai", "security", "startups"], default="ai")
    args = parser.parse_args()

    ensure_dirs()
    load_translation_cache()

    target_json_name = f"{args.date}.json" if args.mode == "ai" else f"{args.date}-{args.mode}.json"
    target_json = DATA_DIR / target_json_name
    if args.fetch or not target_json.exists():
        try:
            items = fetch_news(args.date, args.mode)
            if not items:
                items = DEFAULT_ITEMS
        except Exception:
            items = DEFAULT_ITEMS
        payload = {
            "date": args.date,
            "generatedAt": datetime.now(TZ).isoformat(),
            "items": [display_item(item) for item in items]
        }
        target_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.mode == "ai":
        days = load_all_days()
    else:
        days = []
        for path in sorted(DATA_DIR.glob(f"*-{args.mode}.json"), reverse=True):
            payload = json.loads(path.read_text(encoding="utf-8"))
            payload["items"] = [display_item(item) for item in payload.get("items", [])]
            days.append(payload)
    for day in days:
        render_day_page(day, args.mode)
    render_index(days, args.mode)
    save_translation_cache()


if __name__ == "__main__":
    main()
