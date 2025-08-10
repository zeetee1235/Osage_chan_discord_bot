
# -*- coding: utf-8 -*-
from typing import Dict
from jamo import h2j, j2hcj

# 표준 명칭(국립국어원 표기 관행에 맞춘 형태)
STD_CONSONANTS: Dict[str, str] = {
    "ㄱ": "기역", "ㄲ": "쌍기역", "ㄴ": "니은", "ㄷ": "디귿", "ㄸ": "쌍디귿",
    "ㄹ": "리을", "ㅁ": "미음", "ㅂ": "비읍", "ㅃ": "쌍비읍", "ㅅ": "시옷",
    "ㅆ": "쌍시옷", "ㅇ": "이응", "ㅈ": "지읒", "ㅉ": "쌍지읒", "ㅊ": "치읓",
    "ㅋ": "키윽", "ㅌ": "티윽", "ㅍ": "피읍", "ㅎ": "히읗",
}

# 구어체(키윽/티윽/피읍 등)
CASUAL_CONSONANTS: Dict[str, str] = {
    **STD_CONSONANTS,
    "ㅋ": "키윽",
    "ㅌ": "티윽",
    "ㅍ": "피읍",
}

VOWELS: Dict[str, str] = {
    "ㅏ": "아", "ㅑ": "야", "ㅓ": "어", "ㅕ": "여", "ㅗ": "오", "ㅛ": "요",
    "ㅜ": "우", "ㅠ": "유", "ㅡ": "으", "ㅣ": "이",
    "ㅐ": "애", "ㅒ": "얘", "ㅔ": "에", "ㅖ": "예",
    "ㅘ": "와", "ㅙ": "왜", "ㅚ": "외",
    "ㅝ": "워", "ㅞ": "웨", "ㅟ": "위", "ㅢ": "의",
}

def spell_jamo(text: str, style: str = "casual", sep: str = "") -> str:
    cons_map = CASUAL_CONSONANTS if style == "casual" else STD_CONSONANTS
    out = []
    for ch in text:
        if ch in cons_map:
            out.append(cons_map[ch])
        elif ch in VOWELS:
            out.append(VOWELS[ch])
        else:
            out.append(ch)
    return sep.join(out)

def spell_any_korean(text: str, style: str = "casual", sep: str = "") -> str:
    def is_hangul_syllable(ch):
        return 0xAC00 <= ord(ch) <= 0xD7A3
    out = []
    for ch in text:
        if is_hangul_syllable(ch):
            out.append(ch)
        elif ch in STD_CONSONANTS or ch in VOWELS:
            out.append(spell_jamo(ch, style=style))
        else:
            out.append(ch)
    return sep.join(out)

if __name__ == "__main__":
    print(spell_jamo("ㅋㅋㅇㅇ"))                 # 키윽키윽이응이응
    print(spell_jamo("ㅋㅋㅇㅇ", style="standard")) # 표준: 키읔키읔이응이응
    print(spell_jamo("ㅏㅣㅗ", sep=" "))          # 아 이 오
    print(spell_any_korean("안녕ㅋㅋ", style="casual")) # 안녕키윽키윽
