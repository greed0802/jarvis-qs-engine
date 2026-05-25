from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.qa_runner.test_pack_loader import load_test_pack


def client():
    return TestClient(app)


def test_alpha26_1_version_and_latest_route_dispatch():
    c = client()
    version = c.get('/api/version').json()
    assert version['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    latest = c.get('/api/builder/engine-contract/latest/no_such_conversation_alpha26_1').json()
    assert latest['route'] == 'builder_engine_contract_latest_not_found'
    assert latest['workbook_read'] is False
    assert latest['engine_called'] is False
    assert latest['excel_created'] is False
    assert latest['legacy_builder_called'] is False


def test_alpha26_1_debug_clarification_response_has_safety():
    data = client().post('/api/debug/create-test-clarification', json={
        'conversation_id': 'missing_alpha26_1',
        'client_event_id': 'missing_alpha26_1_evt',
        'prompt': 'Choose A or B.',
    }).json()
    assert data['route'] == 'debug_create_test_clarification'
    assert data['blocked'] is True
    assert data['safety']['workbook_read'] is False
    assert data['safety']['engine_called'] is False
    assert data['safety']['excel_created'] is False
    assert data['safety']['legacy_builder_called'] is False


def test_alpha26_1_pack_schema_accepts_format_discriminator():
    pack = load_test_pack('alpha11_contract_negative_guards.json')
    assert pack.version_target == APP_VERSION
    assert pack.pack_format == 'multi_step'
