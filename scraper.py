from __future__ import annotations

import re

from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync

from config import TESLA_URL

# 차량 모델 경로 패턴 (design/drive 등 하위 경로 제외, 모델 루트만 매칭)
_MODEL_PATH_RE = re.compile(r"/ko_kr/(model[a-z0-9]*|cybertruck|roadster|semi)(?:/)?$")


def scrape_models() -> list[str]:
    """테슬라 한국 사이트에서 차량 모델 목록을 스크래핑한다."""
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--window-position=-9999,-9999",  # 창을 화면 밖으로
            ],
        )
        context = browser.new_context(
            locale="ko-KR",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/131.0.0.0 Safari/537.36"
            ),
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        stealth_sync(page)

        # 봇 감지 우회를 위한 추가 스크립트
        page.add_init_script("""
            Object.defineProperty(navigator, "webdriver", { get: () => undefined });
            window.chrome = { runtime: {} };
            Object.defineProperty(navigator, "plugins", {
                get: () => [1, 2, 3, 4, 5]
            });
            Object.defineProperty(navigator, "languages", {
                get: () => ["ko-KR", "ko", "en-US", "en"]
            });
        """)

        page.goto(TESLA_URL, wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(5_000)

        # 모든 링크에서 차량 모델 경로 추출
        links = page.evaluate("""() => {
            const results = [];
            document.querySelectorAll('a').forEach(a => {
                const href = a.getAttribute('href') || '';
                results.push(href);
            });
            return results;
        }""")

        browser.close()

    # href 패턴으로 모델 코드 추출
    model_codes: list[str] = []
    seen: set[str] = set()

    for href in links:
        m = _MODEL_PATH_RE.search(href)
        if m:
            code = m.group(1)  # e.g. "model3", "modely", "cybertruck"
            if code not in seen:
                seen.add(code)
                model_codes.append(code)

    # design 링크에서도 추출 (모델 페이지가 /design 으로만 존재하는 경우 대비)
    design_re = re.compile(r"/ko_kr/(model[a-z0-9]*|cybertruck|roadster|semi)/design")
    for href in links:
        m = design_re.search(href)
        if m:
            code = m.group(1)
            if code not in seen:
                seen.add(code)
                model_codes.append(code)

    return sorted(model_codes)


if __name__ == "__main__":
    found = scrape_models()
    print(f"감지된 모델 ({len(found)}개): {found}")
