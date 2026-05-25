from __future__ import annotations

from io import BytesIO
from uuid import uuid4
from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.reducers.slot_reducer import apply_slot_edit


def client() -> TestClient:
    return TestClient(app)


def post_chat(c: TestClient, conversation_id: str, event_id: str, text: str) -> dict:
    return c.post('/api/chat', json={'conversation_id': conversation_id, 'client_event_id': event_id, 'text': text}).json()


def attach_workbook(c: TestClient, conversation_id: str, event_id: str, filename: str = 'Steel_test.xlsx') -> dict:
    return c.post(
        '/api/attach',
        data={'conversation_id': conversation_id, 'client_event_id': event_id, 'text': 'Here'},
        files={'file': (filename, BytesIO(b'fake workbook bytes - not read'), 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
    ).json()


def create_snapshot(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post('/api/builder/create-snapshot', json={'conversation_id': conversation_id, 'client_event_id': event_id, 'approve': True}).json()


def adapter_dry_run(c: TestClient, conversation_id: str, event_id: str) -> dict:
    return c.post('/api/builder/adapter-dry-run', json={'conversation_id': conversation_id, 'client_event_id': event_id}).json()


def test_reducer_parses_complete_wall_types_shell_setup():
    plan = {}
    for text in [
        'Use Wall Types',
        'Use XGETWALLAREA',
        'Unit m2',
        'Zone 1: Old and New',
        'Use Head 2 for Zone 1',
        'Levels GF to L3',
    ]:
        plan, result = apply_slot_edit(plan, text)
        assert result.handled is True

    assert plan['trade_profile'] == 'Wall Types'
    assert plan['costx_function'] == 'XGETWALLAREA'
    assert plan['unit'] == 'm2'
    assert plan['dynamic_zones'][0]['values'] == ['Old', 'New']
    assert plan['heading_assignments']['1'] == 'Head2'
    assert plan['dynamic_zones'][0]['head_assignment'] == 'Head2'
    assert plan['levels'] == ['GF', 'L1', 'L2', 'L3']


def test_reducer_parses_doors_windows_and_structural_steel_slots():
    plan = {}
    for text in ['Use Doors and Windows', 'Use Count', 'Unit no']:
        plan, result = apply_slot_edit(plan, text)
        assert result.handled is True
    assert plan['trade_profile'] == 'Doors / Windows'
    assert plan['costx_function'] == 'XGETCOUNT'
    assert plan['unit'] == 'no'

    steel = {}
    for text in ['Use Structural Steel', 'Use Steel Surface Area', 'Unit m2']:
        steel, result = apply_slot_edit(steel, text)
        assert result.handled is True
    assert steel['trade_profile'] == 'Structural Steel'
    assert steel['costx_function'] == 'XGETCUSTOM'
    assert steel['custom_quantity'] == 'Steel Surface Area'
    assert steel['unit'] == 'm2'


def test_reducer_parses_headings_levels_and_aliases():
    plan = {}
    for text in [
        'Zone 1: Old and New',
        'Zone 2: External and Internal',
        'Use Head 2 for Zone 1 and Head 3 for Zone 2',
        'Levels GF to L5 with Mezzanine on L1, L2, and L5',
        'Use Mezz as code for Mezzanine',
    ]:
        plan, result = apply_slot_edit(plan, text)
        assert result.handled is True

    assert plan['heading_assignments'] == {'1': 'Head2', '2': 'Head3'}
    assert plan['dynamic_zones'][0]['head_assignment'] == 'Head2'
    assert plan['dynamic_zones'][1]['head_assignment'] == 'Head3'
    assert 'L1 Mezzanine' in plan['levels']
    assert 'L2 Mezzanine' in plan['levels']
    assert 'L5 Mezzanine' in plan['levels']
    assert plan['aliases']['Mezzanine'] == 'Mezz'


def test_api_complete_shell_setup_reaches_plan_snapshot_adapter_and_stays_safe():
    c = client()
    conv = f'alpha8_complete_{uuid4().hex}'
    post_chat(c, conv, 'a8_evt_001', 'Build me a BOQ')
    attach_workbook(c, conv, 'a8_attach_001')
    for idx, text in enumerate([
        'Use Wall Types',
        'Use XGETWALLAREA',
        'Unit m2',
        'Zone 1: Old and New',
        'Use Head 2 for Zone 1',
        'Levels GF to L3',
    ], start=2):
        response = post_chat(c, conv, f'a8_evt_{idx:03d}', text)
        assert response['route'] == 'active_task_slot_edit'

    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['plan_summary']['trade_profile'] == 'Wall Types'
    assert plan['plan_summary']['costx_function'] == 'XGETWALLAREA'
    assert plan['plan_summary']['unit'] == 'm2'
    assert plan['setup_completeness']['missing_required'] == []
    assert plan['setup_completeness']['ready_for_future_engine'] is True

    snap = create_snapshot(c, conv, 'a8_snap_001')
    assert snap['snapshot_status'] == 'current'
    assert snap['snapshot']['trade_profile'] == 'Wall Types'
    assert snap['snapshot']['costx_function'] == 'XGETWALLAREA'
    assert snap['snapshot']['unit'] == 'm2'
    assert snap['setup_completeness']['ready_for_future_engine'] is True

    dry = adapter_dry_run(c, conv, 'a8_adapter_001')
    assert dry['route'] == 'builder_adapter_dry_run'
    assert dry['blocked'] is False
    assert dry['workbook_read'] is False
    assert dry['engine_called'] is False
    assert dry['excel_created'] is False
    assert dry['adapter_input']['trade_profile'] == 'Wall Types'
    assert dry['adapter_input']['costx_function'] == 'XGETWALLAREA'
    assert dry['adapter_input']['unit'] == 'm2'
    assert dry['setup_completeness']['ready_for_future_engine'] is True

    preview = post_chat(c, conv, 'a8_preview_001', 'Preview')
    assert preview['route'] == 'active_task_preview_stub'
    assert preview['blocked'] is True
    assert preview['reason'] == 'preview_engine_not_connected'
    assert preview['setup_completeness']['ready_for_future_engine'] is True
    assert 'No Builder engine was called' in preview['message']


def test_stale_logic_still_marks_snapshot_and_adapter_after_slot_change():
    c = client()
    conv = f'alpha8_stale_{uuid4().hex}'
    post_chat(c, conv, 'a8s_evt_001', 'Build me a BOQ')
    attach_workbook(c, conv, 'a8s_attach_001')
    for idx, text in enumerate(['Use Wall Types', 'Use XGETWALLAREA', 'Unit m2', 'Zone 1: Old and New', 'Use Head 2 for Zone 1', 'Levels GF to L3'], start=2):
        post_chat(c, conv, f'a8s_evt_{idx:03d}', text)
    create_snapshot(c, conv, 'a8s_snap_001')
    adapter_dry_run(c, conv, 'a8s_adapter_001')
    post_chat(c, conv, 'a8s_change_001', 'Add Same to Zone 1')

    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['plan_summary']['zones'][0]['values'] == ['Old', 'New', 'Same']
    assert plan['snapshot']['status'] == 'stale'
    assert plan['adapter_dry_run']['freshness'] == 'stale'
    assert 'snapshot_current' in plan['setup_completeness']['missing_required']
    assert 'adapter_current' in plan['setup_completeness']['missing_required']
