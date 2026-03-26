"""
Lyric Analyzer — rhyme scheme detection, rhythm/meter analysis,
and improvement suggestions for English and Chinese lyrics.
"""

import re
import pronouncing
from pypinyin import pinyin, Style


# ── Chinese finals that share rhyme groups (十三辙 / Shísān Zhé) ─────────
CHINESE_RHYME_GROUPS = {
    "发花": ["a", "ia", "ua"],
    "梭波": ["o", "uo", "e"],
    "乜斜": ["ie", "ue", "üe"],
    "姑苏": ["u"],
    "衣期": ["i", "ü", "er"],
    "怀来": ["ai", "uai"],
    "灰堆": ["ei", "ui", "uei"],
    "遥条": ["ao", "iao"],
    "由求": ["ou", "iu", "iou"],
    "言前": ["an", "ian", "uan", "üan"],
    "人辰": ["en", "in", "un", "ün"],
    "江阳": ["ang", "iang", "uang"],
    "中东": ["eng", "ing", "ong", "iong"],
}

_FINAL_TO_GROUP: dict[str, str] = {}
for group, finals in CHINESE_RHYME_GROUPS.items():
    for f in finals:
        _FINAL_TO_GROUP[f] = group


def get_chinese_final(char: str) -> str | None:
    py = pinyin(char, style=Style.FINALS, heteronym=False)
    if py and py[0]:
        return py[0][0]
    return None


def chinese_rhyme_group(char: str) -> str | None:
    final = get_chinese_final(char)
    if final is None:
        return None
    return _FINAL_TO_GROUP.get(final)


def last_chinese_char(line: str) -> str | None:
    chars = [c for c in line.strip() if "\u4e00" <= c <= "\u9fff"]
    return chars[-1] if chars else None


def analyze_chinese_rhyme(lines: list[str]) -> dict:
    results = []
    for line in lines:
        ch = last_chinese_char(line)
        if ch:
            final = get_chinese_final(ch)
            group = chinese_rhyme_group(ch)
            py = pinyin(ch, style=Style.TONE, heteronym=False)[0][0]
            results.append({
                "line": line.strip(),
                "end_char": ch,
                "pinyin": py,
                "final": final,
                "rhyme_group": group,
            })
        else:
            results.append({
                "line": line.strip(),
                "end_char": None,
                "pinyin": None,
                "final": None,
                "rhyme_group": None,
            })
    return {"lines": results, "scheme": _derive_chinese_scheme(results)}


def _derive_chinese_scheme(results: list[dict]) -> str:
    group_map: dict[str | None, str] = {}
    label = ord("A")
    scheme = []
    for r in results:
        g = r["rhyme_group"]
        if g is None:
            scheme.append("?")
            continue
        if g not in group_map:
            group_map[g] = chr(label)
            label += 1
        scheme.append(group_map[g])
    return "-".join(scheme)


# ── English rhyme helpers ────────────────────────────────────────────────

def last_word(line: str) -> str | None:
    words = re.findall(r"[a-zA-Z']+", line)
    return words[-1].lower() if words else None


def english_rhymes_with(w1: str, w2: str) -> bool:
    if w1 == w2:
        return True
    phones1 = pronouncing.phones_for_word(w1)
    phones2 = pronouncing.phones_for_word(w2)
    if not phones1 or not phones2:
        return _simple_english_rhyme(w1, w2)
    rp1 = pronouncing.rhyming_part(phones1[0])
    rp2 = pronouncing.rhyming_part(phones2[0])
    return rp1 == rp2


def _simple_english_rhyme(w1: str, w2: str) -> bool:
    """Fallback: check if last 2+ chars match."""
    min_len = min(len(w1), len(w2))
    if min_len < 2:
        return False
    return w1[-2:] == w2[-2:]


def analyze_english_rhyme(lines: list[str]) -> dict:
    words = [last_word(l) for l in lines]
    n = len(words)
    labels: list[str | None] = [None] * n
    label = ord("A")

    for i in range(n):
        if words[i] is None:
            labels[i] = "?"
            continue
        if labels[i] is not None:
            continue
        labels[i] = chr(label)
        for j in range(i + 1, n):
            if words[j] is None:
                continue
            if labels[j] is not None:
                continue
            if english_rhymes_with(words[i], words[j]):
                labels[j] = chr(label)
        label += 1

    results = []
    for i, line in enumerate(lines):
        results.append({
            "line": line.strip(),
            "end_word": words[i],
            "label": labels[i],
        })
    return {"lines": results, "scheme": "-".join(labels)}


# ── Syllable / stress helpers ────────────────────────────────────────────

FUNCTION_WORDS = {
    "a", "an", "the", "and", "but", "or", "nor", "for", "yet", "so",
    "in", "on", "at", "to", "of", "by", "as", "is", "am", "are",
    "was", "were", "be", "been", "do", "does", "did", "has", "have",
    "had", "will", "would", "shall", "should", "may", "might", "can",
    "could", "must", "if", "than", "that", "with", "from", "into",
    "up", "out", "it", "its", "my", "your", "his", "her", "our",
    "their", "me", "him", "us", "them", "who", "whom", "which",
    "this", "these", "those", "not", "no", "i", "we", "you", "he",
    "she", "they", "i'm", "i've", "i'll", "i'd", "he's", "she's",
    "it's", "we're", "they're", "you're", "don't", "doesn't",
    "didn't", "won't", "wouldn't", "can't", "couldn't", "shouldn't",
}


def syllable_count(word: str) -> int:
    phones = pronouncing.phones_for_word(word.lower())
    if phones:
        return pronouncing.syllable_count(phones[0])
    return _approx_syllables(word)


