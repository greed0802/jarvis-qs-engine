from __future__ import annotations

from io import BytesIO
from uuid import uuid4
from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client() -> TestClient:
    return TestClient(app)


def post_chat(c: TestClient, conversation_id: str, event_id: str, text: str) -> dict:
    return c.post('/api/chat', json={
        'conversation_id': conversation_id,
        'client_event_id': event_id,
        'text': text,
    }).json()


def attach_workbook(c: TestClient, conversation_id: str, event_id: str, filename: str = 'Test.xlsx') -> dict:
    return c.post(
        '/api/attach',
        data={'conversation_id': conversation_id, 'client_event_id': event_id, 'text': 'Here'},
        files={'file': (filename, BytesIO(b'fake workbook bytes - not read'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
    ).json()


def complete_contract_flow(c: TestClient, conv: str) -> dict:
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    attached = attach_workbook(c, conv, f'{conv}_attach')
    assert attached['route'] == 'attachment_bind'
    assert attached['reducer_result']['workbook_read'] is False
    for idx, text in enumerate([
        'Use Wall Types',
        'Use XGETWALLAREA',
        'Unit m2',
        'Zone 1: Old and New',
        'Use Head 2 for Zone 1',
        'Levels GF to L3',
    ], start=2):
        assert post_chat(c, conv, f'{conv}_{idx}', text)['route'] == 'active_task_slot_edit'
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': f'{conv}_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    dry = c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': f'{conv}_adapter'}).json()
    assert dry['route'] == 'builder_adapter_dry_run'
    assert dry['engine_called'] is False
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    return contract


def test_boundary_audit_maps_valid_contract_without_engine_or_excel():
    c = client()
    conv = f'alpha13_boundary_valid_{uuid4().hex}'
    contract = complete_contract_flow(c, conv)
    audit = c.post('/api/builder/engine-boundary-audit', json={'conversation_id': conv, 'client_event_id': f'{conv}_audit'}).json()
    assert audit['route'] == 'builder_engine_boundary_audit'
    assert audit['blocked'] is False
    assert audit['audit_status'] in {'compatible', 'compatible_with_warnings'}
    assert audit['contract_id'] == contract['contract_id']
    assert audit['contract_schema_version'] == 'builder_contract_v1'
    assert audit['legacy_target'] == 'legacy_builder_v4_contract_v1'
    assert audit['missing_legacy_required_fields'] == []
    assert audit['workbook_read'] is False
    assert audit['engine_called'] is False
    assert audit['excel_created'] is False
    assert audit['legacy_builder_called'] is False
    assert audit['mapping']['trade_profile']['legacy_field'] == 'trade_profile'
    assert audit['mapping']['costx_function']['legacy_field'] == 'selected_function'
    assert audit['mapping']['dynamic_zones']['status'] == 'mapped'


def test_boundary_audit_blocks_when_no_contract_exists():
    c = client()
    conv = f'alpha13_boundary_missing_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    audit = c.post('/api/builder/engine-boundary-audit', json={'conversation_id': conv, 'client_event_id': f'{conv}_audit'}).json()
    assert audit['route'] == 'builder_engine_boundary_audit_blocked'
    assert audit['blocked'] is True
    assert audit['audit_status'] == 'not_ready'
    assert audit['reason'] == 'contract_not_found'
    assert audit['engine_called'] is False
    assert audit['excel_created'] is False
    assert audit['workbook_read'] is False
    assert audit['legacy_builder_called'] is False


def test_latest_contract_replay_and_plan_include_boundary_audit_summary():
    c = client()
    conv = f'alpha13_boundary_plan_{uuid4().hex}'
    contract = complete_contract_flow(c, conv)
    latest = c.get(f'/api/builder/engine-contract/latest/{conv}').json()
    assert latest['route'] == 'builder_engine_contract_latest_replay'
    assert latest['contract_id'] == contract['contract_id']
    assert latest['engine_boundary_audit']['found'] is True
    assert latest['engine_boundary_audit']['legacy_target'] == 'legacy_builder_v4_contract_v1'
    assert latest['engine_boundary_audit']['missing_legacy_required_fields'] == []
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['engine_contract']['found'] is True
    assert plan['engine_contract']['engine_boundary_audit']['found'] is True
    assert plan['engine_contract']['engine_boundary_audit']['audit_status'] in {'compatible', 'compatible_with_warnings'}
    assert plan['engine_contract']['engine_boundary_audit']['engine_called'] is False


def test_preview_remains_stub_after_boundary_audit():
    c = client()
    conv = f'alpha13_boundary_preview_{uuid4().hex}'
    complete_contract_flow(c, conv)
    audit = c.post('/api/builder/engine-boundary-audit', json={'conversation_id': conv, 'client_event_id': f'{conv}_audit'}).json()
    assert audit['engine_called'] is False
    preview = post_chat(c, conv, f'{conv}_preview', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['reason'] == 'preview_engine_not_connected'
    assert preview['adapter']['engine_called'] is False
    assert preview['adapter']['excel_created'] is False
    assert preview['adapter']['workbook_read'] is False
