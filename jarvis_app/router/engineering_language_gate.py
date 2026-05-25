from __future__ import annotations

"""Engineering language classifier for alpha.22.2F.

This module is classification-only. It never mutates Builder plans, never chooses
execution, and never calls any tool. Router gates consume its decision when they
need to decide whether engineering text is explanatory/help language or a safe
choose-tool ambiguity.
"""

import re
from dataclasses import dataclass
from typing import Any

from jarvis_v5.router.action_aliases import normalize_text


@dataclass(frozen=True)
class EngineeringLanguageDecision:
    matched: bool = False
    category: str = "none"  # engineering_help | engineering_unit_help | engineering_choose_tool | none
    engineering_category: str = "none"
    confidence: int = 0
    reason: str = "no_engineering_language_match"
    terms: tuple[str, ...] = ()
    tool_candidates: tuple[str, ...] = ()
    requires_clarification: bool = False

    def as_dict(self) -> dict[str, Any]:
        return {
            "matched": self.matched,
            "category": self.category,
            "engineering_category": self.engineering_category,
            "confidence": self.confidence,
            "reason": self.reason,
            "terms": list(self.terms),
            "tool_candidates": list(self.tool_candidates),
            "requires_clarification": self.requires_clarification,
            "plan_mutated": False,
        }


# Keep Builder quantity units separate from engineering reference units. These
# are not automatically valid Builder setup units; they are language/reference
# tokens unless the slot reducer explicitly supports them later.
_ENGINEERING_UNIT_PATTERNS: list[tuple[str, str]] = [
    ("mpa", r"\bmpa\b|\bmegapascal(?:s)?\b"),
    ("kpa", r"\bkpa\b|\bkilopascal(?:s)?\b"),
    ("pa", r"\bpa\b|\bpascal(?:s)?\b"),
    ("gpa", r"\bgpa\b|\bgigapascal(?:s)?\b"),
    ("psi", r"\bpsi\b|\bpounds?\s+per\s+square\s+inch\b"),
    ("ksi", r"\bksi\b"),
    ("psf", r"\bpsf\b|\bpounds?\s+per\s+square\s+foot\b"),
    ("plf", r"\bplf\b|\bpounds?\s+per\s+linear\s+foot\b|\bline\s+load\s+\d+(?:\.\d+)?\s*plf\b"),
    ("ksf", r"\bksf\b"),
    ("kn/m", r"\bkn\s*/\s*m\b|\bkilonewtons?\s+per\s+met(?:re|er)\b"),
    ("kn/m2", r"\bkn\s*/\s*m(?:2|²)\b|\bkn\s+per\s+square\s+met(?:re|er)\b"),
    ("kn/m3", r"\bkn\s*/\s*m(?:3|³)\b|\bunit\s+weight\b"),
    ("n/mm2", r"\bn\s*/\s*mm(?:2|²)\b"),
    ("kg/m3", r"\bkg\s*/\s*m(?:3|³)\b|\bkg\s+per\s+cubic\s+met(?:re|er)\b"),
    ("pcf", r"\bpcf\b|\bpounds?\s+per\s+cubic\s+foot\b"),
    ("l/s", r"\bl\s*/\s*s\b|\blit(?:re|er)s?\s+per\s+second\b"),
    ("gpm", r"\bgpm\b|\bgallons?\s+per\s+minute\b"),
    ("cfm", r"\bcfm\b|\bcubic\s+feet\s+per\s+minute\b"),
    ("m/s", r"\bm\s*/\s*s\b|\bmet(?:re|er)s?\s+per\s+second\b"),
    ("kip", r"\bkip(?:s)?\b"),
    ("kip-ft", r"\bkip\s*[- ]?ft\b|\bkip\s*feet\b"),
    ("ft", r"\bft\b|\bfeet\b|\bfoot\b"),
    ("sf", r"\bsf\b|\bsquare\s+feet\b|\bsquare\s+foot\b"),
    ("yd", r"\byd\b|\byard(?:s)?\b"),
    ("in", r"\bin\b|\binch(?:es)?\b"),
    ("kn", r"\bkn\b|\bkilonewton(?:s)?\b"),
    ("kn-m", r"\bkn\s*[·.-]?\s*m\b|\bkilonewton[- ]?met(?:re|er)(?:s)?\b"),
    ("m3/s", r"\bm(?:3|³)\s*/\s*s\b|\bcubic\s+met(?:re|er)s?\s+per\s+second\b"),
    ("mm", r"\bmm\b|\bmillimet(?:re|er)s?\b"),
    ("percent", r"\b\d+(?:\.\d+)?\s*%\b|\bpercent\b|\bdegrees?\b"),
    ("celsius", r"°\s*c\b|\bdeg(?:ree)?s?\s*c\b|\bcelsius\b"),
    ("fahrenheit", r"°\s*f\b|\bdeg(?:ree)?s?\s*f\b|\bfahrenheit\b"),
    ("w/m2k", r"\bw\s*/\s*m(?:2|²)\s*k\b|\bw\s+per\s+square\s+met(?:re|er)\s+k\b"),
    ("kgco2e", r"\bkg\s*co2e(?:\s*/\s*m(?:2|²))?\b|\bkgco2e(?:/m2)?\b"),
]

