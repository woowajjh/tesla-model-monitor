"""테슬라 한국 신규 모델 출시 모니터링 — 메인 스크립트."""

from __future__ import annotations

import json
import sys

from config import STATE_FILE
from scraper import scrape_models
from notifier import send_discord_notification


def load_state() -> list[str]:
    """state.json에서 이전 모델 목록을 로드한다."""
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("models", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def save_state(models: list[str]) -> None:
    """현재 모델 목록을 state.json에 저장한다."""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({"models": models}, f, ensure_ascii=False, indent=2)


def main() -> None:
    print("=== 테슬라 한국 모델 모니터링 시작 ===")

    # 1. 현재 모델 목록 스크래핑
    current_models = scrape_models()
    if not current_models:
        print("[경고] 모델을 하나도 가져오지 못했습니다. 사이트 구조가 변경되었을 수 있습니다.")
        sys.exit(1)

    print(f"[스크래핑] 현재 모델: {current_models}")

    # 2. 이전 상태 로드
    previous_models = load_state()
    print(f"[상태] 이전 모델: {previous_models}")

    # 3. 새 모델 감지 (차집합)
    new_models = [m for m in current_models if m not in previous_models]

    if new_models:
        print(f"[감지] 새 모델 발견: {new_models}")
        send_discord_notification(new_models)
    else:
        print("[결과] 새로운 모델이 없습니다.")

    # 4. 상태 업데이트 (항상 최신 목록으로 갱신)
    save_state(current_models)
    print(f"[저장] state.json 업데이트 완료")
    print("=== 모니터링 종료 ===")


if __name__ == "__main__":
    main()
