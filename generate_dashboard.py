"""수집된 공고 데이터를 사람이 보기 좋은 정적 HTML 대시보드로 렌더링한다."""
import datetime
import html
import os

CARD_TEMPLATE = """
<div class="card {highlight_class}">
  <div class="card-top">
    <span class="badge badge-{site_class}">{site}</span>
    <span class="date">{date}</span>
  </div>
  {highlight_badges}
  <a class="title" href="{link}" target="_blank" rel="noopener">{title}</a>
  <div class="company">{company}</div>
  <div class="keyword">검색어: {keyword}</div>
</div>
"""

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>오늘의 채용 공고 대시보드</title>
<style>
  :root {{
    --bg: #f6f7fb;
    --card-bg: #ffffff;
    --text: #1f2430;
    --muted: #6b7280;
    --accent: #4f46e5;
    --border: #e5e7eb;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    margin: 0;
    font-family: -apple-system, "Apple SD Gothic Neo", "Malgun Gothic", sans-serif;
    background: var(--bg);
    color: var(--text);
    padding: 24px 16px 60px;
  }}
  .wrap {{ max-width: 880px; margin: 0 auto; }}
  h1 {{ font-size: 22px; margin-bottom: 4px; }}
  .updated {{ color: var(--muted); font-size: 13px; margin-bottom: 28px; }}
  h2 {{ font-size: 17px; margin: 32px 0 12px; }}
  .grid {{ display: grid; gap: 12px; grid-template-columns: 1fr; }}
  @media (min-width: 640px) {{ .grid {{ grid-template-columns: 1fr 1fr; }} }}
  .card {{
    background: var(--card-bg);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 14px 16px;
  }}
  .card-top {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }}
  .badge {{
    font-size: 11px; padding: 3px 8px; border-radius: 999px; font-weight: 600;
    background: #eef2ff; color: var(--accent);
  }}
  .badge-잡코리아 {{ background: #fef3e2; color: #b45309; }}
  .badge-원티드 {{ background: #e0f2fe; color: #0369a1; }}
  .date {{ font-size: 12px; color: var(--muted); }}
  .title {{
    display: block; font-size: 15px; font-weight: 600; color: var(--text);
    text-decoration: none; margin-bottom: 4px; line-height: 1.4;
  }}
  .title:hover {{ color: var(--accent); }}
  .company {{ font-size: 13px; color: var(--muted); margin-bottom: 4px; }}
  .keyword {{ font-size: 11px; color: #9ca3af; }}
  .empty {{ color: var(--muted); font-size: 14px; padding: 12px 0; }}
  .card.highlight {{
    border: 1.5px solid #f59e0b;
    background: #fffbeb;
    box-shadow: 0 1px 3px rgba(245, 158, 11, 0.15);
  }}
  .highlight-badges {{ display: flex; gap: 6px; margin-bottom: 6px; flex-wrap: wrap; }}
  .tag-major {{
    font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;
    background: #fee2e2; color: #b91c1c;
  }}
  .tag-hot {{
    font-size: 11px; font-weight: 700; padding: 2px 8px; border-radius: 6px;
    background: #ffedd5; color: #c2410c;
  }}
</style>
</head>
<body>
<div class="wrap">
  <h1>오늘의 채용 공고</h1>
  <div class="updated">마지막 업데이트: {updated_at} · 관심 키워드: {keywords}</div>

  <h2>🆕 새로 등록된 공고 ({new_count}건)</h2>
  <div class="grid">
    {new_cards}
  </div>

  <h2>📋 이전에 확인한 공고 ({old_count}건)</h2>
  <div class="grid">
    {old_cards}
  </div>
</div>
</body>
</html>
"""


def _site_class(site):
    return html.escape(site)


def _badge_html(job):
    badges = []
    if job.get("is_major"):
        badges.append('<span class="tag-major">🏢 대기업</span>')
    if job.get("multi_site"):
        badges.append('<span class="tag-hot">🔥 여러 사이트 동시 등록</span>')
    if not badges:
        return ""
    return '<div class="highlight-badges">' + "".join(badges) + "</div>"


def _sort_key(job):
    # 강조 대상(대기업 또는 인기)을 먼저 보여주되, 원래 순서는 최대한 유지
    return 0 if (job.get("is_major") or job.get("multi_site")) else 1


def _render_cards(jobs):
    if not jobs:
        return '<div class="empty">해당하는 공고가 없습니다.</div>'

    ordered = sorted(jobs, key=_sort_key)

    return "\n".join(
        CARD_TEMPLATE.format(
            highlight_class="highlight" if (job.get("is_major") or job.get("multi_site")) else "",
            highlight_badges=_badge_html(job),
            site=html.escape(job["site"]),
            site_class=_site_class(job["site"]),
            date=html.escape(job.get("date", "")),
            link=html.escape(job["link"]),
            title=html.escape(job["title"]),
            company=html.escape(job.get("company", "")),
            keyword=html.escape(job.get("keyword", "")),
        )
        for job in ordered
    )


def render_dashboard(path, new_jobs, old_jobs, keywords):
    page = PAGE_TEMPLATE.format(
        updated_at=datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
        keywords=html.escape(", ".join(keywords)),
        new_count=len(new_jobs),
        old_count=len(old_jobs),
        new_cards=_render_cards(new_jobs),
        old_cards=_render_cards(old_jobs),
    )
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(page)
