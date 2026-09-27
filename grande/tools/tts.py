"""ElevenLabs로 컷별 내레이션 mp3 생성.

사용법: ELEVENLABS_API_KEY=... python3 tools/tts.py 2026-09-26 [보이스이름]
결과: <날짜>/audio/ep1_01.mp3 ... (컷당 1파일)
"""
import json
import os
import sys
import urllib.request

API = "https://api.elevenlabs.io/v1"
KEY = os.environ["ELEVENLABS_API_KEY"]


def call(path, body=None):
    req = urllib.request.Request(
        API + path,
        data=json.dumps(body).encode() if body else None,
        headers={"xi-api-key": KEY, "Content-Type": "application/json"},
        method="POST" if body else "GET",
    )
    with urllib.request.urlopen(req) as r:
        return r.read()


def find_voice(name):
    voices = json.loads(call("/voices"))["voices"]
    for v in voices:
        if v["name"].strip() == name:
            return v["voice_id"]
    raise SystemExit(f"'{name}' 보이스 없음. 있는 것: {[v['name'] for v in voices]}")


def main():
    day = sys.argv[1]
    voice_id = find_voice(sys.argv[2] if len(sys.argv) > 2 else "해철")
    narration = json.load(open(f"{day}/narration.json", encoding="utf-8"))
    os.makedirs(f"{day}/audio", exist_ok=True)
    for ep, cuts in narration.items():
        for c in cuts:
            mp3 = call(
                f"/text-to-speech/{voice_id}?output_format=mp3_44100_128",
                {"text": c["text"], "model_id": "eleven_multilingual_v2"},
            )
            path = f"{day}/audio/{ep}_{c['cut']:02d}.mp3"
            open(path, "wb").write(mp3)
            print("saved", path)


if __name__ == "__main__":
    main()
