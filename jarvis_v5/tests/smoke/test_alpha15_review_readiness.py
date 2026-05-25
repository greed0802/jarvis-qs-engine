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
        r = c.post('/api/attach', data={'conversation_id': conv, 'client_event_id': event, 'text': 'Here'}, files={'file': ('Test.xlsx', fh, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')})
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


def test_alpha15_plan_readiness_incomplete_no_engine():
    c = client()
    conv = f'alpha15_plan_incomplete_{uuid4().hex}'
    post_chat(c, conv, 'a15_inc_001', 'Build me a BOQ')
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['readiness']['status'] in {'waiting_for_workbook', 'incomplete_setup'}
    assert plan['readiness']['can_create_snapshot'] is False
    assert plan['readiness']['can_create_engine_contract'] is False
    assert plan['readiness']['safety']['workbook_read'] is False
    assert plan['readiness']['safety']['engine_called'] is False
    assert plan['readiness']['safety']['excel_created'] is False


def test_alpha15_review_low_risk_trade_readable():
    c = client()
    conv = f'alpha15_review_carpet_{uuid4().hex}'
    post_chat(c, conv, 'a15_carpet_001', 'Build me a BOQ')
    post_chat(c, conv, 'a15_carpet_002', 'Use Carpet')
    review = post_chat(c, conv, 'a15_carpet_003', 'Review')
    assert review['route'] == 'active_task_review'
    assert review['readiness']['status'] in {'waiting_for_workbook', 'incomplete_setup'}
    assert 'Floor Finishes / Carpet' in review['message']
    assert 'Trade registry' in review['message']
    assert review['readiness']['safety']['engine_called'] is False


def test_alpha15_pending_clarification_readiness_blocks():
    c = client()
    conv = f'alpha15_painting_block_{uuid4().hex}'
    post_chat(c, conv, 'a15_paint_001', 'Build me a BOQ')
    post_chat(c, conv, 'a15_paint_002', 'Use Painting')
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['readiness']['status'] == 'needs_clarification'
    assert plan['readiness']['can_create_snapshot'] is False
    assert plan['readiness']['can_create_engine_contract'] is False
    review = post_chat(c, conv, 'a15_paint_003', 'Review')
    assert 'Open clarification' in review['message']
    assert 'Answer or cancel' in review['message']


def test_alpha15_contract_ready_review_and_boundary_runner_allowed():
    c = client()
    conv = f'alpha15_contract_ready_{uuid4().hex}'
    complete_wall_types_setup(c, conv)
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': conv, 'client_event_id': 'a15_snap'}).json()
    assert snap['readiness']['status'] == 'ready_for_snapshot' or snap['readiness']['status'] == 'snapshot_current'
    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': conv, 'client_event_id': 'a15_adapter'}).json()
    assert adapter['readiness']['can_create_engine_contract'] is True
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': conv, 'client_event_id': 'a15_contract'}).json()
    assert contract['readiness']['status'] == 'contract_ready'
    audit = c.post('/api/builder/engine-boundary-audit', json={'conversation_id': conv, 'client_event_id': 'a15_audit'}).json()
    assert audit['route'] == 'builder_engine_boundary_audit'
    assert audit['readiness']['status'] == 'contract_ready'
    review = post_chat(c, conv, 'a15_review', 'Review')
    assert 'Engine contract' in review['message']
    assert 'Preview/export engines are not connected' in review['message']
