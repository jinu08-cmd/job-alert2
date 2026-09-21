"""
사람인(saramin.co.kr) 검색 결과 스크레이퍼.

주의: 사람인은 페이지 구조를 종종 바꿉니다. 이 스크립트가 공고를 0개 가져온다면
아래 방법으로 셀렉터를 직접 확인해서 SELECTORS 값을 고쳐주세요.
  1. 브라우저에서 https://www.saramin.co.kr/zf_user/search/recruit?searchword=키워드 접속
  2. 공고 목록의 카드 하나를 우클릭 > 검사(Inspect)
  3. 카드 전체를 감싸는 태그의 class 이름을 확인해 SELECTORS["item"]에 반영
  4. 제목/링크/회사명/등록일 요소의 class도 같은 방식으로 확인
"""
from bs4 import BeautifulSoup
from .common import fetch_html, job_id

SEARCH_URL = "https://www.saramin.co.kr/zf_user/search/recruit"
SITE_NAME = "사람인"

# 사람인 검색 결과 페이지의 실제 CSS 클래스 (변경될 수 있음)
SELECTORS = {
    "item": "div.item_recruit",
    "title": "h2.job_tit a",
    "company": "strong.corp_name a",
    "date": "span.job_day",
}


def search(keyword, max_items=20):
    resp = fetch_html(SEARCH_URL, params={
        "searchword": keyword,
        "recruitPage": 1,
        "recruitSort": "relation",
    })
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
            link = "https://www.saramin.co.kr" + link

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
        print(f"[사람인] '{keyword}' 검색 결과 0건 — 셀렉터가 바뀌었을 수 있습니다.")

    return jobs
