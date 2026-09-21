"""
매일 실행되는 메인 스크립트.

1. config.json에서 관심 키워드/사이트 목록을 읽는다.
2. 각 사이트 모듈로 키워드별 검색을 수행한다.
3. data/seen.json과 비교해 '오늘 새로 보이는 공고'를 가려낸다.
4. dashboard/index.html을 새로 생성한다.
5. seen.json을 갱신한다 (오래된 기록은 정리).
"""
import datetime
from scraper import SITE_MODULES
from scraper.common import load_json, save_json
from generate_dashboard import render_dashboard

CONFIG_PATH = "config.json"
SEEN_PATH = "data/seen.json"
DASHBOARD_PATH = "docs/index.html"


def collect_all_jobs(config):
    all_jobs = []
    for site_key in config.get("sites", []):
        module = SITE_MODULES.get(site_key)
        if module is None:
            print(f"[경고] 알 수 없는 사이트 키: {site_key}")
            continue
        for keyword in config.get("keywords", []):
            try:
                jobs = module.search(keyword)
                all_jobs.extend(jobs)
            except Exception as e:
                print(f"[오류] {site_key} / '{keyword}' 검색 중 문제 발생: {e}")

    # 같은 공고가 여러 키워드로 중복 매칭될 수 있으므로 id 기준으로 정리
    dedup = {}
    for job in all_jobs:
        dedup[job["id"]] = job
    return list(dedup.values())


def split_new_and_old(jobs, seen, keep_days):
    today = datetime.date.today().isoformat()
    new_jobs = []
    old_jobs = []

    for job in jobs:
        if job["id"] in seen:
            old_jobs.append(job)
        else:
            new_jobs.append(job)
            seen[job["id"]] = {"first_seen": today}

    # 오래된 기록 정리 (더 이상 검색 결과에 나오지 않는 오래된 항목 삭제)
    cutoff = datetime.date.today() - datetime.timedelta(days=keep_days)
    seen_cleaned = {
        jid: info for jid, info in seen.items()
        if datetime.date.fromisoformat(info["first_seen"]) >= cutoff
    }

    return new_jobs, old_jobs, seen_cleaned


def main():
    config = load_json(CONFIG_PATH, {})
    if not config:
        print("config.json을 찾을 수 없거나 비어 있습니다.")
        return

    seen = load_json(SEEN_PATH, {})
    jobs = collect_all_jobs(config)
    new_jobs, old_jobs, seen = split_new_and_old(jobs, seen, config.get("keep_days", 60))

    print(f"총 {len(jobs)}건 수집, 신규 {len(new_jobs)}건, 기존 {len(old_jobs)}건")

    render_dashboard(DASHBOARD_PATH, new_jobs, old_jobs, config.get("keywords", []))
    save_json(SEEN_PATH, seen)


if __name__ == "__main__":
    main()
