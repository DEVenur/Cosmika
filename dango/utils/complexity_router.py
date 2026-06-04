"""
complexity_router.py — rule-based query-complexity router for two-tier LLM
serving (fast model vs deep model).

Derived from the original three-layer design, with project-specific changes
validated against temp/router_eval.py and temp/router_history_eval.py:

  1. HISTORY-AWARE: conversation history feeds *topic* signals (keywords, code,
     math) but NOT *effort* signals (length, sentence count, symbol density).
     A follow-up to a hard topic escalates; a long prior answer does not inflate
     the current turn's length.
  2. CLOSER SUPPRESSION: acknowledgments / closers ("謝謝", "ok", "thanks",
     "감사", ...) are forced SIMPLE so they don't inherit history complexity.
     Closers are a CLOSED word class (unlike open-ended task verbs), so the
     list is stable and cheap to maintain.
  3. REASONING WEIGHT: open-ended why/how/explain questions are exactly what the
     deep model is for, so a single reasoning hit is enough to escalate.
  4. WIDER LANGUAGE COVERAGE: KO/RU/PT/VI/TH/AR added to the keyword sets.
  5. TRAP GUARDS: URLs are stripped before symbol/number scoring; arithmetic is
     detected as digit-operator-digit so prices/phones/dates don't false-fire.

Length is measured in tokens (tiktoken if available, else a script-aware
fallback). The host project can swap in its own tokenizer via set_token_counter.
"""

from __future__ import annotations
import re
import unicodedata
from dataclasses import dataclass, field
from typing import Callable

# --------------------------------------------------------------------------
# 1. LENGTH ESTIMATION (language-neutral, swappable)
# --------------------------------------------------------------------------

_TIKTOKEN = None
try:
    import tiktoken
    _TIKTOKEN = tiktoken.get_encoding("cl100k_base")
except Exception:
    _TIKTOKEN = None

_TOKEN_COUNTER: Callable[[str], float] | None = None


def set_token_counter(fn: Callable[[str], float] | None) -> None:
    """Inject a custom token counter (e.g. the host model's count_tokens).

    Routing only needs an approximate length, so the default fallback is fine;
    this exists so the project can reuse its built-in counter if desired.
    """
    global _TOKEN_COUNTER
    _TOKEN_COUNTER = fn


def _is_ideographic(ch: str) -> bool:
    """CJK ideographs, Japanese kana, Korean hangul -> ~1 token/char."""
    o = ord(ch)
    return (
        0x4E00 <= o <= 0x9FFF or   # CJK Unified
        0x3400 <= o <= 0x4DBF or   # CJK Ext A
        0x3040 <= o <= 0x30FF or   # Hiragana + Katakana
        0xAC00 <= o <= 0xD7A3 or   # Hangul syllables
        0xF900 <= o <= 0xFAFF      # CJK compat
    )


def estimate_tokens(text: str) -> float:
    """Approximate token count. Prefers an injected counter, then tiktoken,
    then a script-aware heuristic (~4 Latin chars/token, ~1.2 token/ideograph)."""
    if _TOKEN_COUNTER is not None:
        try:
            return float(_TOKEN_COUNTER(text))
        except Exception:
            pass
    if _TIKTOKEN is not None:
        return float(len(_TIKTOKEN.encode(text)))
    ideographic = sum(1 for ch in text if _is_ideographic(ch))
    others = sum(1 for ch in text if not ch.isspace() and not _is_ideographic(ch))
    return ideographic * 1.2 + others / 4.0


# --------------------------------------------------------------------------
# 2. SYMBOL / STRUCTURE PATTERNS (language-agnostic)
# --------------------------------------------------------------------------

