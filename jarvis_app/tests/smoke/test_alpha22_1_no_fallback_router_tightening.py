from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client():
    return TestClient(app)


def post(c, cid, eid, text):
    return c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': eid, 'text': text}).json()


def test_alpha22_1_version_locks():
    data = client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_generic_tool_like_phrases_choose_tool_not_fallback():
    c = client()
    for idx, text in enumerate(['Compare', 'Check', 'Create', 'Run it', 'Start the tool']):
        data = post(c, f'alpha221_generic_{idx}', f'a221_generic_{idx}', text)
        assert data['route'] == 'choose_tool'
        assert data['requires_clarification'] is True
        assert data['fallback_used'] is False
        assert data['tool_candidates']
        assert data['active_task_id'] is None


def test_format_text_negative_guard_is_general_chat_not_formatter():
    c = client()
    for idx, text in enumerate(['Format this sentence', 'Format this chat reply only']):
        data = post(c, f'alpha221_format_text_{idx}', f'a221_format_{idx}', text)
        assert data['route'] == 'general_stub'
        assert data['fallback_used'] is False
        assert data['tool_candidates'] == []
        assert data['confidence_reason'] == 'negative_guard:format_text_not_workbook'
        assert data['router_step'] == 'no_active_task_language_gate'
        assert data['active_task_id'] is None


def test_carpet_or_tiling_requires_trade_clarification_no_silent_mutation():
    c = client()
    cid = 'alpha221_carpet_or_tiling'
    start = post(c, cid, 'a221_trade_001', 'Build me a BOQ')
    assert start['route'] == 'new_builder_task_shell'
    data = post(c, cid, 'a221_trade_002', 'Use Carpet or Tiling')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    assert data['requires_clarification'] is True
    assert data['fallback_used'] is False
    assert data['reducer_result']['conflict_type'] == 'trade_choice_ambiguous'
    assert data['reducer_result']['plan_mutated'] is False
    plan = c.get(f'/api/plan/{cid}').json()
    assert plan['plan_summary']['trade_profile'] is None


def test_trade_measure_schedule_alias_starts_builder_shell():
    data = post(client(), 'alpha221_trade_measure_schedule', 'a221_tms_001', 'Prepare a trade measure schedule for NZ QS review')
    assert data['route'] == 'new_builder_task_shell'
    assert data['fallback_used'] is False
    assert data['tool_candidates'] == ['builder']
    assert data['reducer_result']['qs_alias']['alias'] == 'trade_measure_schedule'


def test_existing_negative_guards_still_do_not_start_builder():
    c = client()
    meeting = post(c, 'alpha221_meeting', 'a221_meeting_001', 'Schedule a meeting tomorrow')
    assert meeting['route'] == 'general_stub'
    assert meeting['fallback_used'] is False
    assert meeting['confidence_reason'] == 'negative_guard:casual_non_tool_phrase'
    assert meeting['confidence_engine']['negative_guard_detail'] == 'schedule_meeting'

    definition = post(c, 'alpha221_define', 'a221_define_001', 'What is a Schedule of Values?')
    assert definition['route'] == 'general_stub'
    assert definition['fallback_used'] is False
    assert definition['confidence_reason'] == 'negative_guard:casual_non_tool_phrase'
    assert definition['confidence_engine']['negative_guard_detail'] == 'definition_request'
