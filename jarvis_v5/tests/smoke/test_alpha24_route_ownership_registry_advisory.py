from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client():
    return TestClient(app)


def test_alpha24_version_scope_and_locks():
    data = client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['scope'] == 'workbook_read_policy_review_no_content_read'
    assert data['scope_metadata']['active_task_action_language_gate'] is True
    assert data['scope_metadata']['registry_advisory_metadata_only_route'] is True
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_active_natural_actions_route_without_fallback():
    c = client()
    cid = 'a24_smoke_active_actions'
    start = c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': 'a24_smoke_start', 'text': 'Build me a BOQ'}).json()
    assert start['route'] == 'new_builder_task_shell'
    cases = [
        ('Please review the current setup', 'active_task_review'),
        ('Preview it please', 'active_task_preview_stub'),
        ('Export it when ready', 'active_task_export_stub'),
        ('Download the output', 'active_task_action_stub'),
    ]
    for idx, (text, expected_route) in enumerate(cases):
        payload = c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': f'a24_smoke_action_{idx}', 'text': text}).json()
        assert payload['route'] == expected_route
        assert payload['router_step'] == 'active_task_action_language_gate'
        assert payload['fallback_used'] is False
        assert payload['active_task_action_language']['matched'] is True


def test_active_setup_corrections_still_owned_by_slot_reducer():
    c = client()
    cid = 'a24_smoke_setup_norm'
    c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': 'a24_smoke_setup_start', 'text': 'Build me a BOQ'}).json()
    unit = c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': 'a24_smoke_unit', 'text': 'The unit should be no, not square metres'}).json()
    assert unit['route'] == 'active_task_slot_edit'
    assert unit['router_step'] == 'slot_reducer'
    assert 'unit' in unit['reducer_result']['changed_slots']
    assert unit['reducer_result']['normalization']['canonical_text'] == 'Unit no'

    zone = c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': 'a24_smoke_zone', 'text': 'Please put Old and New under Zone 1'}).json()
    assert zone['route'] == 'active_task_slot_edit'
    assert zone['router_step'] == 'slot_reducer'
    assert 'dynamic_zones' in zone['reducer_result']['changed_slots']
    assert zone['reducer_result']['normalization']['canonical_text'] == 'Zone 1: Old and New'


def test_registry_advisory_route_is_metadata_only():
    payload = client().post('/api/chat', json={'conversation_id': 'a24_smoke_registry_adv', 'client_event_id': 'a24_smoke_registry_adv_1', 'text': 'Create a BOQ checklist from fire report'}).json()
    assert payload['route'] == 'registry_advisory_metadata_only'
    assert payload['metadata_only'] is True
    assert payload['execution_enabled'] is False
    assert payload['workbook_read'] is False
    assert payload['engine_called'] is False
    assert payload['excel_created'] is False
    assert payload['legacy_builder_called'] is False
    assert payload['fallback_used'] is False
    assert 'qs_scope_advice' in payload['capability_candidates']
    assert 'document_ocr_or_report_reader' in payload['capability_candidates']


def test_measure_schedule_soft_alias_and_definition_guard():
    c = client()
    start = c.post('/api/chat', json={'conversation_id': 'a24_smoke_measure_start', 'client_event_id': 'a24_smoke_measure_start_1', 'text': 'Can you start a measure schedule?'}).json()
    assert start['route'] == 'new_builder_task_shell'
    assert start['reducer_result']['qs_alias']['alias'] == 'measure_schedule'
    assert start['fallback_used'] is False

    definition = c.post('/api/chat', json={'conversation_id': 'a24_smoke_measure_definition', 'client_event_id': 'a24_smoke_measure_definition_1', 'text': 'What does measure schedule mean?'}).json()
    assert definition['route'] == 'general_stub'
    assert definition['reason'] == 'casual_non_tool_phrase'
    assert definition['fallback_used'] is False
