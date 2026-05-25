from fastapi.testclient import TestClient
from jarvis_v5.app import app


def client():
    return TestClient(app)


def post(c, conversation_id, event_id, text):
    return c.post('/api/chat', json={
        'conversation_id': conversation_id,
        'client_event_id': event_id,
        'text': text,
    }).json()


def create_task(c, conversation_id):
    data = post(c, conversation_id, f'{conversation_id}_new', 'Build me a BOQ')
    assert data['route'] == 'new_builder_task_shell'
    return data


def test_trade_conflict_blocks_without_mutation():
    c = client()
    create_task(c, 'alpha9_conflict_trade')
    data = post(c, 'alpha9_conflict_trade', 'a9_trade_002', 'Use Wall Types and Structural Steel')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    rr = data['reducer_result']
    assert rr['conflict_type'] == 'trade_conflict'
    assert rr['plan_mutated'] is False
    assert data['pending_clarification_id']
    plan = c.get('/api/plan/alpha9_conflict_trade').json()
    assert plan['plan_summary']['trade_profile'] is None


def test_function_unit_conflict_blocks_count_m2():
    c = client()
    create_task(c, 'alpha9_count_conflict')
    data = post(c, 'alpha9_count_conflict', 'a9_count_002', 'Use Count unit m2')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    rr = data['reducer_result']
    assert rr['conflict_type'] == 'function_unit_conflict'
    assert 'costx_function' in rr['conflicting_slots']
    assert rr['plan_mutated'] is False
    plan = c.get('/api/plan/alpha9_count_conflict').json()
    assert plan['plan_summary']['costx_function'] is None


def test_safe_count_no_still_applies():
    c = client()
    create_task(c, 'alpha9_count_safe')
    data = post(c, 'alpha9_count_safe', 'a9_count_003', 'Use Count unit no')
    assert data['route'] == 'active_task_slot_edit'
    rr = data['reducer_result']
    assert rr['changes']['costx_function'] == 'XGETCOUNT'
    assert rr['changes']['unit'] == 'no'
    assert rr['plan_mutated'] is True


def test_heading_ambiguity_blocks_when_multiple_zones_exist():
    c = client()
    create_task(c, 'alpha9_head')
    data = post(c, 'alpha9_head', 'a9_head_002', 'Zone 1: Old and New; Zone 2: External and Internal')
    assert data['route'] == 'active_task_slot_edit'
    data = post(c, 'alpha9_head', 'a9_head_003', 'Use Head 2')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    assert data['reducer_result']['conflict_type'] == 'heading_ambiguity'


def test_valid_heading_after_ambiguity_option_resolves():
    c = client()
    create_task(c, 'alpha9_head_resolve')
    post(c, 'alpha9_head_resolve', 'a9_head_resolve_002', 'Zone 1: Old and New; Zone 2: External and Internal')
    data = post(c, 'alpha9_head_resolve', 'a9_head_resolve_003', 'Use Head 2')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    data = post(c, 'alpha9_head_resolve', 'a9_head_resolve_004', 'Use Head2 for Zone 1')
    assert data['route'] == 'clarification_resolved'
    plan = c.get('/api/plan/alpha9_head_resolve').json()
    assert plan['plan_summary']['heading_assignments']['1'] == 'Head2'


def test_basement_range_asks_for_direction():
    c = client()
    create_task(c, 'alpha9_basement')
    data = post(c, 'alpha9_basement', 'a9_basement_002', 'Levels B2 to B5')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    assert data['reducer_result']['conflict_type'] == 'ambiguous_basement_range'
    assert data['pending_clarification_id']


def test_alpha8_complete_flow_remains_ready_for_future_engine(tmp_path):
    c = client()
    cid = 'alpha9_full_safe'
    create_task(c, cid)
    # Use attachment endpoint with a tiny valid upload metadata path; alpha does not read workbook content.
    files = {'file': ('Test.xlsx', b'not-a-real-workbook-but-not-read', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
    data = c.post('/api/attach', data={'conversation_id': cid, 'client_event_id': 'a9_attach_001', 'text': 'Here'}, files=files).json()
    assert data['route'] == 'attachment_bind'
    for idx, text in enumerate([
        'Use Wall Types', 'Use XGETWALLAREA', 'Unit m2', 'Zone 1: Old and New', 'Use Head 2 for Zone 1', 'Levels GF to L3'
    ], start=2):
        assert post(c, cid, f'a9_full_{idx}', text)['route'] == 'active_task_slot_edit'
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': cid, 'client_event_id': 'a9_snap_001', 'approve': True}).json()
    assert snap['setup_completeness']['ready_for_future_engine'] is True
    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': cid, 'client_event_id': 'a9_adapter_001'}).json()
    assert adapter['route'] == 'builder_adapter_dry_run'
    assert adapter['workbook_read'] is False
    assert adapter['engine_called'] is False
    assert adapter['excel_created'] is False
    assert adapter['adapter']['valid_for_future_engine'] is True
    assert adapter['adapter']['normalization']['status'] == 'clean'
