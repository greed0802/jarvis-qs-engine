from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client():
    return TestClient(app)


def post(c, cid, eid, text):
    return c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': eid, 'text': text}).json()


def test_alpha22_2a_version_locks():
    data = client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_confidence_engine_is_shadow_only_on_existing_builder_alias():
    data = post(client(), 'a222a_shadow_boq', 'a222a_boq_001', 'Can you help me put together a BOQ?')
    assert data['route'] == 'new_builder_task_shell'
    engine = data['confidence_engine']
    assert engine['enabled'] is True
    assert engine['mode'] == 'limited_control'
    assert engine['control_taken'] is True
    assert engine['actual_route'] == 'new_builder_task_shell'
    assert engine['would_route'] == 'new_builder_task_shell'
    assert engine['route_mismatch'] is False
    assert 'builder' in engine['tool_candidates']


def test_confidence_engine_reports_choose_tool_mismatch_without_changing_route():
    data = post(client(), 'a222a_compare_shadow', 'a222a_compare_001', 'Compare this')
    assert data['route'] in {'general_stub', 'choose_tool'}
    engine = data['confidence_engine']
    assert engine['control_taken'] is True
    assert engine['mode'] == 'limited_control'
    assert engine['actual_route'] == data['route']
    assert engine['would_route'] == 'choose_tool'
    assert engine['would_confidence'] >= 88
    assert 'builder' in engine['tool_candidates']


def test_confidence_engine_detects_writing_negative_guard():
    data = post(client(), 'a222a_writing_shadow', 'a222a_writing_001', 'Clean this reply wording')
    engine = data['confidence_engine']
    assert engine['control_taken'] is True
    assert engine['mode'] == 'limited_control'
    assert engine['would_route'] == 'general_writing_help'
    assert engine['negative_guard'] == 'format_text_not_workbook'
    assert engine['negative_guard_detail'] == 'writing_help_not_workbook'
    assert engine['tool_candidates'] == []


def test_confidence_engine_detects_casual_schedule_negative_guard():
    data = post(client(), 'a222a_meeting_shadow', 'a222a_meeting_001', 'Schedule a meeting tomorrow')
    engine = data['confidence_engine']
    assert engine['control_taken'] is True
    assert engine['mode'] == 'limited_control'
    assert engine['would_route'] == 'general_stub'
    assert engine['negative_guard'] == 'casual_non_tool_phrase'
    assert engine['negative_guard_detail'] == 'schedule_meeting'
    assert engine['route_mismatch'] is False


def test_api_plan_no_active_task_has_safety_readiness():
    data = client().get('/api/plan/a222a_no_active_task').json()
    assert data['found'] is False
    assert data['reason'] == 'conversation_not_found'
    assert data['safety']['workbook_read'] is False
    assert data['safety']['engine_called'] is False
    assert data['safety']['excel_created'] is False
    assert data['safety']['contract_only'] is True
    assert data['safety']['legacy_builder_called'] is False
    assert data['readiness']['status'] == 'no_active_task'
    assert data['readiness']['safety']['workbook_read'] is False
    assert data['readiness']['safety']['engine_called'] is False
    assert data['readiness']['safety']['excel_created'] is False
    assert data['readiness']['safety']['contract_only'] is True
    assert data['readiness']['safety']['legacy_builder_called'] is False
