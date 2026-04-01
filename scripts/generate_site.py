#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
DAYS_DIR = ROOT / "days"
SKILL_SCRIPT = Path("/root/.openclaw/workspace-tg-group-5075638349/skills/openclaw-tavily-search/scripts/tavily_search.py")
TZ = ZoneInfo("Europe/Berlin")

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

INDEX_TEMPLATE_TOP = """<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>情報哈狗 AI News</title>
  <meta name=\"description\" content=\"每日 AI 熱點新聞整理，可依日期瀏覽並支援站內搜尋。\" />
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"> 
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800&display=swap\" rel=\"stylesheet\">
  <link rel=\"stylesheet\" href=\"styles.css\" />
</head>
<body>
  <div class=\"breaking-bar\">
    <span class=\"breaking-label\">HOME</span>
    <div class=\"ticker\"><span>首頁已上線：每天早上 8:00 自動更新 AI 熱點新聞，支援日期分頁與站內搜尋</span></div>
  </div>
  <header class=\"hero\">
    <div class=\"hero-overlay\"></div>
    <div class=\"hero-content container\">
      <p class=\"channel\">情報哈狗 AI NEWS</p>
      <h1>AI 新聞首頁</h1>
      <p class=\"subtitle\">先看最新焦點，再追歷史日期；每天早上 8:00 自動更新</p>
      <div class=\"search-bar\">
        <input id=\"site-search\" type=\"search\" placeholder=\"搜尋日期、標題、摘要、來源...\" />
      </div>
      <div class=\"hero-tags\">
        <span>首頁摘要</span>
        <span>每日更新</span>
        <span>日期分頁</span>
        <span>站內搜尋</span>
      </div>
    </div>
  </header>
  <main class=\"container home-main\">
    <section class=\"home-grid\">
      <article class=\"feature-panel\">
        <div class=\"section-kicker\">Latest Issue</div>
        <h2>最新一期：<a href=\"{latest_href}\">{latest_date}</a></h2>
        <p>{latest_intro}</p>
        <div class=\"feature-actions\">
          <a class=\"primary-button\" href=\"{latest_href}\">閱讀今日完整頁</a>
          <a class=\"secondary-button\" href=\"#archive\">查看歷史日期</a>
        </div>
      </article>
      <aside class=\"stats-panel\">
        <div class=\"stat-card\">
          <span class=\"stat-label\">已收錄日期</span>
          <strong>{days_count}</strong>
        </div>
        <div class=\"stat-card\">
          <span class=\"stat-label\">新聞條目</span>
          <strong>{items_count}</strong>
        </div>
        <div class=\"stat-card\">
          <span class=\"stat-label\">更新時間</span>
          <strong>08:00</strong>
        </div>
      </aside>
    </section>

    <section class=\"section-block\">
      <div class=\"section-head\">
        <div>
          <div class=\"section-kicker\">Top Stories</div>
          <h2>今日焦點</h2>
        </div>
        <a class=\"section-link\" href=\"{latest_href}\">看完整榜單 →</a>
      </div>
      <div class=\"top-stories\">{featured_cards}</div>
    </section>

    <section id=\"archive\" class=\"section-block archive-section\">
      <div class=\"section-head\">
        <div>
          <div class=\"section-kicker\">Archive</div>
          <h2>日期總覽</h2>
        </div>
        <div class=\"latest-banner\">最新一期：<a href=\"{latest_href}\">{latest_date}</a></div>
      </div>
      <div id=\"results\" class=\"archive-list\">"""

INDEX_TEMPLATE_BOTTOM = """
      </div>
    </section>
  </main>
  <footer class=\"footer\">
    <div class=\"container footer-inner\">
      <div>情報哈狗 AI News 首頁</div>
      <div>每日 08:00 自動更新 · Tavily Search 驅動 · 支援搜尋與日期分頁</div>
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


def today_str():
    return datetime.now(TZ).strftime("%Y-%m-%d")


def fetch_news(date_str: str):
    query = f"AI news headlines {date_str} top stories"
    cmd = ["python3", str(SKILL_SCRIPT), "--query", query, "--max-results", "10", "--format", "brave"]
    out = subprocess.check_output(cmd, text=True)
    data = json.loads(out)
    results = data.get("results", [])[:10]
    items = []
    for r in results:
        title = r.get("title", "未命名新聞")
        url = r.get("url", "#")
        snippet = (r.get("snippet") or "").strip()
        source = source_from_url(url)
        items.append({
            "title": title,
            "url": url,
            "summary": snippet[:220] if snippet else "尚無摘要，請點原文查看。",
            "source": source
        })
    return items


def source_from_url(url: str) -> str:
    host = url.split("//")[-1].split("/")[0].replace("www.", "")
    return host


def save_day(date_str: str, items):
    payload = {
        "date": date_str,
        "generatedAt": datetime.now(TZ).isoformat(),
        "items": items
    }
    (DATA_DIR / f"{date_str}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def load_all_days():
    days = []
    for path in sorted(DATA_DIR.glob("*.json"), reverse=True):
        days.append(json.loads(path.read_text(encoding="utf-8")))
    return days


def render_day_page(day):
    date = day["date"]
    items_html = []
    for i, item in enumerate(day["items"], start=1):
        items_html.append(f"""
        <article class=\"headline-card\">
          <div class=\"rank\">{i}</div>
          <h3>{escape(item['title'])}</h3>
          <p>{escape(item['summary'])}</p>
          <div class=\"meta\">來源：{escape(item['source'])}</div>
          <a href=\"{item['url']}\" target=\"_blank\" rel=\"noopener\">查看原文</a>
        </article>
        """)

    html = f"""<!DOCTYPE html>