def _approx_syllables(word: str) -> int:
    word = word.lower().strip()
    vowels = "aeiouy"
    count = 0
    prev_vowel = False
    for ch in word:
        if ch in vowels:
            if not prev_vowel:
                count += 1
            prev_vowel = True
        else:
            prev_vowel = False
    if word.endswith("e") and count > 1:
        count -= 1
    return max(count, 1)


def stressed_syllable_count(word: str) -> int:
    """Count primary (1) and secondary (2) stressed syllables in a word."""
    phones = pronouncing.phones_for_word(word.lower())
    if phones:
        return sum(1 for p in phones[0].split() if p[-1] in "12")
    return max(1, _approx_syllables(word))


def is_function_word(word: str) -> bool:
    return word.lower().strip("',.-!?") in FUNCTION_WORDS


def line_syllable_count(line: str) -> int:
    words = re.findall(r"[a-zA-Z']+", line)
    return sum(syllable_count(w) for w in words)


def line_stressed_count(line: str) -> int:
    """Count stressed syllables in a line (line length for songwriting).

    Function words (a, the, is, was, etc.) are treated as unstressed
    in connected speech, even though CMU dict marks them with stress
    in citation form.
    """
    words = re.findall(r"[a-zA-Z']+", line)
    count = 0
    for w in words:
        if is_function_word(w):
            continue
        count += stressed_syllable_count(w)
    return count


def analyze_rhythm(lines: list[str]) -> list[dict]:
    results = []
    for line in lines:
        total = line_syllable_count(line)
        stressed = line_stressed_count(line)
        results.append({
            "line": line.strip(),
            "syllables": total,
            "stressed": stressed,
        })
    return results


# ── High-level analysis ─────────────────────────────────────────────────

def analyze_song_section(title: str, lines: list[str], language: str = "en") -> dict:
    if language == "zh":
        rhyme = analyze_chinese_rhyme(lines)
    else:
        rhyme = analyze_english_rhyme(lines)

    rhythm = analyze_rhythm(lines) if language == "en" else None
    return {"title": title, "language": language, "rhyme": rhyme, "rhythm": rhythm}


# ── Demo / CLI ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== TWO STORY HOUSE — Verse ===")
    verse_lines = [
        "How long have we known each other",
        "Since I met you the first time",
        "When you asked me if I was alone",
        "I came to your two story house across the city",
        "So crowded we could barely move",
    ]
    result = analyze_song_section("Two Story House Verse", verse_lines, "en")
    print(f"Rhyme scheme: {result['rhyme']['scheme']}")
    for r in result["rhythm"]:
        print(f"  {r['stressed']:2d} stressed ({r['syllables']:2d} total) | {r['line']}")

    print("\n=== TWO STORY HOUSE — Chorus ===")
    chorus_lines = [
        "In the two story house",
        "In the two story house",
        "We spend our time and life",
        "We share our hurt and joy",
        "In the two story house",
        "In the two story house",
        "We love it so much, We hate it so much",
        "We lose our minds, yet find our home",
    ]
    result = analyze_song_section("Two Story House Chorus", chorus_lines, "en")
    print(f"Rhyme scheme: {result['rhyme']['scheme']}")
    for r in result["rhythm"]:
        print(f"  {r['stressed']:2d} stressed ({r['syllables']:2d} total) | {r['line']}")

    print("\n=== FOOL'S GOLD — Verse ===")
    fg_verse = [
        "I've been told I'm a fool",
        "I only chase after what's new",
        "I can't seem to love anyone but you",
        "For now",
        "Guess that's why they call me a fool",
    ]
    result = analyze_song_section("Fool's Gold Verse", fg_verse, "en")
    print(f"Rhyme scheme: {result['rhyme']['scheme']}")
    for r in result["rhythm"]:
        print(f"  {r['stressed']:2d} stressed ({r['syllables']:2d} total) | {r['line']}")

    print("\n=== FOOL'S GOLD — Chorus ===")
    fg_chorus = [
        "I'm a fool, I'm a fool",
        "Can't help fallin' for you",
        "You're perfect in every way",
        "But I'm a fool, I'm a fool",
        "'Cause when I hold on to you",
        "All that glitters fades away",
    ]
    result = analyze_song_section("Fool's Gold Chorus", fg_chorus, "en")
    print(f"Rhyme scheme: {result['rhyme']['scheme']}")
    for r in result["rhythm"]:
        print(f"  {r['stressed']:2d} stressed ({r['syllables']:2d} total) | {r['line']}")

    print("\n=== 再见的另一面 ===")
    cn_lines = [
        "最后他们也没有再见",
        "想念在开始就发了芽",
        "她明知故问",
        "他不会回答",
        "这是意料之中的结果",
        "就忘却吧",
        "翻过一夜夜，一重重山",
        "她在岛上用夕阳填满时空的不安，一眼万年",
        "就熄灭吧",
        "翻过一页页，一列列",
        "他来到村庄车子惊起犬吠一片",
        "熄灭了烟看她笑颜",
        "繁星点点诉说着每个不眠的夜飞鸟经过蝴蝶的花丛",
        "它贪恋的不过是散落的果实",
        "一场没有再见的意外",
    ]
    result = analyze_song_section("再见的另一面", cn_lines, "zh")
    print(f"Rhyme scheme: {result['rhyme']['scheme']}")
    for r in result["rhyme"]["lines"]:
        if r["end_char"]:
            print(f"  {r['end_char']} ({r['pinyin']}) [{r['rhyme_group'] or '?'}] | {r['line'][:30]}...")
