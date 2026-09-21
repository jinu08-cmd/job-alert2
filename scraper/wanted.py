"""
원티드(wanted.co.kr) 검색 결과 수집기.

중요: 원티드는 페이지가 자바스크립트로 렌더링되기 때문에 사람인/잡코리아처럼
단순 HTML 스크레이핑(requests + BeautifulSoup)으로는 공고가 보이지 않습니다.
대신 브라우저가 내부적으로 호출하는 JSON API를 사용해야 합니다.

아래 API_URL은 원티드가 검색 시 호출하는 API의 예시 형태이며, 원티드 쪽 사정으로
경로/파라미터가 바뀌었을 수 있습니다. 동작하지 않으면 다음과 같이 실제 주소를
직접 확인해서 API_URL과 파라미터를 고쳐주세요.
  1. 크롬에서 https://www.wanted.co.kr/search?query=키워드&tab=position 접속
  2. F12 개발자도구 > Network 탭 > XHR/Fetch 필터
  3. 검색 결과가 로드될 때 호출되는 요청 중 'search' 또는 'position'이 포함된
     요청을 찾아 그 URL과 응답(JSON) 구조를 확인
  4. 확인한 URL/파라미터 이름/응답 필드명을 아래 API_URL, params, 파싱 부분에 반영
"""
from .common import fetch_html, job_id

API_URL = "https://www.wanted.co.kr/api/v4/search"
SITE_NAME = "원티드"


def search(keyword, max_items=20):
    resp = fetch_html(API_URL, params={
        "query": keyword,
        "tab": "position",
        "count": max_items,
    })
    if resp is None:
        return []

    try:
        data = resp.json()
    except ValueError:
        print(f"[원티드] '{keyword}' 응답이 JSON이 아닙니다 — API 주소가 바뀌었을 수 있습니다.")
        return []

    # 응답 구조는 실제 API 확인 후 아래 경로를 맞춰야 할 수 있습니다.
    raw_items = data.get("data") or data.get("positions") or []
    jobs = []

    for raw in raw_items[:max_items]:
        title = raw.get("position") or raw.get("title", "")
        company = (raw.get("company") or {}).get("name", "") if isinstance(raw.get("company"), dict) else raw.get("company_name", "")
        job_id_raw = raw.get("id", "")
        link = f"https://www.wanted.co.kr/wd/{job_id_raw}" if job_id_raw else ""
        date = raw.get("due_time") or raw.get("created_at", "")

        if not title or not link:
            continue

        jobs.append({
            "id": job_id(SITE_NAME, link),
            "site": SITE_NAME,
            "keyword": keyword,
            "title": title,
            "company": company,
            "date": date,
            "link": link,
        })

    if not raw_items:
        print(f"[원티드] '{keyword}' 검색 결과 0건 — API 응답 구조를 확인해주세요.")

    return jobs
