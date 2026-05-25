from __future__ import annotations

from pathlib import Path
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


def complete_wall_types_setup(c, conv: str):
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    attach_fixture(c, conv, f'{conv}_attach')
    post_chat(c, conv, f'{conv}_002', 'Use Wall Types')
    post_chat(c, conv, f'{conv}_003', 'Use XGETWALLAREA')
    post_chat(c, conv, f'{conv}_004', 'Unit m2')
    post_chat(c, conv, f'{conv}_005', 'Zone 1: Old and New')
    post_chat(c, conv, f'{conv}_006', 'Use Head 2 for Zone 1')
    post_chat(c, conv, f'{conv}_007', 'Levels GF to L3')


def create_contract_flow(c, conv: str):
    complete_wall_types_setup(c, conv)
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': f'{conv}_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': f'{conv}_adapter'}).json()
    assert adapter['route'] == 'builder_adapter_dry_run'
    assert adapter['workbook_read'] is False
    assert adapter['engine_called'] is False
    assert adapter['excel_created'] is False
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    return contract


def test_alpha16_version():
    c = client()
    data = c.get('/api/version').json()
    assert data['version'] == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False


def test_alpha16_valid_preflight_no_engine_and_plan_review_visibility():
    c = client()
    conv = f'alpha16_full_{uuid4().hex}'
    contract = create_contract_flow(c, conv)
    audit = c.post('/api/builder/engine-boundary-audit', json={'conversation_id': conv, 'client_event_id': f'{conv}_audit'}).json()
    assert audit['route'] == 'builder_engine_boundary_audit'

    preflight = c.post('/api/builder/engine-preflight', json={'conversation_id': conv, 'client_event_id': f'{conv}_preflight'}).json()
    assert preflight['route'] == 'builder_engine_preflight_ready'
    assert preflight['blocked'] is False
    assert preflight['preflight_status'] == 'ready_for_future_engine_adapter'
    assert preflight['contract_id'] == contract['contract_id']
    assert preflight['contract_schema_version'] == 'builder_contract_v1'
    assert preflight['legacy_target'] == 'legacy_builder_v4_contract_v1'
    assert preflight['compatibility']['valid'] is True
    assert preflight['compatibility']['missing_required_fields'] == []
    assert preflight['workbook_read'] is False
    assert preflight['engine_called'] is False
    assert preflight['excel_created'] is False
    assert preflight['legacy_builder_called'] is False
    assert preflight['safety']['contract_only'] is True
    assert preflight['fixture_path']
    assert Path(preflight['fixture_path']).exists()

    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['engine_preflight']['found'] is True
    assert plan['engine_preflight']['status'] == 'ready_for_future_engine_adapter'
    assert plan['engine_preflight']['compatibility_score'] == 100
    assert plan['engine_preflight']['engine_called'] is False

    review = post_chat(c, conv, f'{conv}_review', 'Review')
    assert review['route'] == 'active_task_review'
    assert 'Builder engine preflight' in review['message']
    assert 'No Builder engine was called' in review['message']
    assert 'No Excel file was created' in review['message']

    preview = post_chat(c, conv, f'{conv}_preview', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['reason'] == 'preview_engine_not_connected'


def test_alpha16_preflight_blocked_without_contract():
    c = client()
    conv = f'alpha16_no_contract_{uuid4().hex}'
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    preflight = c.post('/api/builder/engine-preflight', json={'conversation_id': conv, 'client_event_id': f'{conv}_preflight'}).json()
    assert preflight['route'] == 'builder_engine_preflight_blocked'
    assert preflight['reason'] == 'engine_contract_not_found'
    assert preflight['workbook_read'] is False
    assert preflight['engine_called'] is False
    assert preflight['excel_created'] is False
    assert preflight['legacy_builder_called'] is False


def test_alpha16_preflight_blocked_pending_clarification():
    c = client()
    conv = f'alpha16_pending_{uuid4().hex}'
    post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')
    post_chat(c, conv, f'{conv}_002', 'Use Painting')
    preflight = c.post('/api/builder/engine-preflight', json={'conversation_id': conv, 'client_event_id': f'{conv}_preflight'}).json()
    assert preflight['route'] == 'builder_engine_preflight_blocked'
    assert preflight['reason'] == 'pending_clarification_exists'
    assert preflight['workbook_read'] is False
    assert preflight['engine_called'] is False
    assert preflight['excel_created'] is False
    assert preflight['legacy_builder_called'] is False


def test_alpha16_golden_contract_fixture_has_no_workbook_contents():
    c = client()
    conv = f'alpha16_fixture_{uuid4().hex}'
    create_contract_flow(c, conv)
    preflight = c.post('/api/builder/engine-preflight', json={'conversation_id': conv, 'client_event_id': f'{conv}_preflight'}).json()
    fixture = Path(preflight['fixture_path'])
    data = fixture.read_text(encoding='utf-8')
    assert 'builder_engine_contract_fixture_v1' in data
    assert 'Test.xlsx' in data
    assert 'workbook_read' in data
    # The fixture should contain contract metadata only, not workbook sheet/cell contents.
    assert 'worksheet' not in data.lower()
    assert 'cell' not in data.lower()
