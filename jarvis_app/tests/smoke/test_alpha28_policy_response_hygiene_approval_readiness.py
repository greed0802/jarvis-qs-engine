from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


RAW_PATH_KEYS = {
    "absolute_path",
    "file_path",
    "local_path",
    "stored_path",
    "resolved_path",
    "raw_path",
    "attachment_path",
    "directory",
    "parent",
    "full_path",
}


def _client():
    return TestClient(app)


def _chat(client, cid: str, event: str, text: str) -> dict:
    return client.post('/api/chat', json={
        'conversation_id': cid,
        'client_event_id': event,
        'text': text,
    }).json()


def _contains_key(payload, keys: set[str]) -> bool:
    if isinstance(payload, dict):
        return any(str(key) in keys or _contains_key(value, keys) for key, value in payload.items())
    if isinstance(payload, list):
        return any(_contains_key(item, keys) for item in payload)
    return False


def _ready_contract_policy_response(client, cid: str) -> dict:
    assert _chat(client, cid, 'start', 'Build me a BOQ')['route'] == 'new_builder_task_shell'
    with open('jarvis_v5/tests/fixtures/Test.xlsx', 'rb') as fh:
        attach = client.post(
            '/api/attach',
            data={'conversation_id': cid, 'client_event_id': 'attach', 'text': 'Here'},
            files={'file': ('Test.xlsx', fh, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        ).json()
    assert attach['route'] == 'attachment_bind'
    for event, text in [
        ('trade', 'Use Wall Types'),
        ('func', 'Use XGETWALLAREA'),
        ('unit', 'Unit m2'),
        ('zone', 'Zone 1: Old and New'),
        ('head', 'Use Head 2 for Zone 1'),
        ('levels', 'Levels GF to L3'),
    ]:
        assert _chat(client, cid, event, text)['route'] == 'active_task_slot_edit'
    assert client.post('/api/builder/create-snapshot', json={'conversation_id': cid, 'client_event_id': 'snap'}).json()['route'] == 'builder_snapshot_created'
    assert client.post('/api/builder/adapter-dry-run', json={'conversation_id': cid, 'client_event_id': 'adapter'}).json()['route'] == 'builder_adapter_dry_run'
    contract = client.post('/api/builder/engine-contract', json={'conversation_id': cid, 'client_event_id': 'contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    return client.post('/api/builder/preview-execution-policy', json={
        'conversation_id': cid,
        'client_event_id': 'a28_policy',
        'requested_action': 'preview',
    }).json()


def test_alpha28_version_policy_response_hygiene_metadata():
    client = _client()
    version = client.get('/api/version').json()
    assert version['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert version['scope'] == 'workbook_read_policy_review_no_content_read'
    assert version['scope_metadata']['policy_response_hygiene'] is True
    assert version['scope_metadata']['contract_summary_public_only'] is True
    assert version['scope_metadata']['approval_token_policy_schema_defined'] is True
    assert version['scope_metadata']['preview_approval_readiness_defined'] is True
    assert version['scope_metadata']['export_approval_readiness_defined'] is True
    locks = version['execution_locks']
    assert locks['builder_engine_execution_enabled'] is False
    assert locks['legacy_builder_callable'] is False
    assert locks['workbook_read_enabled'] is False
    assert locks['excel_output_enabled'] is False


def test_alpha28_policy_without_contract_public_summary_and_approval_lock():
    client = _client()
    data = client.post('/api/builder/preview-execution-policy', json={
        'conversation_id': 'smoke_alpha28_no_contract',
        'client_event_id': 'a28_no_contract',
        'requested_action': 'preview',
    }).json()
    assert data['route'] == 'builder_preview_execution_policy'
    assert data['metadata_only'] is True
    assert data['execution_enabled'] is False
    assert data['blocked'] is True
    assert data['reason'] == 'engine_contract_not_found'
    assert data['workbook_read'] is False
    assert data['engine_called'] is False
    assert data['excel_created'] is False
    assert data['legacy_builder_called'] is False
    assert data['contract'] is None
    assert data['contract_summary']['found'] is False
    assert data['contract_summary']['ready'] is False
    assert data['safety']['raw_contract_payload_returned'] is False
    assert data['safety']['contract_summary_has_raw_path_key'] is False
    assert data['approval_token_policy']['token_issued'] is False
    assert data['approval_token_policy']['status'] == 'schema_defined_not_issued'
    assert data['preview_approval_readiness']['can_execute_preview'] is False
    assert data['preview_approval_readiness']['approval_token_issued'] is False
    assert data['export_approval_readiness']['can_execute_export'] is False
    assert data['export_approval_readiness']['requires_successful_preview'] is True
    assert 'workbook_read_disabled' in data['blocked_by_policy']
    assert 'execution_kill_switch' in data['blocked_by_policy']


def test_alpha28_ready_contract_returns_scrubbed_summary_only():
    client = _client()
    data = _ready_contract_policy_response(client, 'smoke_alpha28_contract')
    assert data['route'] == 'builder_preview_execution_policy'
    assert data['reason'] == 'preview_execution_disabled_by_policy'
    assert data['contract_found'] is True
    assert data['contract_ready'] is True
    assert data['contract'] is None
    summary = data['contract_summary']
    assert summary['found'] is True
    assert summary['ready'] is True
    assert summary['contract_id'] == data['contract_id']
    assert summary['workbook_ref']['filename'] == 'Test.xlsx'
    assert set(summary['workbook_ref']).issubset({'filename', 'workbook_id', 'source'})
    assert summary['setup_summary']['trade_profile'] == 'Wall Types'
    assert summary['setup_summary']['costx_function'] == 'XGETWALLAREA'
    assert summary['setup_summary']['unit'] == 'm2'
    assert data['safety']['contract_summary_public_only'] is True
    assert data['safety']['raw_contract_payload_returned'] is False
    assert data['safety']['contract_summary_has_raw_path_key'] is False
    assert _contains_key(summary, RAW_PATH_KEYS) is False
    assert data['approval_token_policy']['token_issued'] is False
    assert data['preview_approval_readiness']['can_execute_preview'] is False
    assert data['export_approval_readiness']['can_execute_export'] is False
    assert data['workbook_read'] is False
    assert data['engine_called'] is False
    assert data['excel_created'] is False
    assert data['legacy_builder_called'] is False


def test_alpha28_export_policy_readiness_requires_successful_preview_first():
    client = _client()
    data = client.post('/api/builder/preview-execution-policy', json={
        'conversation_id': 'smoke_alpha28_export',
        'client_event_id': 'a28_export',
        'requested_action': 'export',
    }).json()
    assert data['route'] == 'builder_preview_execution_policy'
    assert data['requested_action'] == 'export'
    assert data['blocked'] is True
    assert data['contract'] is None
    assert data['export_approval_readiness']['can_execute_export'] is False
    assert data['export_approval_readiness']['requires_successful_preview'] is True
    assert 'preview_approval_required_before_export' in data['blocked_by_policy']
    assert 'preview_approval_required_before_export' in data['export_approval_readiness']['blocked_by_policy']
    assert any(item['code'] == 'preview_approval_required_before_export' for item in data['blocked_reason_details'])
    assert data['workbook_read'] is False
    assert data['engine_called'] is False
    assert data['excel_created'] is False
    assert data['legacy_builder_called'] is False