URL = re.compile(r"https?://\S+|www\.\S+")
CODE_FENCE = re.compile(r"```")
INLINE_CODE_KEYWORDS = re.compile(
    r"\b(def|function|class|return|import|public\s+static|SELECT|INSERT|UPDATE|"
    r"DELETE|FROM|WHERE|console\.log|print\(|for\s*\(|while\s*\(|=>|::|->|"
    r"std::|#include|System\.out)\b"
)
LATEX = re.compile(r"\$[^$]+\$|\\\[|\\\]|\\frac|\\sum|\\int|\\sqrt|\\begin\{")

MATH_LOGIC_CHARS = set("∫∑√∏∂≤≥≠≈⇒→∞±×÷∧∨¬⊕≡∀∃∈∉⊂⊆⊃∇∮∝⟹⟺")
# ASCII chars that signal code/math when dense
ASCII_SYMBOLS = set("{}[]<>|&^%*/=~")

# arithmetic as digit-operator-digit ('-' excluded so phone numbers / date
# ranges like 0912-345 or 2024-03-15 don't false-trigger)
ARITH_EXPR = re.compile(r"\d\s*[+*/=^]\s*\d")

# date / time / version tokens (e.g. 2024/03/15, 3:00, 12.25) — these carry
# digits and slashes but are NOT math; stripped before effort scoring so prices
# and schedules don't read as arithmetic / dense-symbol queries.
DATE_TIME = re.compile(r"\b\d{1,4}[/:.\-]\d{1,4}(?:[/:.\-]\d{1,4})?\b")
# a digit-dot-digit decimal (so '.' inside numbers isn't a sentence boundary)
DECIMAL = re.compile(r"(\d)\.(\d)")

# terminal question marks across scripts (¿ is an *opening* mark -> ignored)
QMARKS = set("?？؟")

SENT_SPLIT = re.compile(r"[.!?。！？…\n]+")
DIGIT_GROUP = re.compile(r"\d+")


# --------------------------------------------------------------------------
# 3. MULTILINGUAL KEYWORD SETS
#    ascii entries are matched with word boundaries; non-ascii by substring.
# --------------------------------------------------------------------------

HARD_TASK_VERBS = {
    # EN
    "prove", "derive", "optimize", "optimise", "debug", "refactor",
    "analyze", "analyse", "differentiate", "integrate", "diagnose", "troubleshoot",
    # ZH
    "證明", "证明", "推導", "推导", "最佳化", "优化", "優化", "推理",
    "證成", "求導", "求导", "化簡", "化简", "演算", "除錯", "重構", "重构",
    # JA
    "証明", "導出", "最適化", "推論",
    # KO
    "증명", "도출", "최적화", "디버깅", "리팩토링", "리팩터링",
    # ES / FR / DE
    "demostrar", "demuestra", "optimizar", "optimiza",
    "démontrer", "prouve", "optimiser", "optimise",
    "beweise", "beweisen", "optimiere", "optimieren", "leite", "herleiten",
    # RU / PT / VI / TH / AR
    "докажи", "докажите", "оптимизируй", "выведи",
    "prova", "provar", "otimizar", "otimize", "deriva",
    "chứng minh", "tối ưu", "tối ưu hóa",
    "พิสูจน์", "เพิ่มประสิทธิภาพ",
    "أثبت", "برهن", "حسّن",
}

# 'design'/'analyze' style verbs kept separate (slightly softer, but still hard)
DESIGN_VERBS = {
    "design", "architect", "diseñar", "diseña", "concevoir", "conçois",
    "entwerfen", "entwirf", "設計", "设计", "分析", "設計する",
    "설계", "분석",                       # KO
    "thiết kế", "phân tích",              # VI
    "ออกแบบ", "วิเคราะห์",                  # TH
    "projete", "projetar",                # PT
}

CONDITIONAL = {
    "if", "suppose", "assume", "given that", "unless", "provided that",
    "假設", "假设", "如果", "倘若", "若", "前提", "given",
    "もし", "仮に",
    "만약", "가정",                        # KO
    "si", "supongamos", "supón",
    "falls", "angenommen", "wenn",
    "если", "предположим",                # RU
    "se", "suponha",                      # PT
    "nếu", "giả sử",                       # VI
    "ถ้า", "สมมติ",                         # TH
    "إذا", "افترض",                        # AR
}

