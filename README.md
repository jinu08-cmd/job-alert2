# 채용 공고 자동 수집 대시보드

사람인 · 잡코리아 · 원티드에서 관심 키워드로 공고를 검색해, 매일 정해진 시간에
새로 등록된 공고와 전체 필터링된 공고를 웹 대시보드로 보여주는 프로젝트입니다.
서버가 없어도 **GitHub Actions(무료 스케줄러) + GitHub Pages(무료 호스팅)** 조합으로
매일 자동 실행됩니다.

## 동작 방식
1. `config.json`에 적어둔 키워드로 각 사이트를 검색합니다.
2. 이전에 본 공고 목록(`data/seen.json`)과 비교해 새 공고만 따로 가려냅니다.
3. `docs/index.html`을 새로 만들어 "새 공고 / 전체 공고" 두 섹션으로 보여줍니다.
4. GitHub Actions가 이 과정을 매일 자동 실행하고 결과를 저장소에 커밋합니다.
5. 여러분은 매일 정해진 GitHub Pages 주소(북마크해두면 됨)만 열어보면 됩니다.

## 처음 설정하는 방법

1. **GitHub 저장소 만들기**
   - github.com에서 새 저장소(예: `job-alert`)를 만들고, 이 폴더의 파일을 모두 업로드(또는 `git push`)합니다.

2. **Actions에 쓰기 권한 주기**
   - 저장소 `Settings > Actions > General > Workflow permissions`에서
     **"Read and write permissions"** 를 선택하고 저장합니다.
   - (자동 커밋을 위해 필요합니다.)

3. **GitHub Pages 켜기**
   - 저장소 `Settings > Pages`에서 Source를 `Deploy from a branch`로 두고,
     브랜치는 `main`, 폴더는 `/docs`를 선택합니다.
   - 잠시 후 `https://내아이디.github.io/저장소이름/` 주소가 생깁니다. 이 주소를 매일 열어보면 됩니다.

4. **한 번 수동으로 실행해보기**
   - 저장소 `Actions` 탭 > `Daily Job Scan` 워크플로 선택 > `Run workflow` 클릭.
   - 몇 분 후 `docs/index.html`이 실제 공고로 채워지고, Pages에 반영됩니다.

5. **키워드 수정하기**
   - `config.json`의 `keywords` 배열을 원하는 검색어로 바꾸면 됩니다.

## 알림 시간 바꾸기
`.github/workflows/daily.yml`의 `cron: "0 0 * * *"` 값을 수정하세요.
GitHub Actions는 UTC 기준이라 **한국시간(KST) = UTC + 9시간**입니다.
예) 매일 오전 8시(KST)에 실행하고 싶다면 → UTC 23시 → `"0 23 * * *"`

## 사이트 스크레이퍼가 안 될 때 (중요)
사람인 / 잡코리아 / 원티드는 사이트 개편으로 HTML 구조나 API가 수시로 바뀝니다.
`scraper/saramin.py`, `scraper/jobkorea.py`, `scraper/wanted.py` 각 파일 상단 주석에
문제 발생 시 브라우저 개발자도구(F12)로 실제 셀렉터/API를 확인해 고치는 방법을
적어두었습니다. 특히 **원티드는 자바스크립트 렌더링 방식**이라 API 주소가 바뀌면
꼭 Network 탭에서 실제 요청을 다시 확인해야 합니다.

Actions 실행 로그(`Actions` 탭 > 해당 실행 > `공고 수집 및 대시보드 생성` 단계)에서
"검색 결과 0건" 경고가 보이면 해당 사이트의 셀렉터를 업데이트해야 한다는 뜻입니다.

## 로컬에서 미리 테스트하기
```bash
pip install -r requirements.txt
python main.py
# docs/index.html을 브라우저로 열어서 확인
```

## 폴더 구조
```
config.json              # 키워드/사이트 설정
main.py                  # 실행 진입점
generate_dashboard.py    # HTML 대시보드 생성
scraper/
  common.py               # 공통 유틸(요청, 저장)
  saramin.py              # 사람인 스크레이퍼
  jobkorea.py             # 잡코리아 스크레이퍼
  wanted.py               # 원티드 수집기
data/seen.json            # 이미 본 공고 기록 (자동 갱신)
docs/index.html      # 매일 갱신되는 결과 페이지
.github/workflows/daily.yml  # 매일 자동 실행 설정
```
