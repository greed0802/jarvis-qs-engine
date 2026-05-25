from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def test_alpha26_version_and_shadow_probe_lock():
    client = TestClient(app)
    version = client.get('/api/version').json()
    assert version['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert version['engines_connected']['legacy_bridge_shadow_probe'] is False
    locks = version['execution_locks']
    assert locks['builder_engine_execution_enabled'] is False
    assert locks['legacy_builder_callable'] is False
    assert locks['workbook_read_enabled'] is False
    assert locks['excel_output_enabled'] is False


def test_alpha26_shadow_probe_without_contract_is_metadata_only():
    client = TestClient(app)
    data = client.post('/api/builder/legacy-bridge-shadow-probe', json={
        'conversation_id': 'smoke_alpha26_empty',
        'client_event_id': 'smoke_a26_empty',
        'allow_missing_contract': True,
    }).json()
    assert data['route'] == 'builder_legacy_bridge_shadow_probe'
    assert data['metadata_only'] is True
    assert data['execution_enabled'] is False
    assert data['workbook_read'] is False
    assert data['engine_called'] is False
    assert data['excel_created'] is False
    assert data['legacy_builder_called'] is False
    assert data['bridge_probe']['legacy_import_attempted'] is False
    assert data['bridge_probe']['legacy_module_imported'] is False
    assert data['bridge_probe']['legacy_callable_available'] is False
    assert data['bridge_probe']['safe_for_execution'] is False
    for blocker in ['workbook_read_disabled', 'legacy_builder_callable_disabled', 'excel_output_disabled', 'execution_kill_switch']:
        assert blocker in data['blocked_by_policy']


def _post_chat(client, conversation_id: str, event: str, text: str) -> dict:
    return client.post('/api/chat', json={
        'conversation_id': conversation_id,
        'client_event_id': event,
        'text': text,
    }).json()


def test_alpha26_shadow_probe_with_contract_still_does_not_execute():
    client = TestClient(app)
    cid = 'smoke_alpha26_contract'
    assert _post_chat(client, cid, 'start', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    with open('jarvis_v5/tests/fixtures/Test.xlsx', 'rb') as fh:
        attach = client.post('/api/attach', data={'conversation_id': cid, 'client_event_id': 'attach', 'text': 'Here'}, files={'file': ('Test.xlsx', fh, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}).json()
    assert attach['route'] == 'attachment_bind'
    for event, text in [
        ('trade', 'Use Wall Types'),
        ('func', 'Use XGETWALLAREA'),
        ('unit', 'Unit m2'),
        ('zone', 'Zone 1: Old and New'),
        ('head', 'Use Head 2 for Zone 1'),
        ('levels', 'Levels GF to L3'),
    ]:
        assert _post_chat(client, cid, event, text)['route'] == 'active_task_slot_edit'
    assert client.post('/api/builder/create-snapshot', json={'conversation_id': cid, 'client_event_id': 'snap'}).json()['route'] == 'builder_snapshot_created'
    assert client.post('/api/builder/adapter-dry-run', json={'conversation_id': cid, 'client_event_id': 'adapter'}).json()['route'] == 'builder_adapter_dry_run'
    contract = client.post('/api/builder/engine-contract', json={'conversation_id': cid, 'client_event_id': 'contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    data = client.post('/api/builder/legacy-bridge-shadow-probe', json={'conversation_id': cid, 'client_event_id': 'probe', 'allow_missing_contract': False}).json()
    assert data['route'] == 'builder_legacy_bridge_shadow_probe'
    assert data['reason'] == 'legacy_builder_execution_disabled'
    assert data['bridge_probe']['contract_found'] is True
    assert data['bridge_probe']['contract_ready'] is True
    assert data['bridge_probe']['safe_for_future_mapping'] is True
    assert data['bridge_probe']['safe_for_execution'] is False
    assert data['workbook_read'] is False
    assert data['engine_called'] is False
    assert data['excel_created'] is False
    assert data['legacy_builder_called'] is False
