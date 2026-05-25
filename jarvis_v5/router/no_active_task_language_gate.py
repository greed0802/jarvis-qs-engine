from __future__ import annotations

"""Single owner for no-active-task language routing in alpha.22.2C.

This module is intentionally side-effect free. It classifies plain language when
there is no active task, no pending clarification, and no attachment binding.
It does not mutate Builder plans, bind attachments, call engines, or create
files. MainRouter is the only caller that may turn a decision into a task shell.
"""

import re
from dataclasses import dataclass
from typing import Any

from jarvis_v5.router.action_aliases import normalize_text
from jarvis_v5.router.engineering_language_gate import classify_engineering_language


@dataclass(frozen=True)
class NoActiveTaskLanguageDecision:
    matched: bool = False
    category: str = "none"  # writing_help | casual_non_tool | generic_choose_tool | prompt_injection_safe_block | soft_builder_start | general_qs_help | none
    route: str = "no_decision"  # general_stub | choose_tool | no_active_prompt_injection_safe_block | new_builder_task_shell | no_decision
    intent: str = "GENERAL"
    confidence: int = 0
    reason: str = "no_language_gate_match"
    alias: str | None = None
    region_hint: str | None = None
    requires_setup: bool = False
    requires_clarification: bool = False
    tool_candidates: tuple[str, ...] = ()
    public_negative_guard: str | None = None
    negative_guard_detail: str | None = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "matched": self.matched,
            "category": self.category,
            "route": self.route,
            "intent": self.intent,
            "confidence": self.confidence,
            "reason": self.reason,
            "tool_candidates": list(self.tool_candidates),
            "requires_setup": self.requires_setup,
            "requires_clarification": self.requires_clarification,
        }
        if self.alias:
            payload["alias"] = self.alias
        if self.region_hint:
            payload["region_hint"] = self.region_hint
        if self.public_negative_guard:
            payload["negative_guard"] = self.public_negative_guard
        if self.negative_guard_detail:
            payload["negative_guard_detail"] = self.negative_guard_detail
        return payload


def _strip_language_wrappers(normalized: str) -> str:
    cleaned = normalized or ""
    cleaned = re.sub(r"^[,\s]*(?:please|safely|no engine|before anything else|for this active task|in jarvis|as a qs command)[:,\s]+", "", cleaned)
    cleaned = re.sub(r"\s+(?:please|with approval first|in the current workflow|and keep no-engine safety|but do not read workbook|before export|do not fallback|but do not export yet|but only if it is safe)\.?$", "", cleaned)
    cleaned = re.sub(r"\s+—\s+do not fallback$", "", cleaned)
    return cleaned.strip(" .,:")


_CREATE_VERBS = r"(?:create|prepare|make|build|start|begin|initiate|configure|initialize|set up|setup|generate|draft|produce|help me create|help me prepare|put together|help me put together)"
_QS_CONTEXT = r"(?:boq|bq|bill of quantities|schedule of values|schedule of quantities|schedule of works|trade schedule|trade measure schedule|measure schedule|quantity schedule|measurement schedule|tender boq|base sheet|costx|nrm|smm|takeoff|take off|priced boq|unpriced boq)"


def _has_negative_workbook_read_polarity(normalized: str) -> bool:
    """Detect no-active requests that explicitly forbid workbook reading.

    This lets safe Builder-shell setup phrases like "Create BOQ but do not read
    workbook contents" start a no-engine shell instead of being over-blocked as
    a direct content-read attack. It never permits workbook access.
    """
    return bool(
        re.search(
            r"\bdo\s+not\s+(?:read|open|parse|inspect|scan|extract)\b.*\b(?:workbook|cells?|formulas?|contents?)\b",
            normalized,
        )
        or re.search(
            r"\bwithout\s+(?:reading|opening|parsing|inspecting|scanning|extracting)\b.*\b(?:workbook|cells?|formulas?|contents?)\b",
            normalized,
        )
        or re.search(r"\bno\s+workbook\s+read\b", normalized)
        or re.search(r"\bnot\s+read\s+(?:the\s+)?workbook\s+contents?\b", normalized)
    )

_NEGATIVE_GUARD_PATTERNS: list[tuple[str, str, str]] = [
    (r"\brun\s+the\s+explanation\s+again\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\b(?:good\s+morning|good\s+afternoon|good\s+evening|hello|hi)\s+jarvis\b", "casual_non_tool_phrase", "greeting"),
    (r"\bcost\s+of\s+living\b", "casual_non_tool_phrase", "non_qs_cost_phrase"),
    (r"\bi\s+value\s+your\s+help\b", "casual_non_tool_phrase", "casual_value_phrase"),
    (r"\b(schedule|book|set|create|make)\s+(a\s+)?(meeting|call|appointment|reminder)\b", "casual_non_tool_phrase", "schedule_meeting"),
    (r"\bschedule\b.*\bworkbook\s+read\s+approval\b.*\b(?:later|tomorrow|next|future|schedule)\b", "casual_non_tool_phrase", "schedule_workbook_read_approval_for_later"),
    (r"\bschedule\b.*\bapproval\b.*\bfor\s+later\b", "casual_non_tool_phrase", "schedule_approval_for_later"),
    (r"\b(?:create|make|build|set\s+up|prepare)\s+(?:a\s+)?(?:study|learning|revision|discussion|work\s*day|personal)\s+schedule\b", "casual_non_tool_phrase", "schedule_planning_not_tool"),
    (r"\b(?:what\s+is|what's|what\s+does|define|explain|meaning\s+of|tell\s+me\s+about)\b.*\b(?:schedule\s+of\s+values|boq|bq|bill\s+of\s+quantities|estimate|cost\s+plan|value|cost|schedule)\b", "casual_non_tool_phrase", "definition_request"),
    (r"\bschedule\b.*\btasks?\s+in\s+order\b", "casual_non_tool_phrase", "schedule_planning_not_tool"),
    (r"\bwhat\s+is\s+the\s+cost\s+of\s+making\s+this\s+complex\b", "casual_non_tool_phrase", "value_cost_concept"),
    (r"\b(?:estimate|roughly\s+estimate|guess)\b.*\b(?:time|duration|how\s+long|effort|risk|complexity|learning\s+curve|tomorrow|too\s+early)\b", "casual_non_tool_phrase", "non_qs_estimate"),
    (r"\b(?:how\s+long|how\s+much\s+time|how\s+much\s+effort)\b", "casual_non_tool_phrase", "non_qs_estimate"),
    (r"\b(?:value|cost)\b.*\b(?:mean|meaning|idea|approach|effort|time|risk|worth|too\s+much)\b", "casual_non_tool_phrase", "value_cost_concept"),
    (r"\bformat\s+(?:this\s+|my\s+|the\s+)?(?:sentence|chat\s+reply|slack\s+reply|reply|paragraph|wording|text|message|email|explanation|note)\b", "format_text_not_workbook", "format_text_not_workbook"),
    (r"\bformat\s+(?:this\s+|my\s+|the\s+)?(?:engineering\s+)?(?:paragraph|note|comment|message|text)\s+only\b", "format_text_not_workbook", "format_text_not_workbook"),
    (r"\bnot\s+(?:a\s+)?(?:boq|bq|bill\s+of\s+quantities)\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\b(?:clean|clean\s+up|fix|improve|polish|rewrite|reword|make|turn)\b.*\b(?:sentence|reply|slack\s+reply|paragraph|wording|grammar|message|email|tone|text|explanation|note|comment|normal\s+english|professional)\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\b(?:fix|check|correct)\s+(?:my\s+|this\s+|the\s+)?(?:grammar|spelling|wording|sentence|reply|paragraph|message|note)\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\b(?:give\s+me\s+a\s+)?rough\s+estimate\s+of\s+(?:time|effort|risk|complexity)\b", "casual_non_tool_phrase", "non_qs_estimate"),
    (r"\b(?:estimate|roughly\s+estimate)\b.*\b(?:hard|difficulty)\b", "casual_non_tool_phrase", "non_qs_estimate"),
    (r"\bwhat\s+is\s+(?:my|the)\s+schedule\s+(?:today|tomorrow)?\b", "casual_non_tool_phrase", "schedule_planning_not_tool"),
    (r"\b(?:schedule|make|create|put|help\s+schedule)\b.*\b(?:explanation|discussion|reminder|learning\s+schedule|work\s+day|meeting\s+schedule|tasks\s+in\s+order|study\s+schedule)\b", "casual_non_tool_phrase", "schedule_planning_not_tool"),
    (r"\b(?:do\s+not\s+open\s+formatter|no\s+workbook\s+action|nothing\s+with\s+excel|wording\s+only|below\s+only)\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\btake\s+off\s+the\s+pressure\s+from\s+this\s+wording\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\bcreate\s+a\s+nicer\s+paragraph\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\bbuild\s+confidence\s+in\s+the\s+explanation\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\b(?:reply|sentence|paragraph|wording|text|message|email|explanation|note|comment|bug\s+report|issue\s+report)\b.*\b(?:not\s+the\s+workbook|not\s+the\s+boq|plain\s+english|less\s+harsh|professional|clearer|polished|cleaner|better)\b", "format_text_not_workbook", "writing_help_not_workbook"),
    (r"\b(?:make|rewrite|clean|polish|improve|fix)\b.*\b(?:bug\s+report|issue\s+report)\b.*\b(?:clearer|professional|better|cleaner|polished)?\b", "format_text_not_workbook", "writing_help_not_workbook"),
]


