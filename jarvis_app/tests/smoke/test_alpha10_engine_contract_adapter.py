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


def create_snapshot(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post('/api/builder/create-snapshot', json={
        'conversation_id': conversation_id,
        'client_event_id': event_id,
        'approve': True,
    }).json()


def adapter_dry_run(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post('/api/builder/adapter-dry-run', json={
        'conversation_id': conversation_id,
        'client_event_id': event_id,
    }).json()


def engine_contract(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post('/api/builder/engine-contract', json={
        'conversation_id': conversation_id,
        'client_event_id': event_id,
    }).json()


def complete_setup(c: TestClient, conv: str) -> None:
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


def test_complete_setup_creates_engine_contract_without_engine_or_excel():
    c = client()
    conv = f'alpha10_contract_full_{uuid4().hex}'
    complete_setup(c, conv)
    snap = create_snapshot(c, conv, 'a10_snap_001')
    assert snap['snapshot_status'] == 'current'
    assert snap['setup_completeness']['ready_for_future_engine'] is True
    dry = adapter_dry_run(c, conv, 'a10_adapter_001')
    assert dry['adapter_status'] == 'dry_run_ready'
    assert dry['workbook_read'] is False
    assert dry['engine_called'] is False
    assert dry['excel_created'] is False
    contract = engine_contract(c, conv, 'a10_contract_001')
    assert contract['route'] == 'builder_engine_contract_created'
    assert contract['contract_status'] == 'ready_for_engine_connection'
    assert contract['validation']['valid'] is True
    assert contract['workbook_read'] is False
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False
    payload = contract['contract']
    assert payload['engine_mode'] == 'contract_only'
    assert payload['safety']['legacy_builder_called'] is False
    assert payload['safety']['contract_only'] is True
    assert payload['workbook_ref']['filename'] == 'Test.xlsx'
    assert payload['builder_setup']['trade_profile'] == 'Wall Types'
    assert payload['builder_setup']['costx_function'] == 'XGETWALLAREA'
    assert payload['builder_setup']['unit'] == 'm2'
    assert payload['builder_setup']['dynamic_zones'][0]['values'] == ['Old', 'New']
    assert payload['builder_setup']['dynamic_zones'][0]['head_assignment'] == 'Head2'
    assert payload['builder_setup']['levels'] == ['GF', 'L1', 'L2', 'L3']

    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['engine_contract']['found'] is True
    assert plan['engine_contract']['status'] == 'ready_for_engine_connection'
    assert plan['engine_contract']['workbook_read'] is False
    assert plan['engine_contract']['engine_called'] is False
    assert plan['engine_contract']['excel_created'] is False


def test_incomplete_setup_blocks_engine_contract():
    c = client()
    conv = f'alpha10_contract_incomplete_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    assert post_chat(c, conv, f'{conv}_zone', 'Zone 1: Old and New')['route'] == 'active_task_slot_edit'
    snap = create_snapshot(c, conv, 'a10_inc_snap')
    assert snap['blocked'] is False
    dry = adapter_dry_run(c, conv, 'a10_inc_adapter')
    assert dry['blocked'] is False
    contract = engine_contract(c, conv, 'a10_inc_contract')
    assert contract['route'] == 'builder_engine_contract_blocked'
    assert contract['blocked'] is True
    assert contract['validation']['valid'] is False
    assert 'setup_not_ready_for_future_engine' in contract['validation']['issues']
    assert contract['workbook_read'] is False
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False


def test_stale_snapshot_blocks_engine_contract():
    c = client()
    conv = f'alpha10_contract_stale_{uuid4().hex}'
    complete_setup(c, conv)
    create_snapshot(c, conv, 'a10_stale_snap')
    adapter_dry_run(c, conv, 'a10_stale_adapter')
    changed = post_chat(c, conv, 'a10_stale_change', 'Add Same to Zone 1')
    assert changed['snapshot']['status'] == 'stale'
    contract = engine_contract(c, conv, 'a10_stale_contract')
    assert contract['route'] == 'builder_engine_contract_blocked'
    assert contract['blocked'] is True
    assert contract['reason'] in {'snapshot_is_stale', 'adapter_is_stale'}
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False


def test_pending_clarification_blocks_engine_contract():
    c = client()
    conv = f'alpha10_contract_pending_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    conflict = post_chat(c, conv, f'{conv}_002', 'Use Wall Types and Structural Steel')
    assert conflict['route'] == 'active_task_slot_edit_needs_clarification'
    contract = engine_contract(c, conv, 'a10_pending_contract')
    assert contract['route'] == 'builder_engine_contract_blocked'
    assert contract['blocked'] is True
    assert contract['reason'] == 'pending_clarification_exists'
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False


def test_preview_stays_stub_after_engine_contract():
    c = client()
    conv = f'alpha10_contract_preview_{uuid4().hex}'
    complete_setup(c, conv)
    create_snapshot(c, conv, 'a10_prev_snap')
    adapter_dry_run(c, conv, 'a10_prev_adapter')
    engine_contract(c, conv, 'a10_prev_contract')
    preview = post_chat(c, conv, 'a10_preview_001', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['reason'] == 'preview_engine_not_connected'
    assert preview['adapter']['engine_called'] is False
    assert preview['adapter']['excel_created'] is False
    assert preview['adapter']['workbook_read'] is False
