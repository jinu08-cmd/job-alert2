"""사이트별 스크레이퍼에서 공통으로 쓰는 함수 모음."""
import json
import hashlib
import time
import os
import requests

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 10
SLEEP_BETWEEN_REQUESTS = 1.5  # 사이트에 과도한 부하를 주지 않기 위한 대기 시간(초)


def fetch_html(url, params=None):
    """URL에서 HTML(or JSON 텍스트)을 가져온다. 실패 시 None 반환."""
    try:
        resp = requests.get(url, headers=HEADERS, params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        time.sleep(SLEEP_BETWEEN_REQUESTS)
        return resp
    except requests.RequestException as e:
        print(f"[경고] 요청 실패: {url} ({e})")
        return None


def job_id(site, link):
    """사이트명 + 링크를 기반으로 고유 ID(해시)를 만든다."""
    raw = f"{site}:{link}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def load_json(path, default):
    if not os.path.exists(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
