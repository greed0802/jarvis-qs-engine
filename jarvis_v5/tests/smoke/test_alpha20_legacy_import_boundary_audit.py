from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client():
    return TestClient(app)


def start_complete_wall_types(c, conversation_id="alpha20_wall_contract"):
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
    snap = c.post('/api/builder/create-snapshot', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_snapshot"}).json()
    c.post('/api/builder/adapter-dry-run', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_adapter"})
    contract = c.post('/api/builder/engine-contract', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_contract"}).json()
    return snap, contract


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


def test_alpha20_version_and_locks():
    data = client().get('/api/version').json()
    assert data['version'] == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['engines_connected']['legacy_import_boundary_audit'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_snapshot_preview_export_messages_do_not_contain_alpha11():
    c = client()
    conv = 'alpha20_message_cleanup'
    snap, contract = start_complete_wall_types(c, conv)
    assert snap['route'] == 'builder_snapshot_created'
    assert 'alpha.11' not in snap['message']
    assert 'v5.0.0-alpha.36.3' in snap['message']
    preview = c.post('/api/chat', json={"conversation_id": conv, "client_event_id": conv+"_preview", "text": "Preview"}).json()
    assert preview['route'] == 'active_task_preview_stub'
    assert 'alpha.11' not in preview['message']
    assert 'v5.0.0-alpha.36.3' in preview['message']
    export = c.post('/api/chat', json={"conversation_id": conv, "client_event_id": conv+"_export", "text": "Export"}).json()
    assert export['route'] == 'active_task_export_stub'
    assert 'alpha.11' not in export['message']
    assert 'v5.0.0-alpha.36.3' in export['message']


def test_general_stub_message_does_not_contain_alpha11():
    data = client().post('/api/chat', json={"conversation_id": "alpha20_general", "client_event_id": "alpha20_general_hi", "text": "Hello there"}).json()
    assert data['route'] == 'general_stub'
    assert 'alpha.11' not in data['message']
    assert 'v5.0.0-alpha.36.3' in data['message']


def test_legacy_import_boundary_audit_locked_no_import():
    c = client()
    conv = 'alpha20_import_audit'
    data = c.post('/api/builder/legacy-import-boundary-audit', json={"conversation_id": conv, "client_event_id": "a20_audit_001", "write_report": True}).json()
    assert data['route'] == 'builder_legacy_import_boundary_audit'
    assert data['audit_status'] == 'locked_no_import'
    assert data['legacy_import_attempted'] is False
    assert data['legacy_module_imported'] is False
    assert data['legacy_builder_callable'] is False
    assert data['legacy_builder_called'] is False
    assert data['builder_engine_execution_enabled'] is False
    assert data['workbook_read_enabled'] is False
    assert data['excel_output_enabled'] is False
    assert data['bridge_stub']['status'] == 'stub_only'
    assert data['bridge_stub']['can_execute'] is False
    assert data['import_boundary']['policy'] == 'no_legacy_import_allowed'
    assert_safety(data)
    latest = c.get(f'/api/builder/legacy-import-boundary-audit/latest/{conv}').json()
    assert latest['route'] == 'builder_legacy_import_boundary_audit_latest'
    assert latest['audit_status'] == 'locked_no_import'
    assert_safety(latest)


def test_plan_shows_latest_legacy_import_boundary_audit():
    c = client()
    conv = 'alpha20_plan_audit_visible'
    audit = c.post('/api/builder/legacy-import-boundary-audit', json={"conversation_id": conv, "client_event_id": "a20_plan_audit", "write_report": True}).json()
    assert audit['route'] == 'builder_legacy_import_boundary_audit'
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['legacy_import_boundary_audit']['found'] is True
    assert plan['legacy_import_boundary_audit']['audit_status'] == 'locked_no_import'
    assert plan['legacy_import_boundary_audit']['legacy_import_attempted'] is False
    assert plan['legacy_import_boundary_audit']['legacy_module_imported'] is False
    assert plan['legacy_import_boundary_audit']['legacy_builder_called'] is False
