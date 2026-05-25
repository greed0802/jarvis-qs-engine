from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client():
    return TestClient(app)


def post(c, cid, eid, text, attachments=None):
    payload = {"conversation_id": cid, "client_event_id": eid, "text": text}
    if attachments is not None:
        payload["attachments"] = attachments
    return c.post('/api/chat', json=payload).json()


def assert_safety_readiness(data):
    readiness = data.get('readiness') or {}
    safety = readiness.get('safety') or {}
    if safety:
        assert safety['workbook_read'] is False
        assert safety['engine_called'] is False
        assert safety['excel_created'] is False
        assert safety['legacy_builder_called'] is False


def test_alpha22_2b_version_locks():
    data = client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_limited_control_general_writing_negative_guards():
    c = client()
    phrases = [
        'Format this sentence.',
        'Clean this reply wording.',
        'Make this paragraph read better, not a BOQ.',
        'Improve this explanation, but do not open any tool.',
    ]
    for idx, text in enumerate(phrases):
        data = post(c, f'a222b_write_{idx}', f'a222b_write_{idx}', text)
        assert data['route'] in {'general_chat', 'general_stub'}
        assert data['fallback_used'] is False
        assert data['active_task_id'] is None
        engine = data['confidence_engine']
        assert engine['mode'] == 'limited_control'
        assert engine['control_taken'] is True
        assert engine['would_route'] in {'general_writing_help', 'general_chat', 'general_stub'}
        assert data['tool_candidates'] == []


def test_limited_control_generic_tool_ambiguity():
    c = client()
    phrases = ['Compare this.', 'Check it.', 'Create one for me.', 'Run this.', 'Start the tool.', 'Process this file.']
    for idx, text in enumerate(phrases):
        data = post(c, f'a222b_tool_{idx}', f'a222b_tool_{idx}', text)
        assert data['route'] == 'choose_tool'
        assert data['fallback_used'] is False
        assert data['requires_clarification'] is True
        assert data['active_task_id'] is None
        engine = data['confidence_engine']
        assert engine['mode'] == 'limited_control'
        assert engine['control_taken'] is True
        assert engine['would_route'] == 'choose_tool'
        assert data['tool_candidates']


def test_limited_control_soft_builder_shell_only():
    c = client()
    phrases = [
        'Set up the steel surface area measurement.',
        'I need a door and window count schedule.',
        'Set up the reinforcement weight schedule.',
    ]
    for idx, text in enumerate(phrases):
        data = post(c, f'a222b_shell_{idx}', f'a222b_shell_{idx}', text)
        assert data['route'] == 'new_builder_task_shell'
        assert data['fallback_used'] is False
        assert data['tool_candidates'] == ['builder']
        assert data['active_task_id']
        engine = data['confidence_engine']
        assert engine['mode'] == 'limited_control'
        assert engine['control_taken'] is True
        assert engine['would_route'] == 'new_builder_task_shell'
        # Shell only: no reducer mutation slots should be claimed by confidence control.
        reducer = data.get('reducer_result') or {}
        assert (reducer.get('confidence_engine') or {}).get('plan_mutated') is False
        assert_safety_readiness(data)


def test_existing_qs_aliases_still_work_without_forced_control():
    c = client()
    data = post(c, 'a222b_existing_alias', 'a222b_existing_alias_001', 'Can you help me prepare a BOQ?')
    assert data['route'] == 'new_builder_task_shell'
    assert data['fallback_used'] is False
    assert data['confidence_engine']['would_route'] == 'new_builder_task_shell'
    # Existing route is already correct; limited-control only replaces fallback/choose-tool paths.
    assert data['confidence_engine']['control_taken'] is True


def test_limited_control_casual_estimate_schedule_value_cost_guards():
    c = client()
    phrases = [
        'Estimate how long this will take.',
        'Schedule a call tomorrow.',
        'What does value mean?',
        'Cost meaning only.',
        'Estimate the risk of doing this too early.',
    ]
    for idx, text in enumerate(phrases):
        data = post(c, f'a222b_casual_{idx}', f'a222b_casual_{idx}', text)
        assert data['route'] in {'general_stub', 'general_chat'}
        assert data['fallback_used'] is False
        assert data['active_task_id'] is None
        engine = data['confidence_engine']
        assert engine['mode'] == 'limited_control'
        assert engine['control_taken'] is True
        assert engine['would_route'] == 'general_stub'
        assert engine['negative_guard']


def test_active_builder_context_blocks_limited_confidence_control():
    c = client()
    cid = 'a222b_active_blocks_control'
    start = post(c, cid, 'a222b_active_start', 'Build me a BOQ')
    assert start['route'] == 'new_builder_task_shell'
    data = post(c, cid, 'a222b_active_compare', 'Compare this')
    assert data['route'] in {'active_task_slot_edit_needs_clarification', 'formatter_handoff_needs_confirmation', 'active_task_edit_unhandled'}
    assert data['confidence_engine']['control_taken'] is False
    assert data['active_task_id'] == start['active_task_id']


def test_pending_clarification_blocks_limited_confidence_control():
    c = client()
    cid = 'a222b_pending_blocks_control'
    assert post(c, cid, 'a222b_pending_start', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    clarification = post(c, cid, 'a222b_pending_painting', 'Use Painting')
    assert clarification['route'] == 'active_task_slot_edit_needs_clarification'
    data = post(c, cid, 'a222b_pending_answer', 'Use wall painting')
    assert data['route'] in {'clarification_resolved', 'active_task_slot_edit', 'active_task_edit_unhandled'}
    assert data['confidence_engine']['control_taken'] is False


def test_attachment_without_active_task_does_not_create_fake_builder_task():
    c = client()
    data = post(
        c,
        'a222b_attach_no_task',
        'a222b_attach_no_task_001',
        'Here',
        attachments=[{"filename": "Test.xlsx", "content_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "size_bytes": 1234}],
    )
    assert data['route'] == 'attachment_received_no_active_task'
    assert data['active_task_id'] is None
    assert data['confidence_engine']['control_taken'] is False
    assert data['reducer_result']['workbook_read'] is False


def test_preview_export_stubs_remain_blocked_no_engine():
    c = client()
    cid = 'a222b_preview_export'
    start = post(c, cid, 'a222b_preview_start', 'Build me a BOQ')
    assert start['route'] == 'new_builder_task_shell'
    preview = post(c, cid, 'a222b_preview', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['confidence_engine']['control_taken'] is False
    assert preview['readiness']['safety']['workbook_read'] is False
    assert preview['readiness']['safety']['engine_called'] is False
    assert preview['readiness']['safety']['excel_created'] is False
    assert preview['readiness']['safety']['legacy_builder_called'] is False
    export = post(c, cid, 'a222b_export', 'Export')
    assert export['route'] == 'active_task_export_stub'
    assert export['blocked'] is True
    assert export['confidence_engine']['control_taken'] is False
