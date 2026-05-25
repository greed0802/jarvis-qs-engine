from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def test_alpha24_2_version_and_route_context_trace():
    client = TestClient(app)
    version = client.get('/api/version').json()
    assert version['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'

    start = client.post('/api/chat', json={
        'conversation_id': 'alpha24_2_route_context_probe',
        'client_event_id': 'a242_ctx_001',
        'text': 'Build me a BOQ',
        'mode': 'ask_first',
    }).json()
    assert start['route'] == 'new_builder_task_shell'
    assert start['route_context'] is not None
    assert start['route_context']['classification_owner'] == 'main_router_route_context'
    assert start['route_context']['classification_reused'] is True

    review = client.post('/api/chat', json={
        'conversation_id': 'alpha24_2_route_context_probe',
        'client_event_id': 'a242_ctx_002',
        'text': 'Please review the current setup',
        'mode': 'ask_first',
    }).json()
    assert review['route'] == 'active_task_review'
    assert review['route_context'] is not None
    assert review['route_context']['has_active_task'] is True
    assert 'alpha.17' not in review['message']


def test_alpha24_2_registry_endpoints_keep_metadata_only_route_shape():
    client = TestClient(app)
    for endpoint, route in [
        ('/api/registry/tools', 'registry_tools'),
        ('/api/registry/capabilities', 'registry_capabilities'),
        ('/api/registry/connectors', 'registry_connectors'),
        ('/api/registry/models', 'registry_models'),
    ]:
        data = client.get(endpoint).json()
        assert data['route'] == route
        assert data['metadata_only'] is True
        assert data['execution_enabled'] is False
