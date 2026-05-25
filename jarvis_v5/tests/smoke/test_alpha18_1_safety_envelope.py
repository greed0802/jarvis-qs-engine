from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client():
    return TestClient(app)


def start_complete_wall_types(c, conversation_id="alpha181_snapshot_safety"):
    c.post('/api/chat', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_start", "text": "Build me a BOQ"})
    with open('jarvis_v5/tests/fixtures/Test.xlsx','rb') as f:
        c.post('/api/attach', data={"conversation_id": conversation_id, "client_event_id": conversation_id+"_attach", "text":"Here"}, files={"file": ("Test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    for suffix, text in [
        ("trade", "Use Wall Types"),
        ("function", "Use XGETWALLAREA"),
        ("unit", "Unit m2"),
        ("zone", "Zone 1: Old and New"),
        ("head", "Use Head 2 for Zone 1"),
        ("levels", "Levels GF to L3"),
    ]:
        c.post('/api/chat', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_"+suffix, "text": text})


def assert_safety(payload):
    assert payload['workbook_read'] is False
    assert payload['engine_called'] is False
    assert payload['excel_created'] is False
    assert payload['contract_only'] is True
    assert payload['legacy_builder_called'] is False
    assert payload['safety']['workbook_read'] is False
    assert payload['safety']['engine_called'] is False
    assert payload['safety']['excel_created'] is False
    assert payload['safety']['contract_only'] is True
    assert payload['safety']['legacy_builder_called'] is False


def test_alpha18_1_version():
    data = client().get('/api/version').json()
    assert data['version'] == 'v5.0.0-alpha.36.3'
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_snapshot_created_has_safety_envelope():
    c = client()
    conv = 'alpha181_snapshot_created'
    start_complete_wall_types(c, conv)
    data = c.post('/api/builder/create-snapshot', json={"conversation_id": conv, "client_event_id": conv+"_snapshot"}).json()
    assert data['route'] == 'builder_snapshot_created'
    assert_safety(data)


def test_snapshot_blocked_has_safety_envelope():
    c = client()
    conv = 'alpha181_snapshot_blocked'
    c.post('/api/chat', json={"conversation_id": conv, "client_event_id": conv+"_start", "text": "Build me a BOQ"})
    c.post('/api/chat', json={"conversation_id": conv, "client_event_id": conv+"_painting", "text": "Use Painting"})
    data = c.post('/api/builder/create-snapshot', json={"conversation_id": conv, "client_event_id": conv+"_snapshot"}).json()
    assert data['route'] == 'builder_snapshot_blocked'
    assert data['reason'] == 'pending_clarification_blocks_snapshot'
    assert_safety(data)


def test_boundary_audit_has_nested_safety():
    c = client()
    conv = 'alpha181_boundary_safety'
    start_complete_wall_types(c, conv)
    c.post('/api/builder/create-snapshot', json={"conversation_id": conv, "client_event_id": conv+"_snapshot"})
    c.post('/api/builder/adapter-dry-run', json={"conversation_id": conv, "client_event_id": conv+"_adapter"})
    contract = c.post('/api/builder/engine-contract', json={"conversation_id": conv, "client_event_id": conv+"_contract"}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    audit = c.post('/api/builder/engine-boundary-audit', json={"conversation_id": conv, "client_event_id": conv+"_audit"}).json()
    assert audit['route'] == 'builder_engine_boundary_audit'
    assert_safety(audit)


def test_clarification_resolved_flag_and_null_pending_id():
    c = client()
    conv = 'alpha181_clarification_flag'
    c.post('/api/chat', json={"conversation_id": conv, "client_event_id": conv+"_start", "text": "Build me a BOQ"})
    with open('jarvis_v5/tests/fixtures/Test.xlsx','rb') as f:
        c.post('/api/attach', data={"conversation_id": conv, "client_event_id": conv+"_attach", "text":"Here"}, files={"file": ("Test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    c.post('/api/chat', json={"conversation_id": conv, "client_event_id": conv+"_reinforcement", "text": "Use Reinforcement"})
    data = c.post('/api/chat', json={"conversation_id": conv, "client_event_id": conv+"_resolve", "text": "Use XGETCUSTOM with Reinforcement Weight unit t"}).json()
    assert data['route'] == 'clarification_resolved'
    assert data['clarification_resolved'] is True
    assert data['pending_clarification_id'] is None
    assert data['reducer_result']['requires_clarification'] is False
    assert data['reducer_result']['trade_registry']['matched'] is True
