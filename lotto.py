import calendar
import random
import sys


def generate_lotto():
    """로또 번호 6개(1~45) + 보너스 번호를 랜덤으로 생성한다.

    실행할 때마다 새로운 번호가 나온다.
    """
    numbers = sorted(random.sample(range(1, 46), 6))
    bonus = random.choice([n for n in range(1, 46) if n not in numbers])
    return numbers, bonus


def normalize(raw: str) -> str:
    """다양한 입력 형식(19900101, 1990-01-01, 1990.01.01)을 검증한다."""
    digits = "".join(ch for ch in raw if ch.isdigit())
    if len(digits) != 8:
        raise ValueError("생년월일은 8자리(YYYYMMDD)로 입력해 주세요. 예) 1990-01-01")
    year, month, day = int(digits[:4]), int(digits[4:6]), int(digits[6:])
    if not (1900 <= year <= 2025):
        raise ValueError("연도는 1900~2025 사이로 입력해 주세요.")
    if not (1 <= month <= 12):
        raise ValueError("월은 01~12 사이로 입력해 주세요.")
    max_day = calendar.monthrange(year, month)[1]
    if not (1 <= day <= max_day):
        raise ValueError(f"{year}년 {month}월은 1~{max_day}일까지 있어요.")
    return digits


def main():
    if len(sys.argv) > 1:
        raw = sys.argv[1]
    else:
        raw = input("생년월일을 입력하세요 (예: 1990-01-01): ").strip()

    try:
        birthdate = normalize(raw)
    except ValueError as e:
        print(f"⚠️  {e}")
        sys.exit(1)

    numbers, bonus = generate_lotto()

    print()
    print(f"🎂 생년월일: {birthdate[:4]}-{birthdate[4:6]}-{birthdate[6:]}")
    print(f"🍀 행운의 로또 번호: {'  '.join(f'{n:2d}' for n in numbers)}")
    print(f"➕ 보너스 번호: {bonus}")
    print("   (실행할 때마다 새로운 번호가 나옵니다)")
    print()


if __name__ == "__main__":
    main()