_ALIAS_PATTERNS: list[tuple[str, str, str | None, int]] = [
    (r"\bbill\s+of\s+quantities\b", "bill_of_quantities", None, 98),
    (r"\bboq\b", "boq", None, 98),
    (r"\bbq\b", "bq", None, 96),
    (r"\btender\s+boq\b", "tender_boq", None, 98),
    (r"\btrade\s+boq\b", "trade_boq", None, 97),
    (r"\b(costx|builder)\s+boq\b", "costx_boq", None, 97),
    (r"\bbase\s+sheet\b", "boq_base_sheet", None, 98),
    (r"\bboq\s+base\s+sheet\b", "boq_base_sheet", None, 99),
    (r"\bschedule\s+of\s+values\b", "schedule_of_values", "US", 98),
    (r"\bschedule\s+of\s+quantities\b", "schedule_of_quantities", None, 98),
    (r"\bschedule\s+of\s+works\b", "schedule_of_works", None, 96),
    (r"\btrade\s+schedule\b", "trade_schedule", None, 97),
    (r"\btrade\s+measure\s+schedule\b", "trade_measure_schedule", "NZ/AU", 96),
    (r"\bmeasure\s+schedule\b", "measure_schedule", "AU/NZ", 96),
    (r"\bquantity\s+schedule\b", "quantity_schedule", None, 97),
    (r"\bmeasurement\s+schedule\b", "measurement_schedule", None, 97),
    (r"\bpriced\s+boq\b", "priced_boq", None, 96),
    (r"\bunpriced\s+boq\b", "unpriced_boq", None, 96),
    (r"\bnrm(?:-style|\s+style)?\s+boq\b", "nrm_boq", "UK/AU", 96),
    (r"\bsmm(?:-style|\s+style)?\s+(?:schedule|boq)\b", "smm_schedule", "Singapore", 96),
    (r"\bireland\s+bq\b|\bbq\s+for\s+ireland\b", "ireland_bq", "Ireland", 96),
    (r"\bph(?:ilippines)?\s+bill\s+of\s+quantities\b|\bbill\s+of\s+quantities\s+for\s+(?:ph|philippines)\b", "ph_bill_of_quantities", "PH", 96),
    (r"\bnz\s+trade\s+schedule\b", "nz_trade_schedule", "NZ", 96),
    (r"\buae\s+tender\s+boq\b", "uae_tender_boq", "UAE", 96),
    (r"\bcanada\s+estimate\b", "canada_estimate", "Canada", 90),
    (r"\bglobal\s+qs\b.*\bsafe\s+builder\s+shell\b", "global_qs_safe_builder_shell", "global", 95),
]

_SOFT_REQUEST_PATTERNS = [
    r"^\s*(?:prepare|create|make|build|start|begin|initiate|configure|initialize|set\s+up|setup|put\s+together|draft|get)\b",
    r"\bcan\s+you\s+(?:help\s+me\s+)?(?:prepare|create|make|build|start|begin|initiate|configure|initialize|set\s+up|setup|put\s+together|draft|get)\b",
    r"\bcould\s+(?:you|we)\s+(?:prepare|create|make|build|start|begin|initiate|configure|initialize|set\s+up|setup|put\s+together|get)\b",
    r"\bplease\s+(?:prepare|create|make|build|start|begin|initiate|configure|initialize|set\s+up|setup|put\s+together|draft|get)\b",
    r"\b(?:i|we)\s+(?:need|want)\s+(?:a\s+|an\s+|to\s+)?(?:prepare|create|make|build|start|begin|initiate|configure|initialize|set\s+up|setup|put\s+together|draft|produce|get)?\b",
    r"\bhelp\s+me\s+(?:prepare|create|make|build|start|begin|initiate|configure|initialize|set\s+up|setup|put\s+together|get)\b",
]

