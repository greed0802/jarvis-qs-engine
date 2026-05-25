from __future__ import annotations

import re
from pathlib import Path
from tempfile import TemporaryDirectory

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.core.conversation_id_safety import is_safe_conversation_id, sanitize_conversation_id, safe_conversation_storage_stem
from jarvis_v5.core.conversation_store import ConversationStore
from jarvis_v5.core.event_ledger import EventLedger


UNSAFE_CHARS = ('..', '/', '\\', ':', '"', '<', '>', '|', '?', '*', ';', ' ')


def _client() -> TestClient:
    return TestClient(app)


def _policy(conversation_id: str | None) -> dict:
    response = _client().post(
        '/api/builder/workbook-read-policy-review',
        json={'conversation_id': conversation_id, 'client_event_id': f'policy_{abs(hash(str(conversation_id))) % 100000}'},
    )
    assert response.status_code == 200
    return response.json()


def _assert_safe_public_id(conversation_id: str) -> None:
    assert conversation_id
    assert is_safe_conversation_id(conversation_id)
    assert conversation_id.startswith(('cid_', 'chat_')) or re.fullmatch(r'[A-Za-z0-9_-]{1,80}', conversation_id)
    for marker in UNSAFE_CHARS:
        assert marker not in conversation_id


def test_alpha35_3_version_policy_locks() -> None:
    data = _client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_alpha35_3_safe_id_preserved() -> None:
    assert sanitize_conversation_id('alpha35_3_safe_id') == 'alpha35_3_safe_id'
    data = _policy('alpha35_3_safe_id')
    assert data['conversation_id'] == 'alpha35_3_safe_id'
    assert data['route'] == 'builder_workbook_read_policy_review'
    assert data['policy_only'] is True


def test_alpha35_3_placeholder_generates_chat_id() -> None:
    data = _policy('string')
    assert data['conversation_id'].startswith('chat_')
    _assert_safe_public_id(data['conversation_id'])


def test_alpha35_3_unsafe_ids_map_to_cid_and_policy_stays_safe() -> None:
    unsafe_ids = [
        '../escape',
        'safe/../evil',
        r'safe\\..\\evil',
        'conv:evil',
        'quote"id',
        'CON',
        'CON_p4_t7',
        'nul',
        'nul_p4_t8',
        'emoji_🔒_policy',
        'semi;colon',
        'space id',
        'id with ../../cells',
        '/absolute/path',
    ]
    for raw_id in unsafe_ids:
        expected = sanitize_conversation_id(raw_id)
        assert expected is not None
        assert expected.startswith('cid_')
        data = _policy(raw_id)
        assert data['conversation_id'] == expected
        _assert_safe_public_id(data['conversation_id'])
        assert data['conversation_id'] != raw_id
        assert data['route'] == 'builder_workbook_read_policy_review'
        assert data['policy_only'] is True
        assert data['cell_read_enabled'] is False
        assert data['formula_read_enabled'] is False
        assert data['dimension_read_enabled'] is False
        assert data['workbook_parse_enabled'] is False
        assert data['workbook_opened'] is False
        assert data['workbook_read'] is False
        assert data['workbook_content_read'] is False
        assert data['cells_read'] is False
        assert data['formulas_read'] is False
        assert data['engine_called'] is False
        assert data['excel_created'] is False
        assert data['legacy_builder_called'] is False
        assert data['safety']['workbook_read'] is False
        assert data['safety']['engine_called'] is False
        assert data['safety']['excel_created'] is False
        assert data['safety']['legacy_builder_called'] is False


def test_alpha35_3_event_ledger_non_list_payload_does_not_crash() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp)
        ledger = EventLedger(root=root)
        cid = 'alpha35_3_event_safety'
        path = ledger._path(cid)
        path.write_text('{"not": "an event list"}', encoding='utf-8')
        event = ledger.append(
            cid,
            client_event_id='event_001',
            intent='DEBUG',
            route='builder_workbook_read_policy_review',
            request={'conversation_id': cid},
            response={'route': 'builder_workbook_read_policy_review'},
        )
        assert event['conversation_id'] == cid
        assert isinstance(ledger.list_events(cid), list)
        assert len(ledger.list_events(cid)) == 1


def test_alpha35_3_storage_paths_never_escape_root() -> None:
    with TemporaryDirectory() as tmp:
        root = Path(tmp).resolve()
        store = ConversationStore(root=root)
        ledger = EventLedger(root=root / 'events')
        for raw_id in ['../escape', 'safe/../evil', 'conv:evil', 'quote"id', 'emoji_🔒_policy']:
            safe = sanitize_conversation_id(raw_id)
            assert safe is not None
            store_path = store._path(raw_id).resolve()
            event_path = ledger._path(raw_id).resolve()
            assert root in store_path.parents
            assert (root / 'events').resolve() in event_path.parents
            assert store_path.name == f'{safe_conversation_storage_stem(raw_id)}.json'
            assert event_path.name == f'{safe_conversation_storage_stem(raw_id)}.json'
