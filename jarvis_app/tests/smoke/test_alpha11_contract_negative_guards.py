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
    assert attach_workbook(c, conv, f'{conv}_attach')['route'] == 'attachment_bind'
    for idx, text in enumerate([
        'Use Wall Types',
        'Use XGETWALLAREA',
        'Unit m2',
        'Zone 1: Old and New',
        'Use Head 2 for Zone 1',
        'Levels GF to L3',
    ], start=2):
        assert post_chat(c, conv, f'{conv}_{idx}', text)['route'] == 'active_task_slot_edit'


def test_alpha11_valid_contract_and_replay_endpoints():
    c = client()
    conv = f'alpha11_contract_full_{uuid4().hex}'
    complete_setup(c, conv)
    assert create_snapshot(c, conv, 'a11_snap')['snapshot_status'] == 'current'
    assert adapter_dry_run(c, conv, 'a11_adapter')['adapter_status'] == 'dry_run_ready'
    contract = engine_contract(c, conv, 'a11_contract')
    assert contract['route'] == 'builder_engine_contract_created'
    assert contract['contract_created'] is True
    assert contract['contract_status'] == 'ready_for_engine_connection'
    assert contract['validation']['valid'] is True
    assert contract['workbook_read'] is False
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False
    assert contract['contract']['safety']['contract_only'] is True
    assert contract['contract']['safety']['legacy_builder_called'] is False
    contract_id = contract['contract_id']

    replay = c.get(f'/api/builder/engine-contract/{contract_id}').json()
    assert replay['route'] == 'builder_engine_contract_replay'
    assert replay['found'] is True
    assert replay['contract']['contract_id'] == contract_id
    assert replay['contract_only'] is True
    assert replay['engine_called'] is False
    assert replay['excel_created'] is False

    latest = c.get(f'/api/builder/engine-contract/latest/{conv}').json()
    assert latest['found'] is True
    assert latest['contract_id'] == contract_id
    assert latest['contract']['contract_id'] == contract_id

    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['engine_contract']['found'] is True
    assert plan['engine_contract']['replay_url'] == f'/api/builder/engine-contract/{contract_id}'


def test_alpha11_incomplete_setup_blocks_contract_with_no_engine_side_effects():
    c = client()
    conv = f'alpha11_contract_incomplete_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    assert post_chat(c, conv, f'{conv}_zone', 'Zone 1: Old and New')['route'] == 'active_task_slot_edit'
    assert create_snapshot(c, conv, 'a11_inc_snap')['blocked'] is False
    assert adapter_dry_run(c, conv, 'a11_inc_adapter')['blocked'] is False
    blocked = engine_contract(c, conv, 'a11_inc_contract')
    assert blocked['route'] == 'builder_engine_contract_blocked'
    assert blocked['blocked'] is True
    assert blocked['contract_created'] is False
    assert blocked['reason'] == 'setup_not_ready_for_future_engine'
    assert 'setup_not_ready_for_future_engine' in blocked['validation']['issues']
    assert blocked['workbook_read'] is False
    assert blocked['engine_called'] is False
    assert blocked['excel_created'] is False
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['engine_contract']['found'] is False
    assert plan['engine_contract']['last_blocked_attempt']['reason'] == 'setup_not_ready_for_future_engine'


def test_alpha11_contract_requires_current_adapter():
    c = client()
    conv = f'alpha11_contract_no_adapter_{uuid4().hex}'
    complete_setup(c, conv)
    create_snapshot(c, conv, 'a11_no_adapter_snap')
    blocked = engine_contract(c, conv, 'a11_no_adapter_contract')
    assert blocked['route'] == 'builder_engine_contract_blocked'
    assert blocked['reason'] == 'adapter_required'
    assert blocked['engine_called'] is False
    assert blocked['excel_created'] is False


def test_alpha11_stale_snapshot_or_adapter_blocks_contract():
    c = client()
    conv = f'alpha11_contract_stale_{uuid4().hex}'
    complete_setup(c, conv)
    create_snapshot(c, conv, 'a11_stale_snap')
    adapter_dry_run(c, conv, 'a11_stale_adapter')
    changed = post_chat(c, conv, 'a11_stale_change', 'Add Same to Zone 1')
    assert changed['snapshot']['status'] == 'stale'
    blocked = engine_contract(c, conv, 'a11_stale_contract')
    assert blocked['route'] == 'builder_engine_contract_blocked'
    assert blocked['blocked'] is True
    assert blocked['reason'] in {'snapshot_is_stale', 'adapter_is_stale'}
    assert blocked['engine_called'] is False
    assert blocked['excel_created'] is False


def test_alpha11_pending_clarification_and_conflict_block_contract():
    c = client()
    conv = f'alpha11_contract_pending_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    conflict = post_chat(c, conv, f'{conv}_002', 'Use Count unit m2')
    assert conflict['route'] == 'active_task_slot_edit_needs_clarification'
    blocked = engine_contract(c, conv, 'a11_pending_contract')
    assert blocked['route'] == 'builder_engine_contract_blocked'
    assert blocked['blocked'] is True
    assert blocked['reason'] == 'pending_clarification_exists'
    assert blocked['pending_clarification_id']
    assert blocked['engine_called'] is False
    assert blocked['excel_created'] is False


def test_alpha11_preview_still_stubbed_after_contract():
    c = client()
    conv = f'alpha11_contract_preview_{uuid4().hex}'
    complete_setup(c, conv)
    create_snapshot(c, conv, 'a11_prev_snap')
    adapter_dry_run(c, conv, 'a11_prev_adapter')
    engine_contract(c, conv, 'a11_prev_contract')
    preview = post_chat(c, conv, 'a11_preview', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['reason'] == 'preview_engine_not_connected'
    assert preview['adapter']['engine_called'] is False
    assert preview['adapter']['excel_created'] is False
    assert preview['adapter']['workbook_read'] is False