COMPARISON = {
    "compare", "versus", "vs", "difference between", "tradeoff", "trade-off",
    "比較", "比较", "差異", "差异", "對比", "对比", "區別", "区别",
    "比較して", "違い",
    "비교", "차이",                        # KO
    "comparar", "diferencia entre",
    "comparer", "différence entre",
    "vergleiche", "unterschied zwischen",
    "сравни", "разница между",            # RU
    "compare entre", "diferença entre",   # PT
    "so sánh", "khác nhau",               # VI
    "เปรียบเทียบ", "ความแตกต่าง",            # TH
    "قارن", "الفرق بين",                   # AR
}

REASONING = {
    "why", "how come", "explain", "reason", "justify", "how does", "how do",
    "為什麼", "为什么", "為何", "为何", "如何", "怎麼", "怎么", "原因",
    "解釋", "解释", "說明", "说明", "為甚麼",
    "なぜ", "どうして", "説明",
    "왜", "어째서", "설명", "이유",          # KO
    "por qué", "cómo", "explica",
    "pourquoi", "comment", "explique",
    "warum", "wieso", "erkläre",
    "почему", "объясни", "зачем",         # RU
    "por que", "porque", "explique", "explica",  # PT
    "tại sao", "vì sao", "giải thích",    # VI
    "ทำไม", "อธิบาย", "เพราะอะไร",          # TH
    "لماذا", "اشرح", "كيف",                # AR
}

# tasks that are LONG but usually SIMPLE -> down-weight length
LOW_COMPLEXITY_TASKS = {
    "translate", "translation", "summarize", "summarise", "summary",
    "rephrase", "reformat", "format", "proofread", "spell check", "transcribe",
    "翻譯", "翻译", "摘要", "總結", "总结", "潤飾", "润色", "改寫", "改写",
    "校對", "校对", "排版", "格式化",
    "翻訳", "要約",
    "번역", "요약", "다듬", "교정",          # KO
    "traducir", "resumir",
    "traduire", "résumer", "résume",
    "übersetze", "zusammenfassen", "fasse zusammen",
    "переведи", "резюмируй",              # RU
    "traduz", "traduzir", "resuma", "resumir",  # PT
    "dịch", "tóm tắt",                     # VI
    "แปล", "สรุป",                          # TH
    "ترجم", "لخّص", "لخص",                  # AR
}


def _split_kw(kwset):
    ascii_kw, other_kw = [], []
    for kw in kwset:
        (ascii_kw if kw.isascii() else other_kw).append(kw)
    pat = None
    if ascii_kw:
        pat = re.compile(
            r"\b(" + "|".join(re.escape(k) for k in sorted(ascii_kw, key=len, reverse=True)) + r")\b",
            re.IGNORECASE,
        )
    return pat, other_kw


_KW = {
    name: _split_kw(s)
    for name, s in {
        "hard": HARD_TASK_VERBS, "design": DESIGN_VERBS, "cond": CONDITIONAL,
        "cmp": COMPARISON, "reason": REASONING, "lowtask": LOW_COMPLEXITY_TASKS,
    }.items()
}


def _count_keyword_hits(text: str, name: str) -> int:
    pat, other = _KW[name]
    n = 0
    if pat is not None:
        n += len(pat.findall(text))
    for kw in other:
        n += text.count(kw)
    return n


# --------------------------------------------------------------------------
# 3b. CLOSERS — closed word class; forced SIMPLE regardless of history
# --------------------------------------------------------------------------

