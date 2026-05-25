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


def assert_safety_false(payload: dict):
    assert payload['workbook_read'] is False
    assert payload['engine_called'] is False
    assert payload['excel_created'] is False
    assert payload['legacy_builder_called'] is False
    safety = payload.get('safety') or {}
    assert safety.get('workbook_read') is False
    assert safety.get('engine_called') is False
    assert safety.get('excel_created') is False
    assert safety.get('contract_only') is True
    assert safety.get('legacy_builder_called') is False


def complete_wall_types_to_adapter(c, conv: str):
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    attach_fixture(c, conv, f'{conv}_attach')
    post_chat(c, conv, f'{conv}_002', 'Use Wall Types')
    post_chat(c, conv, f'{conv}_003', 'Use XGETWALLAREA')
    post_chat(c, conv, f'{conv}_004', 'Unit m2')
    post_chat(c, conv, f'{conv}_005', 'Zone 1: Old and New')
    post_chat(c, conv, f'{conv}_006', 'Use Head 2 for Zone 1')
    post_chat(c, conv, f'{conv}_007', 'Levels GF to L3')
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': f'{conv}_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': f'{conv}_adapter'}).json()
    assert adapter['route'] == 'builder_adapter_dry_run'
    assert_safety_false(adapter)
    return snap, adapter


def test_alpha18_version():
    data = client().get('/api/version').json()
    assert data['version'] == 'v5.0.0-alpha.36.3'
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False


def test_alpha18_pending_clarification_blocked_responses_have_safety():
    c = client()
    conv = f'alpha18_pending_{uuid4().hex}'
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    pending = post_chat(c, conv, f'{conv}_002', 'Use Painting')
    assert pending['route'] == 'active_task_slot_edit_needs_clarification'

    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': f'{conv}_adapter'}).json()
    assert adapter['route'] == 'builder_adapter_dry_run_blocked'
    assert adapter['reason'] == 'pending_clarification_blocks_adapter_dry_run'
    assert_safety_false(adapter)

    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_blocked'
    assert contract['reason'] == 'pending_clarification_exists'
    assert_safety_false(contract)

    preflight = c.post('/api/builder/engine-preflight', json={'conversation_id': conv, 'client_event_id': f'{conv}_preflight'}).json()
    assert preflight['route'] == 'builder_engine_preflight_blocked'
    assert preflight['reason'] == 'pending_clarification_exists'
    assert_safety_false(preflight)

    execution = c.post('/api/builder/engine-execution-request', json={'conversation_id': conv, 'client_event_id': f'{conv}_exec'}).json()
    assert execution['route'] == 'builder_engine_execution_blocked'
    assert execution['reason'] == 'pending_clarification_exists'
    assert_safety_false(execution)


def test_alpha18_adapter_snapshot_mismatch_standardizes_reason():
    c = client()
    conv = f'alpha18_stale_adapter_{uuid4().hex}'
    complete_wall_types_to_adapter(c, conv)
    post_chat(c, conv, f'{conv}_edit', 'Levels GF to L5')
    snap2 = c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': f'{conv}_snap2'}).json()
    assert snap2['route'] == 'builder_snapshot_created'
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_blocked'
    assert contract['reason'] == 'adapter_is_stale'
    assert contract['validation'].get('stale_reason') == 'adapter_snapshot_mismatch'
    assert_safety_false(contract)


def test_alpha18_reinforcement_clarification_resolution_visible():
    c = client()
    conv = f'alpha18_reo_{uuid4().hex}'
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    attach_fixture(c, conv, f'{conv}_attach')
    first = post_chat(c, conv, f'{conv}_002', 'Use Reinforcement')
    assert first['route'] == 'active_task_slot_edit_needs_clarification'
    resolved = post_chat(c, conv, f'{conv}_003', 'Use XGETCUSTOM with Reinforcement Weight unit t')
    assert resolved['route'] == 'clarification_resolved'
    assert resolved['reason'] == 'clarification_answer_resolved'
    assert resolved['pending_clarification_id'] is None
    assert resolved['reducer_result']['requires_clarification'] is False
    assert resolved['reducer_result']['normalization']['status'] == 'clean'
    assert resolved['reducer_result']['trade_registry']['canonical_trade'] == 'Concrete / Reinforcement'

    post_chat(c, conv, f'{conv}_004', 'Zone 1: Old and New')
    post_chat(c, conv, f'{conv}_005', 'Use Head 2 for Zone 1')
    post_chat(c, conv, f'{conv}_006', 'Levels GF to L3')
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['plan_summary']['trade_profile'] == 'Concrete / Reinforcement'
    assert plan['plan_summary']['costx_function'] == 'XGETCUSTOM'
    assert plan['plan_summary']['custom_quantity'] == 'Reinforcement Weight'
    assert plan['plan_summary']['unit'] == 't'
    assert plan['normalization']['status'] == 'clean'
    assert plan['readiness']['pending_clarification_id'] is None
