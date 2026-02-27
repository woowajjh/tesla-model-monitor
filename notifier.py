from __future__ import annotations

import json
import requests

from config import DISCORD_WEBHOOK_URL, TESLA_URL


def send_discord_notification(new_models: list[str]) -> bool:
    """새로 감지된 모델 목록을 Discord로 전송한다."""
    if not DISCORD_WEBHOOK_URL:
        print("[알림] DISCORD_WEBHOOK_URL이 설정되지 않았습니다. 알림을 건너뜁니다.")
        return False

    model_list = ", ".join(new_models)
    payload = {
        "embeds": [
            {
                "title": "🚗 테슬라 한국 신규 모델 감지!",
                "description": (
                    f"새로운 모델이 추가되었습니다: **{model_list}**\n\n"
                    f"👉 [테슬라 한국 사이트 확인하기]({TESLA_URL})"
                ),
                "color": 0xE82127,  # 테슬라 레드
            }
        ],
    }

    try:
        resp = requests.post(
            DISCORD_WEBHOOK_URL,
            data=json.dumps(payload),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        resp.raise_for_status()
        print(f"[알림] Discord 전송 성공: {model_list}")
        return True
    except requests.RequestException as e:
        print(f"[알림] Discord 전송 실패: {e}")
        return False


if __name__ == "__main__":
    send_discord_notification(["Model YL (테스트)"])
