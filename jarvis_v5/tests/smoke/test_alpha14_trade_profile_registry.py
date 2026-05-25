from __future__ import annotations

from io import BytesIO
from uuid import uuid4
from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client() -> TestClient:
    return TestClient(app)


def post_chat(c: TestClient, conversation_id: str, event_id: str, text: str) -> dict:
    return c.post('/api/chat', json={
        'conversation_id': conversation_id,
        'client_event_id': event_id,
        'text': text,
    }).json()


def attach_workbook(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post(
        '/api/attach',
        data={'conversation_id': conversation_id, 'client_event_id': event_id, 'text': 'Here'},
        files={'file': ('Test.xlsx', BytesIO(b'fake workbook bytes - not read'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
    ).json()


def test_version_is_alpha14_no_engine():
    c = client()
    data = c.get('/api/version').json()
    assert data['version'] == APP_VERSION
    assert data['engines_connected']['builder'] is False
    assert data['engines_connected']['formatter'] is False
    assert data['engines_connected']['qa_checker'] is False


def test_low_risk_carpet_trade_normalizes_without_engine():
    c = client()
    conv = f'alpha14_carpet_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    result = post_chat(c, conv, f'{conv}_002', 'Use Carpet')
    assert result['route'] == 'active_task_slot_edit'
    assert result['reducer_result']['trade_registry']['matched'] is True
    assert result['reducer_result']['trade_registry']['registry_key'] == 'carpet'
    assert result['reducer_result']['normalization']['status'] == 'clean'
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['plan_summary']['trade_profile'] == 'Floor Finishes / Carpet'
    assert plan['plan_summary']['trade_registry']['normalization_mode'] == 'auto'


def test_ambiguous_painting_requires_clarification_and_does_not_mutate_trade():
    c = client()
    conv = f'alpha14_paint_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    result = post_chat(c, conv, f'{conv}_002', 'Use Painting')
    assert result['route'] == 'active_task_slot_edit_needs_clarification'
    assert result['reason'] == 'slot_reducer_requires_clarification'
    assert result['active_task_status'] == 'needs_clarification'
    assert result['pending_clarification_id']
    assert result['reducer_result']['trade_registry']['registry_key'] == 'painting'
    assert result['reducer_result']['normalization']['status'] == 'needs_clarification'
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['plan_summary']['trade_profile'] is None


def test_high_risk_reinforcement_clarification_can_resolve_to_custom_quantity():
    c = client()
    conv = f'alpha14_reinf_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    ask = post_chat(c, conv, f'{conv}_002', 'Use Reinforcement')
    assert ask['route'] == 'active_task_slot_edit_needs_clarification'
    answer = post_chat(c, conv, f'{conv}_003', 'Use XGETCUSTOM with Reinforcement Weight unit t')
    assert answer['route'] == 'clarification_resolved'
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['plan_summary']['trade_profile'] == 'Concrete / Reinforcement'
    assert plan['plan_summary']['costx_function'] == 'XGETCUSTOM'
    assert plan['plan_summary']['custom_quantity'] == 'Reinforcement Weight'
    assert plan['plan_summary']['unit'] == 't'
    assert plan['plan_summary']['trade_registry']['risk'] == 'high'


def test_wall_types_contract_flow_still_passes_after_registry_patch():
    c = client()
    conv = f'alpha14_wall_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    assert attach_workbook(c, conv, f'{conv}_attach')['route'] == 'attachment_bind'
    for idx, text in enumerate([
        'Use Wall Types', 'Use XGETWALLAREA', 'Unit m2', 'Zone 1: Old and New', 'Use Head 2 for Zone 1', 'Levels GF to L3'
    ], start=2):
        assert post_chat(c, conv, f'{conv}_{idx}', text)['route'] == 'active_task_slot_edit'
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': f'{conv}_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    dry = c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': f'{conv}_adapter'}).json()
    assert dry['route'] == 'builder_adapter_dry_run'
    assert dry['engine_called'] is False
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False
    assert contract['workbook_read'] is False
    latest = c.get(f'/api/builder/engine-contract/latest/{conv}').json()
    assert latest['engine_boundary_audit']['found'] is True
    assert latest['engine_boundary_audit']['engine_called'] is False


def test_unresolved_ambiguous_trade_blocks_contract_without_engine():
    c = client()
    conv = f'alpha14_paint_block_{uuid4().hex}'
    assert post_chat(c, conv, f'{conv}_001', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    assert attach_workbook(c, conv, f'{conv}_attach')['route'] == 'attachment_bind'
    ask = post_chat(c, conv, f'{conv}_002', 'Use Painting')
    assert ask['route'] == 'active_task_slot_edit_needs_clarification'
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': f'{conv}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_blocked'
    assert contract['reason'] == 'pending_clarification_exists'
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False
    assert contract['workbook_read'] is False