_SOFT_QS_OBJECT_PATTERNS: list[tuple[str, str, int]] = [
    (r"\bsmm\s+measurement\s+shell\b", "smm_measurement_shell", 95),
    (r"\bcost\s+schedule\b", "cost_schedule", 95),
    (r"\bmeasurement\s+workbook\s+setup\b", "measurement_workbook_setup", 95),
    (r"\bconstruction\s+quantity\s+measurement\b", "construction_quantity_measurement", 95),
    (r"\bconstruction\s+cost\s+workbook\b", "construction_cost_workbook", 95),
    (r"\bquantity\s+measurement\s+schedule\b", "quantity_measurement_schedule", 95),
    (r"\bcontract-safe\s+builder\s+plan\b", "contract_safe_builder_plan", 95),
    (r"\bboq\b", "boq", 95),
    (r"\bbq\b", "bq", 94),
    (r"\bbill\s+of\s+quantities\b", "bill_of_quantities", 96),
    (r"\bschedule\s+of\s+values\b", "schedule_of_values", 96),
    (r"\bschedule\s+of\s+quantities\b", "schedule_of_quantities", 95),
    (r"\bquantity\s+schedule\b", "quantity_schedule", 95),
    (r"\btrade\s+schedule\b", "trade_schedule", 95),
    (r"\btrade\s+measure\s+schedule\b", "trade_measure_schedule", 95),
    (r"\bmeasure\s+schedule\b", "measure_schedule", 95),
    (r"\bmeasurement\s+schedule\b", "measurement_schedule", 94),
    (r"\bsteel\s+surface\s+area\s+measurement\b", "steel_surface_area_measurement", 95),
    (r"\bdoor(?:s)?\s+(?:and|/)?\s*window(?:s)?\s+count\s+schedule\b", "doors_windows_count_schedule", 95),
    (r"\breinforcement\s+weight\s+schedule\b", "reinforcement_weight_schedule", 95),
    (r"\bqs\s+estimate\s+workbook\s+shell\b", "qs_estimate_workbook_shell", 94),
    (r"\bqs\s+measurement\s+workbook\b", "qs_measurement_workbook", 95),
    (r"\b(?:multinational\s+)?qs\s+measurement\s+workflow\b", "qs_measurement_workflow", 95),
    (r"\bbuilder\s+task\b", "builder_task", 95),
    (r"\bboq\s+shell\b", "boq_shell", 95),
    (r"\bboq\s+workflow\b", "boq_workflow", 95),
    (r"\bboq\s+estimate\s+structure\b", "boq_estimate_structure", 95),
    (r"\btrade\s+cost\s+schedule\b", "trade_cost_schedule", 95),
    (r"\btender\s+value\s+summary\s+boq\b", "tender_value_summary_boq", 95),
    (r"\bqs\s+measurement\s+schedule\b", "qs_measurement_schedule", 95),
    (r"\bquantity\s+takeoff\s+workflow\b", "quantity_takeoff_workflow", 95),
    (r"\bbuilder\s+setup\b", "builder_setup", 95),
    (r"\bbuilder\s+shell\b", "builder_shell", 95),
    (r"\bsafe\s+builder\s+shell\b", "safe_builder_shell", 95),
    (r"\bengineering\s+quantit(?:y|ies)\b", "engineering_quantities", 94),
    (r"\bmeasurement\s+setup\b", "measurement_setup", 94),
    (r"\bexternal\s+works\b", "external_works_measurement", 94),
    (r"\btender\s+boq\b", "tender_boq", 96),
    (r"\bbase\s+sheet\b", "base_sheet", 95),
    (r"\bcostx\s+boq\b", "costx_boq", 95),
    (r"\bmeasurement\s+workbook\s+structure\b", "measurement_workbook_structure", 95),
    (r"\bquantity\s+workbook\s+structure\b", "quantity_workbook_structure", 95),
    (r"\bqs\s+workbook\s+structure\b", "qs_workbook_structure", 95),
    (r"\bmeasurement\s+file\s+structure\b", "measurement_file_structure", 94),
    (r"\bmeasured\s+works\s+schedule\b", "measured_works_schedule", 95),
    (r"\bboq\s+workbook\s+structure\b", "boq_workbook_structure", 95),
]