_ENGINEERING_TERM_PATTERNS: list[tuple[str, str]] = [
    ("concrete_strength", r"\b(?:compressive\s+strength|cylinder\s+strength|concrete\s+strength|f['’]?c|slump|water[-\s]+cement\s+ratio|air\s+content|aggregate|curing)\b"),
    ("steel_strength", r"\b(?:yield\s+(?:stress|strength)|tensile\s+strength|fy\b|ultimate\s+strength|modulus\s+of\s+elasticity|steel\s+grade)\b"),
    ("geometry_detail", r"\b(?:column\s+\d+\s*sq|column|beam|slab|footing|wall\s+thickness|setdown|upstand|downstand)\b"),
    ("reinforcement", r"\b(?:rebar|reinforcement|lap\s+length|development\s+length|bar\s+diameter|mesh|reo|[ntyr]\s*\d+\s+bar|r\s*\d+\s+links?|stirrups?\s*@\s*\d+)\b"),
    ("structural_analysis", r"\b(?:bending\s+moment|moment|shear\s+force|shear|torque|deflection|drift|reaction|bearing\s+stress|punching\s+shear|buckling|torsion|axial\s+load|load\s+path|tributary\s+area|dead\s+load|live\s+load|wind\s+load|seismic\s+load)\b"),
    ("geotechnical", r"\b(?:bearing\s+(?:pressure|capacity)|settlement|cbr|california\s+bearing\s+ratio|dcp\s+test|proctor|atterberg|liquid\s+limit|plasticity\s+index|soil\s+classification|compaction|spt|n\s*value|groundwater|water\s+table|active\s+earth\s+pressure|passive\s+pressure|sheet\s+pile|retaining\s+wall|soil\s+friction\s+angle|friction\s+angle|unit\s+weight)\b"),
    ("civil_hydraulic", r"\b(?:stormwater|runoff|runoff\s+coefficient|culvert|invert\s+level|pipe\s+gradient|pipe\s+diameter|hydraulic\s+grade|flow\s+rate|flow|velocity|head\s+loss|pressure\s+head|manning\s+n|slope|catchment|swale|detention|retention|orifice|weir)\b"),
    ("pavement", r"\b(?:subgrade|subbase|basecourse|asphalt|bitumen|pavement|wearing\s+course|proof\s+roll|prime\s+coat|seal|dcp\s+test|california\s+bearing\s+ratio)\b"),
    ("drainage", r"\b(?:ag\s+drain|subsoil\s+drain|pit|headwall|outlet|surcharge|overland\s+flow|gross\s+pollutant|pipe\s+class\s+sn\d+|hdpe\s+pipe|rcp\s+pipe)\b"),
    ("survey_tolerance", r"\b(?:rl\b|reduced\s+level|datum|benchmark|setout|level\s+tolerance|flatness\s+ff|plumbness|grid\s+line\s+[a-z]/\d+|northing\s+easting|coordinates|tolerance|as\s+built|survey|control\s+point)\b"),
    ("temporary_works", r"\b(?:shoring|propping|scaffold|temporary\s+works|formwork\s+pressure|excavation\s+support|dewatering)\b"),
    ("sustainability", r"\b(?:embodied\s+carbon|operational\s+carbon|carbon|kgco2e|epd|environmental\s+product\s+declaration|energy\s+intensity|thermal\s+bridging|airtightness|solar\s+reflectance|voc|esd|green\s+star|nabers|recycled\s+content|low\s+carbon)\b"),
    ("report_code", r"\b(?:bca|ncc|j1v3|jv3|section\s+j|access\s+report|acoustic\s+report|fire\s+engineering\s+report|geotech\s+report|traffic\s+report|stormwater\s+report|temperature|thermal\s+movement|humidity|sound\s+rating|rw\s+rating|stc|fire\s+rating|frl|r-value|u-value)\b"),
    ("qs_review", r"\b(?:senior\s+qs|quantity\s+surveyor|takeoff\s+review|measurement\s+check|scope\s+gap|variation\s+assessment|consultant\s+query|tender\s+clarification)\b"),
    ("engineering_workflow", r"\b(?:engineering\s+units?|engineering\s+schedule|engineering\s+qa|engineering\s+paragraph|engineering\s+note|pressure\s+units?|structural\s+(?:terms?|notes?)|unit\s+issue)\b"),
    ("costx", r"\b(?:costx|xgetwallarea|xgetcount|xgetcustom|costx\s+function|count\s+function|live\s+excel\s+formula|excel\s+formula|formula\s+protection|unit\s+mismatch|unit\s+systems?|ft2|m2)\b"),
]

