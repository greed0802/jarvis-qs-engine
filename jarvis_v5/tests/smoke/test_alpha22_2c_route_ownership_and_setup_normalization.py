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


def test_alpha22_2c_version_locks():
    data = client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_no_active_task_language_gate_owns_writing_casual_tool_and_builder_shell():
    c = client()
    cases = [
        ('write', 'Format this sentence.', 'general_stub', 'general_writing_help'),
        ('casual', 'What does value mean?', 'general_stub', 'general_stub'),
        ('tool', 'Do whatever tool makes sense here.', 'choose_tool', 'choose_tool'),
        ('builder', 'Can you help me prepare a BOQ?', 'new_builder_task_shell', 'new_builder_task_shell'),
    ]
    for suffix, text, route, would_route in cases:
        data = post(c, f'a222c_gate_{suffix}', f'a222c_gate_{suffix}', text)
        assert data['route'] == route
        assert data['router_step'] == 'no_active_task_language_gate'
        assert data['fallback_used'] is False
        assert data['confidence_engine']['control_taken'] is True
        assert data['confidence_engine']['would_route'] == would_route
        if route != 'new_builder_task_shell':
            assert data['active_task_id'] is None


def test_active_builder_natural_setup_grammar_uses_slot_reducer_no_confidence_control():
    c = client()
    cid = 'a222c_active_setup_normalization'
    start = post(c, cid, 'a222c_setup_start', 'Build me a BOQ')
    assert start['route'] == 'new_builder_task_shell'
    examples = [
        ('unit', 'The unit should be m2', 'active_task_slot_edit'),
        ('zone', 'For now, Zone 1 is Old and New', 'active_task_slot_edit'),
        ('head', 'Please put Zone 1 under Head 2', 'active_task_slot_edit'),
        ('levels', 'Use levels from GF to L3', 'active_task_slot_edit'),
    ]
    for suffix, text, expected_route in examples:
        data = post(c, cid, f'a222c_setup_{suffix}', text)
        assert data['route'] == expected_route
        assert data['router_step'] == 'slot_reducer'
        assert data['confidence_engine']['control_taken'] is False
        assert (data.get('reducer_result') or {}).get('plan_mutated') is True


def test_active_builder_writing_does_not_bypass_active_task_by_default():
    c = client()
    cid = 'a222c_active_writing_guard'
    start = post(c, cid, 'a222c_writing_start', 'Build me a BOQ')
    data = post(c, cid, 'a222c_writing_sentence', 'Format this sentence')
    assert data['active_task_id'] == start['active_task_id']
    assert data['router_step'] == 'active_task_non_mutating_language_gate'
    assert data['route'] == 'active_task_non_mutating_language'
    assert data['confidence_engine']['control_taken'] is False


def test_normalization_preserves_function_unit_conflicts():
    c = client()
    cases = ['Use Count unit m2', 'Use Count, the unit should be m2', 'Use Reinforcement Weight unit kg']
    for idx, text in enumerate(cases):
        cid = f'a222c_conflict_{idx}'
        post(c, cid, f'a222c_conflict_start_{idx}', 'Build me a BOQ')
        data = post(c, cid, f'a222c_conflict_edit_{idx}', text)
        assert data['route'] == 'active_task_slot_edit_needs_clarification'
        assert data['router_step'] == 'slot_reducer'
        assert data['confidence_engine']['control_taken'] is False
        assert (data.get('reducer_result') or {}).get('plan_mutated') is False
        assert (data.get('reducer_result') or {}).get('conflict_type') in {
            'function_unit_conflict',
            'custom_quantity_unit_conflict',
            'trade_profile_requires_clarification',
        }


def test_attachment_and_preview_export_protected_contexts_remain_unchanged():
    c = client()
    attach = post(c, 'a222c_attach_no_task', 'a222c_attach_001', 'Here', attachments=[{
        'filename': 'Test.xlsx',
        'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'size_bytes': 1234,
    }])
    assert attach['route'] == 'attachment_received_no_active_task'
    assert attach['router_step'] == 'attachment_bind'
    assert attach['confidence_engine']['control_taken'] is False
    assert attach['reducer_result']['workbook_read'] is False

    cid = 'a222c_preview_export'
    post(c, cid, 'a222c_preview_start', 'Build me a BOQ')
    preview = post(c, cid, 'a222c_preview', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['confidence_engine']['control_taken'] is False
    assert preview['readiness']['safety']['workbook_read'] is False
    assert preview['readiness']['safety']['engine_called'] is False
    assert preview['readiness']['safety']['excel_created'] is False
    assert preview['readiness']['safety']['legacy_builder_called'] is False
