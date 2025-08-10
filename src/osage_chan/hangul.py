# -*- coding: utf-8 -*-
from typing import Dict
from jamo import h2j, j2hcj

def spell_any_korean(text: str, style: str = "standard", sep: str = "") -> str:
    # 1) 한글 음절을 호환 자모로 변환
    jamo_text = j2hcj(h2j(text))
    # 2) 위에서 만든 변환 함수 재사용
    return spell_jamo(jamo_text, style=style, sep=sep)

print(spell_any_korean("안녕ㅋㅋ", style="casual"))
# 예) 아ㄴ녀ㅇ키윽키윽 → 자모만 골라서 처리하려면 필터링을 더해도 됩니다.

# 표준 명칭(국립국어원 표기 관행에 맞춘 형태)
STD_CONSONANTS: Dict[str, str] = {
    "ㄱ": "기역", "ㄲ": "쌍기역", "ㄴ": "니은", "ㄷ": "디귿", "ㄸ": "쌍디귿",
    "ㄹ": "리을", "ㅁ": "미음", "ㅂ": "비읍", "ㅃ": "쌍비읍", "ㅅ": "시옷",
    "ㅆ": "쌍시옷", "ㅇ": "이응", "ㅈ": "지읒", "ㅉ": "쌍지읒", "ㅊ": "치읓",
    "ㅋ": "키읔", "ㅌ": "티읕", "ㅍ": "피읖", "ㅎ": "히읗",
}

# 자주 쓰는 구어체(키윽/티윽/피읍 등)
CASUAL_CONSONANTS: Dict[str, str] = {
    **STD_CONSONANTS,
    "ㅋ": "키윽",
    "ㅌ": "티윽",
    "ㅍ": "피읍",
    # 필요하면 아래처럼 추가: "ㄷ": "디긋", "ㅈ": "지읏", "ㅎ": "히읏" 등
}

VOWELS: Dict[str, str] = {
    "ㅏ": "아", "ㅑ": "야", "ㅓ": "어", "ㅕ": "여", "ㅗ": "오", "ㅛ": "요",
    "ㅜ": "우", "ㅠ": "유", "ㅡ": "으", "ㅣ": "이",
    "ㅐ": "애", "ㅒ": "얘", "ㅔ": "에", "ㅖ": "예",
    "ㅘ": "와", "ㅙ": "왜", "ㅚ": "외",
    "ㅝ": "워", "ㅞ": "웨", "ㅟ": "위", "ㅢ": "의",
}

def spell_jamo(text: str, style: str = "standard", sep: str = "") -> str:
    """
    자모만으로 이뤄진 문자열을 읽는 소리(명칭)로 변환.
    - style: "standard" 또는 "casual"
    - sep: 각 항목 사이 구분자(예: " ")
    """
    cons_map = STD_CONSONANTS if style == "standard" else CASUAL_CONSONANTS
    out = []
    for ch in text:
        if ch in cons_map:
            out.append(cons_map[ch])
        elif ch in VOWELS:
            out.append(VOWELS[ch])
        else:
            # 자모가 아니면 그대로 둠(필요 시 제거/치환 로직 추가)
            out.append(ch)
    return sep.join(out)

def spell_any_korean(text: str, style: str = "standard", sep: str = "") -> str:
    # 1) 한글 음절을 호환 자모로 변환
    jamo_text = j2hcj(h2j(text))
    # 2) 위에서 만든 변환 함수 재사용
    return spell_jamo(jamo_text, style=style, sep=sep)

print(spell_any_korean("안녕ㅋㅋ", style="casual"))
# 예) 아ㄴ녀ㅇ키윽키윽 → 자모만 골라서 처리하려면 필터링을 더해도 됩니다.

if __name__ == "__main__":
    print(spell_jamo("ㅋㅋㅇㅇ"))                 # 기본(표준): 키읔키읔이응이응
    print(spell_jamo("ㅋㅋㅇㅇ", style="casual")) # 구어체: 키윽키윽이응이응
    print(spell_jamo("ㅏㅣㅗ", sep=" "))          # 아 이 오
    print(spell_any_korean("안녕ㅋㅋ", style="casual"))
    # 예) 아ㄴ녀ㅇ키윽키윽 → 자모만 골라서 처리하려면 필터링을 더해도 됩니다.