_EXPLANATION_VERBS = re.compile(
    r"\b(?:explain|what\s+is|what\s+does|what's|define|meaning\s+of|tell\s+me\s+about|how\s+does|how\s+should|why\s+is|describe)\b",
    re.I,
)
_CHOOSE_TOOL_VERBS = re.compile(r"\b(?:check|audit|review|compare|verify|validate|inspect|find|flag|normalize|process|choose)\b", re.I)
_TOOL_CONTEXT = re.compile(r"\b(?:engineering\s+units?|engineering\s+qa|pressure\s+units?|structural\s+(?:terms?|notes?)|unit\s+issue|values?\s+are\s+consistent|mixed\s+incorrectly|entries|boq|workbook|schedule|quantities|bearing\s+pressure|steel\s+fy|concrete\s+strength|engineering\s+schedule|engineering\s+units)\b", re.I)


def _matches(patterns: list[tuple[str, str]], text: str) -> list[tuple[str, str]]:
    found: list[tuple[str, str]] = []
    for label, pattern in patterns:
        if re.search(pattern, text, flags=re.I):
            found.append((label, pattern))
    return found


def classify_engineering_language(text: str) -> EngineeringLanguageDecision:
    normalized = normalize_text(text)
    if not normalized:
        return EngineeringLanguageDecision()

    unit_matches = _matches(_ENGINEERING_UNIT_PATTERNS, normalized)
    term_matches = _matches(_ENGINEERING_TERM_PATTERNS, normalized)
    labels = tuple(dict.fromkeys([label for label, _p in unit_matches + term_matches]))
    has_engineering_signal = bool(labels)
    if not has_engineering_signal:
        return EngineeringLanguageDecision()

    # Explanation wording wins over tool-choice wording. For example,
    # "How should a senior QS review quantities?" is help, not a tool run.
    if _EXPLANATION_VERBS.search(normalized):
        category = "engineering_unit_help" if unit_matches else "engineering_help"
        return EngineeringLanguageDecision(
            matched=True,
            category=category,
            engineering_category="unit" if unit_matches else (labels[0] if labels else "engineering"),
            confidence=94,
            reason=f"engineering_language:{category}",
            terms=labels,
            tool_candidates=(),
            requires_clarification=False,
        )

    if _CHOOSE_TOOL_VERBS.search(normalized) and _TOOL_CONTEXT.search(normalized):
        return EngineeringLanguageDecision(
            matched=True,
            category="engineering_choose_tool",
            engineering_category="unit_audit" if unit_matches else (labels[0] if labels else "engineering"),
            confidence=92,
            reason="engineering_language:choose_tool_ambiguity",
            terms=labels,
            tool_candidates=("qa_checker", "builder", "formatter"),
            requires_clarification=True,
        )

    # Treat engineering units/terms as explanatory/help language when they are
    # not explicit Builder slot edits. The router still checks slot-edit signals
    # before invoking this for active tasks.
    if unit_matches or term_matches:
        category = "engineering_unit_help" if unit_matches else "engineering_help"
        return EngineeringLanguageDecision(
            matched=True,
            category=category,
            engineering_category="unit" if unit_matches else (labels[0] if labels else "engineering"),
            confidence=94 if _EXPLANATION_VERBS.search(normalized) else 90,
            reason=f"engineering_language:{category}",
            terms=labels,
            tool_candidates=(),
            requires_clarification=False,
        )

    return EngineeringLanguageDecision()
