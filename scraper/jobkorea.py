"""
잡코리아(jobkorea.co.kr) 검색 결과 스크레이퍼.

주의: 잡코리아도 마크업이 바뀔 수 있습니다. 0건이 계속 나오면 saramin.py 상단
주석과 같은 방법으로 개발자도구(F12)에서 실제 class 이름을 확인해
아래 SELECTORS를 수정하세요.
"""
from bs4 import BeautifulSoup
from .common import fetch_html, job_id

SEARCH_URL = "https://www.jobkorea.co.kr/Search/"
SITE_NAME = "잡코리아"

SELECTORS = {
    "item": "div.list-post",
    "title": "a.title",
    "company": "a.name",
    "date": "span.date",
}


def search(keyword, max_items=20):
    resp = fetch_html(SEARCH_URL, params={"stext": keyword})
    if resp is None:
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = soup.select(SELECTORS["item"])
    jobs = []

    for item in items[:max_items]:
        title_el = item.select_one(SELECTORS["title"])
        company_el = item.select_one(SELECTORS["company"])
        date_el = item.select_one(SELECTORS["date"])

        if not title_el:
            continue

        title = title_el.get_text(strip=True)
        link = title_el.get("href", "")
        if link.startswith("/"):
            link = "https://www.jobkorea.co.kr" + link

        jobs.append({
            "id": job_id(SITE_NAME, link),
            "site": SITE_NAME,
            "keyword": keyword,
            "title": title,
            "company": company_el.get_text(strip=True) if company_el else "",
            "date": date_el.get_text(strip=True) if date_el else "",
            "link": link,
        })

    if not items:
        print(f"[잡코리아] '{keyword}' 검색 결과 0건 — 셀렉터가 바뀌었을 수 있습니다.")

    return jobs
