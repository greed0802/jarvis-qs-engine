from __future__ import annotations

from uuid import uuid4
from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client():
    return TestClient(app)


def post_chat(c, conv: str, event: str, text: str):
    r = c.post('/api/chat', json={'conversation_id': conv, 'client_event_id': event, 'text': text})
    assert r.status_code == 200
    return r.json()


def attach_fixture(c, conv: str, event: str):
    with open('jarvis_v5/tests/fixtures/Test.xlsx', 'rb') as fh:
        r = c.post(
            '/api/attach',
            data={'conversation_id': conv, 'client_event_id': event, 'text': 'Here'},
            files={'file': ('Test.xlsx', fh, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        )
    assert r.status_code == 200
    return r.json()


def complete_preflight_flow(c, conv: str):
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    attach_fixture(c, conv, f'{conv}_attach')
    post_chat(c, conv, f'{conv}_002', 'Use Wall Types')
    post_chat(c, conv, f'{conv}_003', 'Use XGETWALLAREA')
    post_chat(c, conv, f'{conv}_004', 'Unit m2')
    post_chat(c, conv, f'{conv}_005', 'Zone 1: Old and New')
    post_chat(c, conv, f'{conv}_006', 'Use Head 2 for Zone 1')
    post_chat(c, conv, f'{conv}_007', 'Levels GF to L3')
    snapshot = c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': f'{conv}_snap'}).json()
    assert snapshot['route'] == 'builder_snapshot_created'
    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': f'{conv}_adapter'}).json()
    assert adapter['route'] == 'builder_adapter_dry_run'
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    audit = c.post('/api/builder/engine-boundary-audit', json={'conversation_id': conv, 'client_event_id': f'{conv}_audit'}).json()
    assert audit['route'] == 'builder_engine_boundary_audit'
    preflight = c.post('/api/builder/engine-preflight', json={'conversation_id': conv, 'client_event_id': f'{conv}_preflight'}).json()
    assert preflight['route'] == 'builder_engine_preflight_ready'
    return preflight


def assert_safety_false(payload: dict):
    assert payload['workbook_read'] is False
    assert payload['engine_called'] is False
    assert payload['excel_created'] is False
    assert payload['legacy_builder_called'] is False
    safety = payload.get('safety') or {}
    assert safety.get('workbook_read') is False
    assert safety.get('engine_called') is False
    assert safety.get('excel_created') is False
    assert safety.get('legacy_builder_called') is False


def test_alpha17_version_execution_locks():
    data = client().get('/api/version').json()
    assert data['version'] == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['engines_connected']['builder_engine_execution'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_alpha17_execution_request_without_contract_blocks():
    c = client()
    conv = f'alpha17_no_contract_{uuid4().hex}'
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    payload = c.post('/api/builder/engine-execution-request', json={'conversation_id': conv, 'client_event_id': f'{conv}_exec'}).json()
    assert payload['route'] == 'builder_engine_execution_blocked'
    assert payload['blocked'] is True
    assert payload['reason'] == 'engine_contract_not_found'
    assert payload['execution_status'] == 'disabled'
    assert_safety_false(payload)


def test_alpha17_execution_request_contract_without_preflight_blocks():
    c = client()
    conv = f'alpha17_no_preflight_{uuid4().hex}'
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    attach_fixture(c, conv, f'{conv}_attach')
    post_chat(c, conv, f'{conv}_002', 'Use Wall Types')
    post_chat(c, conv, f'{conv}_003', 'Use XGETWALLAREA')
    post_chat(c, conv, f'{conv}_004', 'Unit m2')
    post_chat(c, conv, f'{conv}_005', 'Zone 1: Old and New')
    post_chat(c, conv, f'{conv}_006', 'Use Head 2 for Zone 1')
    post_chat(c, conv, f'{conv}_007', 'Levels GF to L3')
    c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': f'{conv}_snap'})
    c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': f'{conv}_adapter'})
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    payload = c.post('/api/builder/engine-execution-request', json={'conversation_id': conv, 'client_event_id': f'{conv}_exec'}).json()
    assert payload['route'] == 'builder_engine_execution_blocked'
    assert payload['reason'] == 'engine_preflight_not_found'
    assert_safety_false(payload)


def test_alpha17_execution_request_after_preflight_blocks_by_kill_switch_and_visible():
    c = client()
    conv = f'alpha17_kill_switch_{uuid4().hex}'
    complete_preflight_flow(c, conv)
    payload = c.post('/api/builder/engine-execution-request', json={'conversation_id': conv, 'client_event_id': f'{conv}_exec'}).json()
    assert payload['route'] == 'builder_engine_execution_blocked'
    assert payload['blocked'] is True
    assert payload['reason'] == 'engine_execution_disabled_by_kill_switch'
    assert payload['bridge_status'] == 'blocked_by_kill_switch'
    assert payload['execution_enabled'] is False
    assert payload['would_call']['legacy_target'] == 'legacy_builder_v4_contract_v1'
    assert_safety_false(payload)

    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['engine_execution']['found'] is True
    assert plan['engine_execution']['status'] == 'blocked_by_kill_switch'
    assert plan['engine_execution']['execution_enabled'] is False
    assert plan['engine_execution']['engine_called'] is False

    review = post_chat(c, conv, f'{conv}_review', 'Review')
    assert review['route'] == 'active_task_review'
    assert 'Builder engine execution lock' in review['message']
    assert 'blocked by kill switch' in review['message']
    assert 'No Builder engine was called' in review['message']

    preview = post_chat(c, conv, f'{conv}_preview', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['readiness']['safety']['engine_called'] is False
    assert preview['readiness']['safety']['excel_created'] is False


def test_alpha17_execution_request_pending_clarification_blocks():
    c = client()
    conv = f'alpha17_pending_{uuid4().hex}'
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    post_chat(c, conv, f'{conv}_002', 'Use Painting')
    payload = c.post('/api/builder/engine-execution-request', json={'conversation_id': conv, 'client_event_id': f'{conv}_exec'}).json()
    assert payload['route'] == 'builder_engine_execution_blocked'
    assert payload['reason'] == 'pending_clarification_exists'
    assert_safety_false(payload)