CLOSERS = {
    # EN
    "ok", "okay", "okok", "thanks", "thank you", "thx", "ty", "got it",
    "gotcha", "cool", "nice", "great", "lol", "lmao", "np", "sure",
    "alright", "makes sense", "understood", "perfect", "awesome", "yep", "yup",
    # ZH
    "謝謝", "谢谢", "感謝", "感谢", "多謝", "多谢", "好喔", "好的", "好啦",
    "了解", "懂了", "知道了", "收到", "哈哈", "哈哈哈", "讚", "赞", "棒",
    "沒問題", "没问题", "可以", "嗯嗯", "好喲", "好",
    # JA
    "ありがとう", "ありがとうございます", "なるほど", "了解", "りょうかい",
    "わかった", "オッケー", "おけ", "さすが", "いいね",
    # KO
    "감사", "감사합니다", "고마워", "고맙습니다", "알겠어", "알겠습니다",
    "그렇구나", "오케이", "좋아", "굿",
    # ES / FR / DE
    "gracias", "vale", "perfecto", "genial", "entendido", "claro",
    "merci", "parfait", "super", "compris", "génial",
    "danke", "alles klar", "verstanden",
    # RU / PT / VI / TH / AR
    "спасибо", "понятно", "ясно", "отлично",
    "obrigado", "obrigada", "perfeito", "entendi", "valeu",
    "cảm ơn", "hiểu rồi", "tuyệt",
    "ขอบคุณ", "โอเค", "เข้าใจแล้ว",
    "شكرا", "تمام", "حسنا",
}
_CLOSERS_SORTED = sorted((c.lower() for c in CLOSERS), key=len, reverse=True)


def _is_closer(text: str) -> bool:
    """True when the message is essentially just an acknowledgment / closer.

    Strips punctuation, symbols (incl. emoji), separators and digits, then peels
    off known closer phrases. If almost nothing remains, it's a closer. A length
    guard prevents long messages that merely contain a closer substring from
    qualifying (e.g. '謝謝你幫我看這段程式碼')."""
    core = "".join(
        ch for ch in text.lower()
        if not (unicodedata.category(ch)[0] in ("P", "S", "Z", "C") or ch.isdigit())
    )
    if not core or len(core) > 20:
        return False
    remaining = core
    for c in _CLOSERS_SORTED:
        if c in remaining:
            remaining = remaining.replace(c, "")
    return len(remaining) <= 1


# --------------------------------------------------------------------------
# 4. CLASSIFIER
# --------------------------------------------------------------------------

@dataclass
class Result:
    decision: str                       # 'simple' | 'complex'
    route: str                          # 'small' | 'large'
    score: float
    band: str                           # 'low' | 'gray' | 'high' | 'override' | 'closer'
    hard_rules: list = field(default_factory=list)
    signals: dict = field(default_factory=dict)
    tokens: float = 0.0