<html lang=\"zh-Hant\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>{date}｜AI 每日新聞</title>
  <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\"> 
  <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
  <link href=\"https://fonts.googleapis.com/css2?family=Noto+Sans+TC:wght@400;500;700;800&display=swap\" rel=\"stylesheet\">
  <link rel=\"stylesheet\" href=\"../styles.css\" />
</head>
<body>
  <div class=\"breaking-bar\">
    <span class=\"breaking-label\">DAILY</span>
    <div class=\"ticker\"><span>{date} AI 新聞精選 10 則</span></div>
  </div>
  <header class=\"hero hero-small\">
    <div class=\"hero-overlay\"></div>
    <div class=\"hero-content container\">
      <p class=\"channel\">情報哈狗 AI NEWS</p>
      <h1>{date} AI 新聞熱點</h1>
      <p class=\"subtitle\">每日自動生成專題頁</p>
      <p><a class=\"back-link\" href=\"../index.html\">← 返回首頁 / 日期總覽</a></p>
    </div>
  </header>
  <main class=\"container\">
    <section class=\"day-grid\">
      {''.join(items_html)}
    </section>
  </main>
</body>
</html>
"""
    (DAYS_DIR / f"{date}.html").write_text(html, encoding="utf-8")


def render_index(days):
    latest = days[0]
    cards = []
    search_index = []
    featured_cards = []
    total_items = 0

    for day in days:
        day_link = f"days/{day['date']}.html"
        preview = day['items'][0]['summary'] if day['items'] else ''
        total_items += len(day['items'])
        cards.append(f"""
        <article class=\"archive-card\" data-date=\"{day['date']}\">
          <div>
            <div class=\"archive-date\">{day['date']}</div>
            <h2><a href=\"{day_link}\">{day['date']} AI 新聞熱點</a></h2>
            <p>{escape(preview)}</p>
          </div>
          <a class=\"archive-link\" href=\"{day_link}\">閱讀當日新聞</a>
        </article>
        """)
        search_index.append({
            "date": day["date"],
            "href": day_link,
            "title": f"{day['date']} AI 新聞熱點",
            "text": " ".join([
                day["date"],
                *(item["title"] for item in day["items"]),
                *(item["summary"] for item in day["items"]),
                *(item["source"] for item in day["items"]),
            ])
        })

    for item in latest["items"][:3]:
        featured_cards.append(f"""
        <article class=\"story-card\">
          <div class=\"story-source\">{escape(item['source'])}</div>
          <h3>{escape(item['title'])}</h3>
          <p>{escape(item['summary'])}</p>
          <a class=\"story-link\" href=\"{item['url']}\" target=\"_blank\" rel=\"noopener\">查看原文</a>
        </article>
        """)

    latest_intro = escape(latest['items'][0]['summary'] if latest['items'] else '這一期已整理最新 AI 熱點，點進去看完整榜單。')
    html = INDEX_TEMPLATE_TOP.format(
        latest_href=f"days/{latest['date']}.html",
        latest_date=latest['date'],
        latest_intro=latest_intro,
        days_count=len(days),
        items_count=total_items,
        featured_cards="\n".join(featured_cards),
    ) + "\n".join(cards) + INDEX_TEMPLATE_BOTTOM
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    (ROOT / "search-index.json").write_text(json.dumps(search_index, ensure_ascii=False, indent=2), encoding="utf-8")


def escape(text: str) -> str:
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--fetch", action="store_true")
    parser.add_argument("--date", default=today_str())
    args = parser.parse_args()

    ensure_dirs()

    target_json = DATA_DIR / f"{args.date}.json"
    if args.fetch or not target_json.exists():
        try:
            items = fetch_news(args.date)
            if not items:
                items = DEFAULT_ITEMS
        except Exception:
            items = DEFAULT_ITEMS
        save_day(args.date, items)

    days = load_all_days()
    for day in days:
        render_day_page(day)
    render_index(days)


if __name__ == "__main__":
    main()
