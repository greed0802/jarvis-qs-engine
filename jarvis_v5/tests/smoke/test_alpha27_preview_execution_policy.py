from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def _client():
    return TestClient(app)


def _chat(client, cid: str, event: str, text: str) -> dict:
    return client.post('/api/chat', json={
        'conversation_id': cid,
        'client_event_id': event,
        'text': text,
    }).json()


def test_alpha27_version_and_policy_metadata():
    client = _client()
    version = client.get('/api/version').json()
    assert version['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert version['scope'] == 'workbook_read_policy_review_no_content_read'
    assert version['engines_connected']['preview_execution_policy'] is False
    assert version['scope_metadata']['workbook_access_boundary_policy'] is True
    assert version['scope_metadata']['preview_execution_policy_metadata_only'] is True
    locks = version['execution_locks']
    assert locks['builder_engine_execution_enabled'] is False
    assert locks['legacy_builder_callable'] is False
    assert locks['workbook_read_enabled'] is False
    assert locks['excel_output_enabled'] is False


def test_alpha27_policy_without_contract_is_metadata_only():
    client = _client()
    data = client.post('/api/builder/preview-execution-policy', json={
        'conversation_id': 'smoke_alpha27_no_contract',
        'client_event_id': 'a27_no_contract',
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
    assert data['contract_found'] is False
    assert data['contract_ready'] is False
    assert 'workbook_read_disabled' in data['blocked_by_policy']
    assert 'legacy_builder_callable_disabled' in data['blocked_by_policy']
    assert 'excel_output_disabled' in data['blocked_by_policy']
    assert 'execution_kill_switch' in data['blocked_by_policy']
    assert 'engine_contract_not_ready' in data['blocked_by_policy']
    assert data['preview_result_schema']['schema_version'] == 'builder_preview_result_v1'
    assert data['output_manifest_schema']['schema_version'] == 'builder_output_manifest_v1'
    assert data['background_job_boundary']['job_enqueue_enabled'] is False
    assert 'formula_generation' in data['formula_integrity_guard_connection_point']['blocked_now']


def test_alpha27_policy_with_contract_still_blocks_and_does_not_execute():
    client = _client()
    cid = 'smoke_alpha27_contract'
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

    data = client.post('/api/builder/preview-execution-policy', json={
        'conversation_id': cid,
        'client_event_id': 'a27_policy',
        'requested_action': 'preview',
    }).json()
    assert data['route'] == 'builder_preview_execution_policy'
    assert data['reason'] == 'preview_execution_disabled_by_policy'
    assert data['contract_found'] is True
    assert data['contract_ready'] is True
    assert data['execution_enabled'] is False
    assert data['workbook_read'] is False
    assert data['engine_called'] is False
    assert data['excel_created'] is False
    assert data['legacy_builder_called'] is False
    assert data['safe_workbook_path_resolver']['status'] == 'metadata_only'
    assert data['preview_approval_policy']['preview_execution_enabled'] is False
    assert data['export_approval_policy']['export_execution_enabled'] is False


def test_alpha27_export_policy_requires_preview_first():
    client = _client()
    data = client.post('/api/builder/preview-execution-policy', json={
        'conversation_id': 'smoke_alpha27_export',
        'client_event_id': 'a27_export',
        'requested_action': 'export',
    }).json()
    assert data['route'] == 'builder_preview_execution_policy'
    assert data['requested_action'] == 'export'
    assert data['blocked'] is True
    assert 'preview_approval_required_before_export' in data['blocked_by_policy']
    assert data['workbook_read'] is False
    assert data['engine_called'] is False
    assert data['excel_created'] is False
    assert data['legacy_builder_called'] is False