def classify(
    text: str,
    history: list[str] | None = None,
    t_low: float = 2.5,
    t_high: float = 4.0,
    history_turns: int = 2,
) -> Result:
    # ---- Layer 0: closer suppression (current message only) ----------
    # A bare acknowledgment must not inherit the prior topic's complexity.
    if _is_closer(text):
        return Result("simple", "small", 0.0, "closer", [], {"closer": True},
                      estimate_tokens(text))

    # `full` carries TOPIC signals across recent turns; `cur` measures the
    # EFFORT of the current turn (length / structure / arithmetic).
    ctx = ""
    if history:
        ctx = " ".join(history[-history_turns:]) + " "
    full = ctx + text
    cur = text
    low_full = full.lower()
    # effort signals run on a cleaned current turn: URLs and date/time/version
    # tokens removed so links and schedules don't read as dense math.
    cur_clean = DATE_TIME.sub(" ", URL.sub(" ", cur))

    tokens = estimate_tokens(cur)
    hard_rules = []

    # ---- Layer 1: hard overrides -------------------------------------
    # Topic signals (code/math/keywords) consider history; multi_question is
    # per-turn (two separate one-question turns is not a multi-question turn).
    if CODE_FENCE.search(full) or INLINE_CODE_KEYWORDS.search(full):
        hard_rules.append("code")
    if LATEX.search(full):
        hard_rules.append("latex")
    math_char_hits = sum(1 for ch in full if ch in MATH_LOGIC_CHARS)
    if math_char_hits >= 2:
        hard_rules.append("math_symbols")
    q_count_cur = sum(1 for ch in cur if ch in QMARKS)
    if q_count_cur >= 2:
        hard_rules.append("multi_question")
    if _count_keyword_hits(low_full, "hard") >= 1:
        hard_rules.append("hard_verb")
    if _count_keyword_hits(low_full, "design") >= 1:
        hard_rules.append("design_verb")
    constraint_hits = len(re.findall(
        r"\b(must|cannot|can't|should not|required|necessario)\b", low_full
    )) + low_full.count("必須") + low_full.count("必须") + low_full.count("不能") + low_full.count("不可")
    if constraint_hits >= 3:
        hard_rules.append("constraints")

    if hard_rules:
        return Result("complex", "large", float("inf"), "override",
                      hard_rules, {"q_count": q_count_cur, "math_chars": math_char_hits},
                      tokens)

    # ---- Layer 2: weighted score -------------------------------------
    # EFFORT signals: current turn only.
    len_pts = max(0.0, min(3.0, (tokens - 20) / 30.0))

    sym = sum(1 for ch in cur_clean if ch in ASCII_SYMBOLS or ch in MATH_LOGIC_CHARS)
    density = sym / max(estimate_tokens(cur_clean), 1.0)
    sym_pts = max(0.0, min(2.0, (density - 0.05) * 20))

    # mask decimals so '.' inside numbers (3.2, 42,000.50) isn't a sentence break
    sents = [s for s in SENT_SPLIT.split(DECIMAL.sub(r"\1\2", cur_clean)) if s.strip()]
    sent_pts = max(0.0, min(2.0, (len(sents) - 1) * 0.5))

    # TOPIC signals: consider history.
    cond_pts = min(2.0, _count_keyword_hits(low_full, "cond") * 1.0)
    cmp_pts = 1.5 if _count_keyword_hits(low_full, "cmp") >= 1 else 0.0
    # Reasoning is a strong "deep model" signal: one hit is enough to escalate.
    reason_pts = min(4.0, _count_keyword_hits(low_full, "reason") * 2.5)

    # numeric: symbolic arithmetic (digit-op-digit), OR a "word problem"
    # (several numbers + a question mark, carried in prose). Current turn only.
    num_groups = len(DIGIT_GROUP.findall(cur_clean))
    if ARITH_EXPR.search(cur_clean):
        num_pts = 1.0
    elif num_groups >= 3 and q_count_cur >= 1:
        num_pts = 1.5
    else:
        num_pts = 0.0

    # low-complexity tasks (translate/summarize/reformat): bulk length is NOT
    # evidence of complexity. Detected on the current turn.
    lowtask = _count_keyword_hits(cur.lower(), "lowtask") >= 1
    if lowtask:
        len_pts = 0.0
        sent_pts = 0.0
        num_pts = 0.0

    score = len_pts + sym_pts + sent_pts + cond_pts + cmp_pts + reason_pts + num_pts
    score = max(0.0, score)

    signals = {
        "len_pts": round(len_pts, 2), "sym_pts": round(sym_pts, 2),
        "sent_pts": round(sent_pts, 2), "cond_pts": round(cond_pts, 2),
        "cmp_pts": round(cmp_pts, 2), "reason_pts": round(reason_pts, 2),
        "num_pts": round(num_pts, 2), "lowtask": lowtask,
        "sym_density": round(density, 3), "sentences": len(sents),
        "has_history": bool(history),
    }

    # ---- Layer 3: hysteresis band ------------------------------------
    if score >= t_high:
        return Result("complex", "large", round(score, 2), "high", [], signals, tokens)
    if score <= t_low:
        return Result("simple", "small", round(score, 2), "low", [], signals, tokens)
    # gray zone -> default complex (misrouting hard->small is the costly error)
    return Result("complex", "large", round(score, 2), "gray", [], signals, tokens)