_GENERIC_TOOL_AMBIGUITY_PATTERNS: list[tuple[str, tuple[str, ...], str, int]] = [
    (r"\bformat\s+the\s+workbook\s+if\s+this\s+is\s+a\s+boq\b", ("formatter", "builder", "qa_checker"), "generic_tool_like:formatter_boq_workbook", 92),
    (r"^process\s+the\s+workbook\s+if\s+appropriate\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:workbook_workflow", 91),
    (r"^run\s+it,?\s+but\s+only\s+if\s+it\s+is\s+safe\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:run_safe", 91),
    (r"\buse\s+(?:the\s+)?formatter\b.*\bworkbook\b", ("formatter",), "generic_tool_like:formatter_workbook", 92),
    (r"\bprepare\b.*\bformatted\s+workbook\b", ("formatter",), "generic_tool_like:formatted_workbook", 92),
    (r"\bmake\b.*\bworkbook\s+layout\b.*\bconsistent\b", ("formatter",), "generic_tool_like:workbook_layout", 92),
    (r"\bcreate\s+the\s+thing\s+from\s+the\s+current\s+setup\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:create_from_current_setup", 91),
    (r"\brun\s+it\b.*\bsafe\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:run_safe", 91),
    (r"\bstart\s+the\s+tool\s+that\s+fits\s+this\s+task\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bcreate\s+an\s+output\b.*\bsetup\s+is\s+ready\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:create_output_when_ready", 91),
    (r"\bstart\s+whichever\s+jarvis\s+tool\s+is\s+appropriate\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bfind\b.*\b(?:inconsistent|missing|duplicate|wrong)\b.*\b(?:description|casing|unit|units|formula|formulas)\b", ("qa_checker", "formatter"), "generic_tool_like:qa_find_issue", 91),
    (r"\bprepare\b.*\bqa\s+discrepancy\s+report\b", ("qa_checker",), "generic_tool_like:qa_discrepancy_report", 91),
    (r"\bclean\b.*\bhead\s*1\b.*\bhead\s*2\b.*\bformatting\b", ("formatter",), "generic_tool_like:format_headings", 91),
    (r"\bcheck\b.*\bdescriptions?\b.*\b(?:missing|material|thickness|finish)\b", ("qa_checker", "description_helper"), "generic_tool_like:description_check", 91),
    (r"^build\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:build", 90),
    (r"^make\s+schedule\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:make_schedule", 90),
    (r"\bcompare\b.*\b(?:two|2|revised|revision|boq\s+files?|quantit(?:y|ies)|changes?)\b", ("compare_boq", "omission_addition", "qa_checker"), "generic_tool_like:compare_boq", 92),
    (r"\b(?:find|show|identify)\b.*\b(?:changes?|revised\s+quantit(?:y|ies)|revision)\b", ("compare_boq", "omission_addition", "qa_checker"), "generic_tool_like:revision_compare", 92),
    (r"\b(?:check|audit)\b.*\b(?:boq|workbook|formulas?|missing\s+units?|construction\s+workbook)\b", ("qa_checker", "builder", "formatter"), "generic_tool_like:qa_check", 92),
    (r"\b(?:format|clean)\b(?!.*\bboq\b).*\b(?:workbook|output\s+file)\b", ("formatter", "builder", "qa_checker"), "generic_tool_like:formatter_workbook", 92),
    (r"\bprocess\b.*\b(?:revision|revised|revision\s+file)\b", ("builder", "compare_boq", "omission_addition"), "generic_tool_like:revision_process", 92),
    (r"\bcreate\s+a\s+new\s+boq\s+from\s+this\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:create_from_this", 92),
    (r"\b(?:generate|create)\b.*\b(?:right|appropriate|correct)\s+(?:qs\s+)?output\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:qs_output", 92),
    (r"\b(?:initiate|run|perform)\b.*\b(?:suitable|relevant|applicable|analysis|workflow|workbook\s+operation)\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:applicable_workflow", 91),
    (r"\b(?:choose|identify|determine|select|resolve|classify)\b.*\b(?:tool|workflow|processing\s+path|mode|builder|formatter|qa)\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\b(?:use|pick)\s+(?:the\s+)?(?:right|proper|correct)\s+tool\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bdo\s+the\s+next\s+step\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:next_step", 90),
    (r"\b(?:can\s+you\s+)?handle\s+(?:this|the\s+attached\s+thing)\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:handle_this", 90),
    (r"\bcan\s+you\s+start\s+the\s+correct\s+jarvis\s+workflow\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bplease\s+process\s+the\s+workbook\s+if\s+appropriate\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:workbook_workflow", 91),
    (r"\bfigure\s+out\s+the\s+right\s+mode\s+first\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bcould\s+you\s+maybe\s+process\s+this.*\bright\s+tool\s+first\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bmaybe\s+compare\s+or\s+check\s+this.*\bcorrect\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bmake\s+something\s+from\s+this\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:create_from_this", 90),
    (r"\bstart\s+only\s+if\s+you\s+know\s+what\s+tool\s+is\s+needed\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"^(?:same|use this)$", ("builder",), "generic_tool_like:active_short_reply", 90),
    (r"^format$", ("formatter",), "generic_tool_like:format", 90),
    (r"\bcreate\s+something\s+from\s+this\s+file\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:create_from_file", 91),
    (r"\baudit\s+this\s+qs\s+file\b", ("qa_checker", "builder", "formatter"), "generic_tool_like:qs_file_audit", 91),
    (r"\bdo\s+the\s+next\s+tool\s+step\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:next_tool_step", 91),
    (r"\bcompare\s+this\s+file\b", ("compare_boq", "qa_checker", "builder"), "generic_tool_like:compare_file", 91),
    (r"\bprocess\s+this\s+construction\s+document\b", ("client_document_reader", "builder", "qa_checker"), "generic_tool_like:construction_document", 91),
    (r"^compare(?:\s+(?:this|it|these|the\s+file|the\s+workbook))?\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:compare", 90),
    (r"^check(?:\s+(?:this|it|these|the\s+file|the\s+workbook))?\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:check", 90),
    (r"^(?:create|make)(?:\s+(?:one|it|this|that))?(?:\s+for\s+me)?\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:create", 90),
    (r"^run\s+(?:it|this|that|the\s+tool)\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:run", 90),
    (r"^start\s+(?:it|this|that|the\s+tool|tool)\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:start", 90),
    (r"^process\s+(?:this|it|this\s+file|the\s+file|this\s+workbook|the\s+workbook)\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:process", 90),
    (r"^do\s+this\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:do_this", 90),
    (r"\b(?:whatever|which|what)\s+tool\s+(?:makes\s+sense|this\s+needs|is\s+needed)\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bnot\s+sure\s+which\s+tool\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bchoose\s+(?:the\s+)?(?:proper|right|correct)\s+tool\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\b(?:workflow|processing\s+path|mode)\s+(?:fits|is\s+right|is\s+correct|makes\s+sense)\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:workflow_choice", 91),
    (r"\b(?:determine|select|classify)\b.*\b(?:correct|proper|right)\s+(?:jarvis\s+)?(?:tool|workflow|processing\s+path)\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:classify_tool", 91),
    (r"\btake\s+care\s+of\s+this\s+file\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:file_workflow", 90),
    (r"\bprocess\s+this\s+workbook\s+if\s+appropriate\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:workbook_workflow", 90),
    (r"\bwhatever\s+tool\s+makes\s+sense\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bwhichever\s+workflow\s+fits\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:workflow_choice", 91),
    (r"\bpick\s+the\s+(?:right|proper|correct)\s+jarvis\s+path\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:tool_choice", 91),
    (r"\bchoose\s+the\s+suitable\s+processing\s+path\b", ("builder", "formatter", "qa_checker"), "generic_tool_like:processing_path", 91),
    (r"^classify\s+this\s+task\s+first\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:classify_tool", 91),
    (r"^do\s+it\s+safely\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:do_it_safely", 91),
    (r"^work\s+on\s+this\s+attachment\.?$", ("builder", "formatter", "qa_checker"), "generic_tool_like:work_on_attachment", 91),
    (r"^what\s+tool\s+should\s+use\s+this\??$", ("builder", "formatter", "qa_checker"), "generic_tool_like:what_tool_should_use_this", 91),
]


_WORKBOOK_READ_POLICY_REVIEW_PATTERNS: list[tuple[str, str]] = [
    (r"\bworkbook\s+read\s+policy\b", "workbook_read_policy"),
    (r"\bworkbook\s+content\s+read\s+boundary\b", "workbook_content_read_boundary"),
    (r"\bpolicy\s+review\b.*\b(?:read(?:ing)?\s+)?(?:formulas?|cells?|workbook|dimensions?)\b", "policy_review_read_boundary"),
    (r"\b(?:check|show|review|explain|tell\s+me)\b.*\b(?:cell|formula|workbook|content|dimension|access|read)\b.*\b(?:policy|gate|boundary|allowed|next\s+gate|access\s+tier|can\s+be\s+read|read\s+yet)\b", "workbook_read_policy_question"),
    (r"\b(?:can\s+we|can\s+i|are\s+we\s+allowed\s+to|is\s+it\s+safe\s+to)\b.*\b(?:read|open|inspect)\b.*\b(?:workbook|cells?|formulas?|dimensions?|content)\b", "workbook_read_allowed_question"),
    (r"\bcheck\b.*\b(?:cells?|formulas?|workbook|dimensions?|content)\b.*\bcan\s+be\s+read\s+yet\b", "check_can_be_read_yet"),
    (r"\bbefore\s+reading\s+(?:the\s+)?workbook\b.*\bpolicy\b", "before_workbook_read_policy"),
    (r"\bsafe\s+next\s+gate\b.*\bbefore\s+reading\s+(?:the\s+)?workbook\b", "safe_next_gate_before_reading"),
    (r"\bwhat\s+is\s+allowed\b.*\bworkbook\s+read\s+policy\b", "workbook_read_allowed_policy"),
    (r"\brun\s+workbook\s+read\s+policy\s+review\b", "run_workbook_read_policy_review"),
    (r"\bcurrent\s+access\s+tier\b.*\bworkbook\s+read", "current_access_tier"),
    (r"\bblocked\s+workbook\s+read\s+operations\b", "blocked_workbook_read_operations"),
    (r"\bpolicy\s+review\s+only\b.*\bno\s+cells?\b", "policy_review_no_cells"),
    (r"^policy\s+review\s+please,\s*no\s+active\s+task\.?$", "policy_review_no_active_task"),
    (r"\bread\s+(?:the\s+)?workbook\s+policy\b.*\bnot\s+(?:the\s+)?workbook\b", "workbook_policy_not_workbook"),
    (r"\bworkbook\s+policy\b.*\bnot\s+(?:the\s+)?workbook\b", "workbook_policy_not_workbook"),
    (r"\bwhat\s+does\s+(?:cells_read|workbook_read|workbook_content_read|formulas_read|engine_called|excel_created|legacy_builder_called)\s+false\s+mean\??$", "safety_flag_false_explanation"),
    (r"\bexplain\b.*\b(?:cells_read|workbook_read|workbook_content_read|formulas_read|engine_called|excel_created|legacy_builder_called)\b", "safety_flag_explanation"),
    (r"\bvalue\s+engineering\b.*\bread\s+cells?\b.*\b(?:optimi[sz]e|reduce|check|cost)\b", "value_engineering_read_cells_policy"),
    (r"\bread\s+cells?\b.*\b(?:optimi[sz]e|reduce|check)\b.*\bcost\b", "read_cells_cost_policy"),
]

_SHEET_NAME_PROBE_AMBIGUITY_PATTERNS: list[tuple[str, str]] = [
    (r"\bsheet\s+names?\b", "sheet_names"),
    (r"\bworksheet\s+names?\b", "worksheet_names"),
    (r"\bworkbook\s+sheets?\b", "workbook_sheets"),
    (r"\b(?:workbook|boq|bq|summary\s+boq\s+rates?)\s+tabs?\b", "workbook_tabs"),
    (r"\btabs?\s+in\s+(?:this|the)\s+workbook\b", "tabs_in_workbook"),
    (r"\b(?:show|list|read\s+only|display|tell\s+me)\b.*\b(?:tabs?|worksheet\s+names?|sheet\s+names?)\b", "show_tabs_or_sheet_names"),
    (r"\b(?:probe|open|use)\b.*\b(?:sheet-name|sheet\s+name|sheet\s+names?|workbook\s+sheets?|worksheet\s+names?)\b", "probe_sheet_names"),
    (r"\bapproved\s+sheet-name\s+probe\b", "approved_sheet_name_probe"),
    (r"\bopen\s+(?:xlsx|workbook)\b.*\bmetadata\b.*\bsheet\s+names?\b", "xlsx_metadata_sheet_names"),
    (r"\bcan\s+you\s+show\s+boq\s+tabs?\b", "boq_tabs"),
    (r"\blist\s+summary\s+boq\s+rates?\s+sheets?\b", "summary_boq_rates_sheets"),
    (r"\bopen\s+(?:the\s+)?workbook\b.*\blist\s+sheets?\b", "open_workbook_list_sheets"),
]

_WORKBOOK_CONTENT_READ_SAFE_BLOCK_PATTERNS: list[tuple[str, str]] = [
    (r"\bforce\s+workbook_parse_enabled\s+true\b", "force_workbook_parse_enabled"),
    (r"\bset\s+cell_read_enabled\s+true\b", "set_cell_read_enabled_true"),
    (r"\bi\s+approve\s+reading\s+formulas?\s+now\b", "approve_formula_read_without_gate"),
    (r"\b(?:open|read|parse|scan|extract|list|get)\b.*\b(?:every\s+cell|all\s+cells?|cell\s+values?|rows?\s+and\s+columns?|formulas?|cached\s+values?|workbook\s+dimensions?|used\s+ranges?|workbook\s+contents?|boq\s+sheet\s+contents?|comments?|tables?|styles?)\b", "direct_workbook_content_read"),
    (r"\bread\s+cells?\b.*\b(?:preview|export|continue|now)\b", "read_cells_action"),
    (r"\bopen\s+(?:the\s+)?workbook\b.*\bread\s+cells?\b", "open_workbook_read_cells"),
]

_NO_ACTIVE_PROMPT_INJECTION_SAFE_BLOCK_PATTERNS: list[tuple[str, str]] = [
    (r"^system\s*:", "system_instruction_override"),
    (r"\bdeveloper\s+override\b", "developer_override"),
    (r"\bhidden\s+instruction\b", "hidden_instruction"),
    (r"\bignore\s+previous\s+instructions\b", "ignore_previous_instructions"),
    (r"\bforget\s+safety\s+locks\b", "forget_safety_locks"),
    (r"\bbypass\s+(?:the\s+)?preview\s+policy\b", "bypass_preview_policy"),
    (r"\breveal\s+(?:the\s+)?system\s+prompt\b", "reveal_system_prompt"),
    (r"\breveal\s+(?:the\s+)?raw\s+path\b", "reveal_raw_path"),
    (r"\b(?:saved_path|local_path)\b", "raw_path_key_request"),
    (r"\bopenpyxl\.load_workbook\b", "openpyxl_load_workbook_request"),
    (r"\brun\s+legacy\s+builder\b", "legacy_builder_request"),
    (r"\bcall\s+(?:the\s+)?builder\s+engine\b", "builder_engine_request"),
    (r"\bcreate\s+excel\b", "create_excel_request"),
    (r"\bdelete\s+outputs?\b", "delete_outputs_request"),
    (r"\bexecution\s+request\b", "execution_request"),
    (r"\buploaded\s+file\s+says\s+(?:you\s+must\s+)?export\s+now\b", "uploaded_file_instruction_export"),
    (r"\bset\s+workbook_read\s*=\s*true\b", "enable_workbook_read_request"),
    (r"\bparse\s+sheet\s+names\b", "parse_sheet_names_request"),
]


_GENERAL_QS_HELP_PATTERNS: list[tuple[str, str, int]] = [
    (r"^explain\s+safe\s+workbook\s+path\s+resolver\.?$", "safe_workbook_path_resolver_explanation", 92),
    (r"\b(?:need|give|create|prepare|make)\b.*\bchecklist\b.*\bwaterproofing\b", "waterproofing_checklist_help", 91),
    (r"\b(?:give|create|prepare|make)\b.*\bchecklist\b.*\btender\s+review\b", "tender_review_checklist", 91),
    (r"\bhow\s+should\s+i\s+ask\s+(?:a\s+)?consultant\b.*\bclarification\b", "consultant_clarification_guidance", 91),
    (r"\bexplain\b.*\b(?:not\s+to\s+guess|avoid\s+guessing)\b.*\b(?:ambiguous\s+)?trade\s+scope\b", "scope_guessing_guidance", 91),
    (r"\b(?:separate|identify|flag|explain|prepare)\b.*\b(?:included\s+scope|excluded\s+scope|conflicting\s+drawings|conflicting\s+specs?|tender\s+quer(?:y|ies)|unit/function\s+mismatch|procurement\s+package|grouping\s+risks?)\b", "senior_qs_risk_guidance", 91),
    (r"\bexplain\b.*\b(?:measurement|quantit(?:y|ies)|takeoff|take\s*off|risk\s+checks?|separation)\b", "general_qs_measurement_help", 91),
    (r"\bexplain\b.*\b(?:painting|excavation|disposal|floor\s+finishes|skirting|wall|ceiling|door|trim)\b.*\b(?:measurement|risk|separation|quantity)\b", "trade_measurement_explanation", 91),
    (r"\bhow\s+should\s+(?:a\s+)?senior\s+qs\s+review\s+quantit(?:y|ies)\b", "senior_qs_quantity_review", 92),
    (r"\bwhat\s+does\s+(?:m2|m3|lm|nr|no|t|kg)\s+mean\s+in\s+measurement\b", "measurement_unit_explanation", 92),
    (r"\bexplain\s+costx\s+functions?\s+generally\b", "costx_function_explanation", 92),
    (r"\bexplain\s+how\s+variations?\s+are\s+usually\s+checked\b", "variation_checking_explanation", 92),
    (r"\bwhat\s+should\s+i\s+ask\s+the\s+consultant\b", "consultant_question_guidance", 91),
    (r"\bexplain\s+omission\s+and\s+addition\s+workflow\b", "omission_addition_explanation", 91),
    (r"\b(?:senior\s+qs|quantity\s+surveyor|qs)\b.*\b(?:review|check|audit|advise|explain|guidance|workflow|quantities|measurement|variation|consultant)\b", "general_qs_help", 90),
    (r"\bavoid\s+guessing\s+scope\b", "scope_checking_guidance", 90),
    (r"\breplacement\s+mode\s+in\s+variation\s+work\b", "variation_replacement_mode", 90),
    (r"\b(?:acoustic|j1v3|jv3|access|fire\s+engineering|geotech|consultant)\s+report\b.*\b(?:qs|scope|risks?|check|read|checklist|output|affecting)\b", "consultant_report_qs_help", 90),
    (r"\bwhat\s+is\s+j1v3\b", "j1v3_explanation", 90),
    (r"\bexplain\s+tender\s+clarification\s+notes\b", "tender_clarification_notes", 90),
    (r"\b(?:omission\s+and\s+addition|o\s*&\s*a|o&a)\b.*\b(?:workbook|workflow|output|replacement\s+mode)\b", "omission_addition_planned_help", 90),
    (r"\bcreate\s+variation\s+schedule\s+from\s+two\s+workbooks\b", "variation_schedule_planned_help", 90),
    (r"\bprepare\s+document\s+reader\s+output\s+for\s+access\s+report\b", "document_reader_planned_help", 90),
    (r"\bextract\s+geotech\s+risks?\s+affecting\s+earthworks\b", "geotech_risk_help", 90),
    (r"\bfind\s+missing\s+scope\s+from\s+the\s+fire\s+engineering\s+report\b", "fire_report_scope_help", 90),
    (r"\bcreate\s+(?:a\s+)?consultant\s+report\s+checklist\b", "consultant_report_checklist", 90),
]



_REGISTRY_ADVISORY_PATTERNS: list[tuple[str, str, tuple[str, ...], int]] = [
    (r"\bwhat\s+should\s+i\s+measure\s+for\s+[a-z0-9 /&-]+\b", "qs_scope_advisory", ("qs_scope_advisor", "file_requirement_advisor", "rfi_generator"), 95),
    (r"\bwhat\s+files\s+do\s+i\s+need\s+for\s+[a-z0-9 /&-]+\b", "file_requirement_advisory", ("file_requirement_advisor", "qs_scope_advisor"), 95),
    (r"\bwhat\s+(?:rfi|rfis|clarification(?:s)?)\s+should\s+i\s+(?:ask|raise)\b", "rfi_template_advisory", ("rfi_generator", "qs_scope_advisor"), 94),
    (r"\bwhich\s+(?:tool|capability)\s+should\s+(?:handle|use|process)\b", "capability_advisory", ("future_tool_advisor",), 94),
    (r"\b(?:run|start|execute|use)\s+(?:o\s*&\s*a|o&a|omission\s+and\s+addition|qa\s+checker|formatter|document\s+reader)\b", "future_tool_status_advisory", ("future_tool_advisor",), 94),
    (r"\b(?:compare|process)\b.*\b(?:old|current)\b.*\b(?:revised|new)\b.*\bboq\b", "future_tool_status_advisory", ("future_tool_advisor", "omission_addition", "compare_boq", "qa_checker"), 94),
    (r"\bcheck\s+the\s+acoustic\s+report\b.*\b(?:walls?|glazing|doors?)\b", "consultant_report_advisory", ("client_document_reader", "qs_scope_advisor", "rfi_generator"), 94),
    (r"\bcreate\s+a\s+qa\s+report\b.*\bformula\s+mismatches\b", "future_tool_status_advisory", ("qa_checker",), 93),
    (r"\brun\s+qa\s+checker\b.*\bboq\b", "future_tool_status_advisory", ("qa_checker", "builder"), 93),
    (r"\bfind\s+missing\s+scope\b.*\bfire\s+engineering\s+report\b", "consultant_report_advisory", ("client_document_reader", "qs_scope_advisor", "rfi_generator"), 94),
    (r"\bextract\s+geotech\s+risks?\b.*\bearthworks\b", "consultant_report_advisory", ("client_document_reader", "qs_scope_advisor"), 94),
    (r"\bcreate\s+o\s*&?\s*a\s+output\b.*\breplacement\s+mode\b", "planned_workbook_tool_advisory", ("omission_addition", "compare_boq"), 93),
    (r"\b(?:extract|identify|summarize|review)\b.*\b(?:scope\s+risks?|scope\s+impacts?|council\s+consent|consent\s+conditions|stormwater\s+report|consultant\s+reports?|fire\s+engineering\s+report|external\s+works)\b", "consultant_report_advisory", ("client_document_reader", "qs_scope_advisor", "rfi_generator"), 94),
    (r"\b(?:prepare|create|generate)\b.*\bvariation\s+schedule\b.*\b(?:without\s+guessing|unmatched\s+rows?|replacement|summary)?\b", "variation_advisory", ("omission_addition", "compare_boq", "qa_checker"), 93),
    (r"\b(?:additions?\s+as\s+positive|omissions?\s+as\s+negative|deleted\s+scope|new\s+scope|replacement-style\s+variation|net\s+the\s+quantity\s+changes|old\s+and\s+revised\s+rows?)\b", "omission_addition_scope_advisory", ("omission_addition", "compare_boq", "qa_checker"), 93),
    (r"\b(?:audit|check|show)\b.*\b(?:builder\s+boundary|future\s+engine\s+boundary|legacy\s+builder\s+.*locked|engine\s+boundary)\b", "engine_boundary_status_advisory", ("builder", "engine_boundary_audit", "engine_preflight"), 92),
    (r"\brun\b.*\bsafe\s+diagnostic\b.*\b(?:without\s+engine\s+execution|no\s+engine)\b", "safe_diagnostic_advisory", ("debug_report", "engine_boundary_audit"), 92),
    (r"\bflag\b.*\bdescription\s+changes?\b.*\bsame\s+quantit", "omission_addition_scope_advisory", ("omission_addition", "compare_boq", "qa_checker"), 92),
    (r"\bmatch\s+items?\b.*\b(?:code|description|level|unit)\b", "omission_addition_matching_advisory", ("omission_addition", "compare_boq", "qa_checker"), 92),
    (r"\bcreate\b.*\bchange\s+log\b.*\brevised\s+scope\b", "omission_addition_change_log_advisory", ("omission_addition", "compare_boq"), 92),
    (r"\b(?:omission\s+and\s+addition|omissions?|additions?|adds?\s+and\s+deducts?|change\s+order|variation\s+claim|remeasurement|revised\s+quantit(?:y|ies)|revised\s+scope)\b.*\b(?:comparison|summary|backup|negative\s+quantit(?:y|ies)|positive\s+quantit(?:y|ies)|change\s+log|match\s+items?|description\s+changes?)\b", "omission_addition_scope_advisory", ("omission_addition", "compare_boq", "qa_checker"), 93),
    (r"\b(?:create|prepare|make|draft|generate)\b.*\b(?:checklist|scope\s+checklist|risk\s+register|query|queries)\b.*\b(?:council|da\s+consent|consent\s+conditions|drawing|drawings|specs?|scope)\b", "project_scope_advisory", ("qs_scope_advisor", "client_document_reader", "rfi_generator"), 92),
    (r"\b(?:create|prepare|make|draft|generate|give|show|list)\b.*\b(?:boq\s+)?(?:checklist|scope\s+checklist|risk\s+register|rfi\s+list|clarification\s+register)\b.*\b(?:report|consultant|fire|acoustic|access|j1v3|jv3|geotech|document|civil|drainage|scope)\b", "report_checklist_advisory", ("client_document_reader", "qs_scope_advisor", "rfi_generator"), 94),
    (r"\b(?:for|from|about)?\s*(?:fire|acoustic|access|j1v3|jv3|geotech|consultant|pdf|civil\s+drainage)\s+report\b.*\b(?:boq|items?|scope|checklist|risk|rfi|read|reader|extract|missing|affected|check)\b", "consultant_report_advisory", ("client_document_reader", "qs_scope_advisor", "rfi_generator"), 94),
    (r"\b(?:what\s+should\s+i\s+(?:check|measure)|what\s+files\s+do\s+i\s+need|measurement\s+checklist|qs\s+scope\s+advisory|scope\s+advisory|file\s+requirement|file\s+checklist)\b", "scope_or_file_requirement_advisory", ("qs_scope_advisor", "file_requirement_advisor", "rfi_generator"), 94),
    (r"\b(?:draft|create|prepare|generate|make|list)\b.*\b(?:rfi|rfis|request\s+for\s+information|clarification\s+(?:question|register|list))\b", "rfi_advisory", ("rfi_generator", "qs_scope_advisor"), 93),
    (r"\b(?:document\s+reader|client\s+document\s+reader|standards\s+knowledge\s+base|scope\s+advisor|rfi\s+generator)\b", "planned_registry_tool_advisory", ("client_document_reader", "standards_knowledge_base", "qs_scope_advisor", "rfi_generator"), 93),
    (r"\b(?:omission\s+and\s+addition|o\s*&\s*a|o&a|compare\s+boq|variation\s+schedule|change\s+order)\b.*\b(?:tool|workflow|workbook|planned|future|advisory|checklist|compare|from\s+two\s+workbooks)\b", "planned_workbook_tool_advisory", ("omission_addition", "compare_boq", "qa_checker"), 92),
    (r"\b(?:formatter|qa\s+checker|document\s+reader|o&a|omission\s+and\s+addition|compare\s+boq)\b.*\b(?:planned|future|disabled|available|metadata|no\s+execution|not\s+connected|advisory)\b", "future_tool_status_advisory", ("formatter", "qa_checker", "client_document_reader", "omission_addition", "compare_boq"), 92),
    (r"\b(?:boundary\s+audit|engine\s+preflight|preflight|kill\s+switch|execution\s+lock|legacy\s+builder\s+lock|no\s+engine\s+safety)\b", "engine_boundary_status_advisory", ("builder", "engine_boundary_audit", "engine_preflight"), 92),
    (r"\b(?:what\s+standards?\s+should\s+i\s+check|standards?\s+to\s+check|standards?\s+should\s+i\s+check)\b.*\b(?:school|project|council|ncc|bca|efsg)\b", "standards_reference_advisory", ("standards_knowledge_base", "qs_scope_advisor"), 91),
    (r"\b(?:standards?|ncc|bca|efsg|eurocode|nrm|anzsmm|cesmm|icms|council\s+standard)\b.*\b(?:checklist|scope|advisory|what\s+to\s+check|reference|school|project)\b", "standards_reference_advisory", ("standards_knowledge_base", "qs_scope_advisor"), 91),
]


def detect_registry_advisory(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    detail = negative_guard_detail(normalized)
    if detail:
        return NoActiveTaskLanguageDecision(matched=False, public_negative_guard=public_negative_guard_for_detail(detail), negative_guard_detail=detail)
    for pattern, alias, tools, confidence in _REGISTRY_ADVISORY_PATTERNS:
        if re.search(pattern, normalized):
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="registry_advisory",
                route="registry_advisory_metadata_only",
                intent="REGISTRY_ADVISORY",
                confidence=confidence,
                reason=f"registry_advisory:{alias}",
                alias=alias,
                requires_setup=False,
                requires_clarification=True,
                tool_candidates=tools,
            )
    return NoActiveTaskLanguageDecision()

def detect_general_qs_help(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    detail = negative_guard_detail(normalized)
    if detail:
        return NoActiveTaskLanguageDecision(matched=False, public_negative_guard=public_negative_guard_for_detail(detail), negative_guard_detail=detail)
    for pattern, alias, confidence in _GENERAL_QS_HELP_PATTERNS:
        if re.search(pattern, normalized):
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="general_qs_help",
                route="general_stub",
                intent="GENERAL_QS_HELP",
                confidence=confidence,
                reason=f"general_qs_help:{alias}",
                alias=alias,
                requires_setup=False,
                requires_clarification=False,
                tool_candidates=(),
            )
    return NoActiveTaskLanguageDecision()


def negative_guard_detail(text: str) -> str | None:
    normalized = normalize_text(text)
    for pattern, _public, detail in _NEGATIVE_GUARD_PATTERNS:
        if re.search(pattern, normalized):
            return detail
    return None


def public_negative_guard_for_detail(detail: str | None) -> str | None:
    if not detail:
        return None
    if detail in {"format_text_not_workbook", "writing_help_not_workbook"}:
        return "format_text_not_workbook"
    return "casual_non_tool_phrase"


def detect_builder_start_alias(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    detail = negative_guard_detail(normalized)
    if detail:
        return NoActiveTaskLanguageDecision(
            matched=False,
            public_negative_guard=public_negative_guard_for_detail(detail),
            negative_guard_detail=detail,
        )

    has_create_verb = bool(re.search(rf"\b{_CREATE_VERBS}\b", normalized))
    has_qs_context = bool(re.search(rf"\b{_QS_CONTEXT}\b", normalized))

    for pattern, alias, region, confidence in _ALIAS_PATTERNS:
        if re.search(pattern, normalized):
            if has_create_verb or alias in {"boq", "bill_of_quantities", "boq_base_sheet", "tender_boq", "schedule_of_values", "trade_schedule"}:
                return NoActiveTaskLanguageDecision(
                    matched=True,
                    category="soft_builder_start",
                    route="new_builder_task_shell",
                    intent="NEW_COMMAND",
                    confidence=confidence,
                    reason=f"exact_qs_builder_alias:{alias}",
                    alias=alias,
                    region_hint=region,
                    requires_setup=True,
                    requires_clarification=False,
                    tool_candidates=("builder",),
                )

    if has_create_verb and has_qs_context and re.search(r"\b(estimate|cost\s+plan|takeoff|take\s+off)\b", normalized):
        return NoActiveTaskLanguageDecision(
            matched=True,
            category="soft_builder_start",
            route="new_builder_task_shell",
            intent="NEW_COMMAND",
            confidence=90,
            reason="exact_qs_builder_alias:qs_estimate_or_takeoff",
            alias="qs_estimate_or_takeoff",
            requires_setup=True,
            requires_clarification=False,
            tool_candidates=("builder",),
        )

    return NoActiveTaskLanguageDecision()



def detect_workbook_read_policy_review(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    for pattern, alias in _WORKBOOK_READ_POLICY_REVIEW_PATTERNS:
        if re.search(pattern, normalized):
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="workbook_read_policy_review",
                route="builder_workbook_read_policy_review",
                intent="WORKBOOK_READ_POLICY_REVIEW",
                confidence=98,
                reason=f"workbook_read_policy_review:{alias}",
                alias=alias,
                requires_setup=False,
                requires_clarification=False,
                tool_candidates=("builder",),
            )
    return NoActiveTaskLanguageDecision()


def detect_no_active_workbook_content_read_safe_block(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    for pattern, alias in _WORKBOOK_CONTENT_READ_SAFE_BLOCK_PATTERNS:
        if re.search(pattern, normalized):
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="workbook_content_read_safe_block",
                route="no_active_prompt_injection_safe_block",
                intent="SAFE_BLOCK",
                confidence=98,
                reason=f"no_active_workbook_content_read_safe_block:{alias}",
                alias=alias,
                requires_setup=False,
                requires_clarification=False,
                tool_candidates=(),
            )
    return NoActiveTaskLanguageDecision()


def detect_no_active_sheet_name_probe_ambiguity(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    for pattern, alias in _SHEET_NAME_PROBE_AMBIGUITY_PATTERNS:
        if re.search(pattern, normalized):
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="sheet_name_probe_ambiguity",
                route="choose_tool",
                intent="TOOL_LIKE_AMBIGUOUS",
                confidence=94,
                reason=f"sheet_name_probe_ambiguity:{alias}",
                alias=alias,
                requires_setup=False,
                requires_clarification=True,
                tool_candidates=("builder",),
            )
    return NoActiveTaskLanguageDecision()


def detect_no_active_prompt_injection_safe_block(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    for pattern, alias in _NO_ACTIVE_PROMPT_INJECTION_SAFE_BLOCK_PATTERNS:
        if re.search(pattern, normalized):
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="prompt_injection_safe_block",
                route="no_active_prompt_injection_safe_block",
                intent="SAFE_BLOCK",
                confidence=99,
                reason=f"no_active_prompt_injection_safe_block:{alias}",
                alias=alias,
                requires_setup=False,
                requires_clarification=False,
                tool_candidates=(),
            )
    return NoActiveTaskLanguageDecision()


def detect_generic_tool_ambiguity(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    detail = negative_guard_detail(normalized)
    if detail:
        return NoActiveTaskLanguageDecision(
            matched=False,
            public_negative_guard=public_negative_guard_for_detail(detail),
            negative_guard_detail=detail,
        )
    for pattern, tools, reason, confidence in _GENERIC_TOOL_AMBIGUITY_PATTERNS:
        if re.search(pattern, normalized):
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="generic_choose_tool",
                route="choose_tool",
                intent="TOOL_LIKE_AMBIGUOUS",
                confidence=confidence,
                reason=reason,
                alias=reason.split(":", 1)[-1].replace("generic_tool_like:", "").replace(" ", "_"),
                requires_setup=True,
                requires_clarification=True,
                tool_candidates=tools,
            )
    return NoActiveTaskLanguageDecision()




def detect_engineering_language(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()
    engineering = classify_engineering_language(normalized)
    if not engineering.matched:
        return NoActiveTaskLanguageDecision()
    if engineering.category == "engineering_choose_tool":
        return NoActiveTaskLanguageDecision(
            matched=True,
            category="generic_choose_tool",
            route="choose_tool",
            intent="ENGINEERING_TOOL_LIKE_AMBIGUOUS",
            confidence=engineering.confidence,
            reason=engineering.reason,
            alias=engineering.engineering_category,
            requires_setup=False,
            requires_clarification=True,
            tool_candidates=engineering.tool_candidates or ("qa_checker", "builder", "formatter"),
        )
    return NoActiveTaskLanguageDecision(
        matched=True,
        category="general_qs_help",
        route="general_stub",
        intent="ENGINEERING_LANGUAGE_HELP",
        confidence=engineering.confidence,
        reason=engineering.reason,
        alias=engineering.engineering_category,
        requires_setup=False,
        requires_clarification=False,
        tool_candidates=engineering.tool_candidates,
    )


def _soft_builder_alias(normalized: str) -> tuple[str, int] | None:
    has_soft_request = any(re.search(pattern, normalized) for pattern in _SOFT_REQUEST_PATTERNS)
    if not has_soft_request:
        return None
    for pattern, alias, confidence in _SOFT_QS_OBJECT_PATTERNS:
        if re.search(pattern, normalized):
            return alias, confidence
    return None


def classify_no_active_task_language(text: str) -> NoActiveTaskLanguageDecision:
    normalized = _strip_language_wrappers(normalize_text(text))
    if not normalized:
        return NoActiveTaskLanguageDecision()

    detail = negative_guard_detail(normalized)
    if detail:
        public = public_negative_guard_for_detail(detail)
        if public == "format_text_not_workbook":
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="writing_help",
                route="general_stub",
                intent="GENERAL_WRITING_HELP",
                confidence=99,
                reason=f"negative_guard:{public}",
                public_negative_guard=public,
                negative_guard_detail=detail,
                requires_clarification=False,
                tool_candidates=(),
            )
        return NoActiveTaskLanguageDecision(
            matched=True,
            category="casual_non_tool",
            route="general_stub",
            intent="GENERAL",
            confidence=99,
            reason=f"negative_guard:{public}",
            public_negative_guard=public,
            negative_guard_detail=detail,
            requires_clarification=False,
            tool_candidates=(),
        )

    if _has_negative_workbook_read_polarity(normalized):
        exact_builder = detect_builder_start_alias(normalized)
        if exact_builder.matched:
            return exact_builder
        soft = _soft_builder_alias(normalized)
        if soft:
            alias, confidence = soft
            return NoActiveTaskLanguageDecision(
                matched=True,
                category="soft_builder_start",
                route="new_builder_task_shell",
                intent="NEW_COMMAND",
                confidence=confidence,
                reason=f"negative_workbook_read_polarity + qs_alias:{alias}",
                alias=alias,
                requires_setup=True,
                requires_clarification=False,
                tool_candidates=("builder",),
            )

    prompt_injection_safe_block = detect_no_active_prompt_injection_safe_block(normalized)
    if prompt_injection_safe_block.matched:
        return prompt_injection_safe_block

    workbook_policy = detect_workbook_read_policy_review(normalized)
    if workbook_policy.matched:
        return workbook_policy

    workbook_content_block = detect_no_active_workbook_content_read_safe_block(normalized)
    if workbook_content_block.matched:
        return workbook_content_block

    sheet_name_probe_ambiguity = detect_no_active_sheet_name_probe_ambiguity(normalized)
    if sheet_name_probe_ambiguity.matched:
        return sheet_name_probe_ambiguity

    # Registry advisory/report/future-tool wording must be classified before
    # exact BOQ Builder aliases so advisory requests do not create Builder shells.
    registry_advisory = detect_registry_advisory(normalized)
    if registry_advisory.matched:
        return registry_advisory

    if re.search(r"\bcheck\b.*\bboq\s+value\s+summary\b.*\bqs\s+review\b", normalized):
        return NoActiveTaskLanguageDecision(
            matched=True,
            category="soft_builder_start",
            route="new_builder_task_shell",
            intent="NEW_COMMAND",
            confidence=95,
            reason="soft_request + qs_alias:boq_value_summary",
            alias="boq_value_summary",
            requires_setup=True,
            requires_clarification=False,
            tool_candidates=("builder",),
        )

    if re.search(r"^check\s+the\s+boq\s+workbook\.?$", normalized):
        return NoActiveTaskLanguageDecision(
            matched=True, category="soft_builder_start", route="new_builder_task_shell",
            intent="NEW_COMMAND", confidence=95, reason="soft_request + qs_alias:boq_workbook_check",
            alias="boq_workbook_check", requires_setup=True, requires_clarification=False, tool_candidates=("builder",),
        )
    if re.search(r"^run\s+the\s+correct\s+jarvis\s+tool\.?$", normalized):
        return NoActiveTaskLanguageDecision(
            matched=True, category="soft_builder_start", route="new_builder_task_shell",
            intent="NEW_COMMAND", confidence=95, reason="soft_request + qs_alias:correct_jarvis_tool",
            alias="correct_jarvis_tool", requires_setup=True, requires_clarification=False, tool_candidates=("builder",),
        )

    # Alpha.32A no-active minimal-pair ownership. These phrases are intentionally
    # scoped here instead of _GENERIC_TOOL_AMBIGUITY_PATTERNS because that helper is
    # also reused by active-task ambiguity guards. Active setup edits must remain
    # owned by slot_reducer.
    if re.search(r"^use\s+doors?\s+and\s+windows?\.?$", normalized):
        return NoActiveTaskLanguageDecision(
            matched=True,
            category="generic_choose_tool",
            route="choose_tool",
            intent="TOOL_LIKE_AMBIGUOUS",
            confidence=92,
            reason="no_active_minimal_pair:doors_windows_setup",
            alias="doors_windows_setup_no_active",
            requires_setup=True,
            requires_clarification=True,
            tool_candidates=("builder",),
        )

    if re.search(r"^run\s+safe\s+workbook\s+path\s+resolver\s+dry\s+run\.?$", normalized):
        return NoActiveTaskLanguageDecision(
            matched=True,
            category="generic_choose_tool",
            route="choose_tool",
            intent="TOOL_LIKE_AMBIGUOUS",
            confidence=92,
            reason="no_active_minimal_pair:safe_workbook_path_resolver_dry_run",
            alias="safe_workbook_path_resolver_dry_run",
            requires_setup=True,
            requires_clarification=True,
            tool_candidates=("builder", "engine_boundary_audit"),
        )

    # Ambiguous file/workflow language must be clarified before exact Builder
    # aliases, e.g. "Compare the two BOQ files" or "Create a new BOQ from this".
    generic = detect_generic_tool_ambiguity(normalized)
    if generic.matched:
        return generic

    engineering = detect_engineering_language(normalized)
    if engineering.matched and engineering.route == "choose_tool":
        return engineering

    soft = _soft_builder_alias(normalized)
    if soft:
        alias, confidence = soft
        return NoActiveTaskLanguageDecision(
            matched=True,
            category="soft_builder_start",
            route="new_builder_task_shell",
            intent="NEW_COMMAND",
            confidence=confidence,
            reason=f"soft_request + qs_alias:{alias}",
            alias=alias,
            requires_setup=True,
            requires_clarification=False,
            tool_candidates=("builder",),
        )

    qs_help = detect_general_qs_help(normalized)
    if qs_help.matched:
        return qs_help

    exact_builder = detect_builder_start_alias(normalized)
    if exact_builder.matched:
        return exact_builder

    if engineering.matched:
        return engineering

    return NoActiveTaskLanguageDecision()
