from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION
from jarvis_v5.schemas.builder_snapshot_schema import validate_snapshot_from_plan
from jarvis_v5.tools.builder.setup_completeness import setup_completeness_from_parts


def client():
    return TestClient(app)


def post(c, conversation_id, event_id, text):
    return c.post('/api/chat', json={
        'conversation_id': conversation_id,
        'client_event_id': event_id,
        'text': text,
    }).json()


def start(c, conversation_id):
    data = post(c, conversation_id, f'{conversation_id}_start', 'Build me a BOQ')
    assert data['route'] == 'new_builder_task_shell'
    return data


def attach(c, conversation_id):
    with open('jarvis_v5/tests/fixtures/Test.xlsx', 'rb') as f:
        data = c.post(
            '/api/attach',
            data={'conversation_id': conversation_id, 'client_event_id': f'{conversation_id}_attach', 'text': 'Here'},
            files={'file': ('Test.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        ).json()
    assert data['route'] == 'attachment_bind'
    assert data['reducer_result']['workbook_read'] is False
    return data


def complete_common(c, conversation_id, function_text='Use XGETWALLAREA', unit_text='Unit m2'):
    start(c, conversation_id)
    attach(c, conversation_id)
    for suffix, text in [
        ('trade', 'Use Wall Types'),
        ('function', function_text),
        ('unit', unit_text),
        ('zone', 'Zone 1: Old and New'),
        ('head', 'Use Head 2 for Zone 1'),
        ('levels', 'Levels GF to L3'),
    ]:
        data = post(c, conversation_id, f'{conversation_id}_{suffix}', text)
        assert data['route'] == 'active_task_slot_edit'
    return c.get(f'/api/plan/{conversation_id}').json()


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


def test_alpha21_version():
    assert client().get('/api/version').json()['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'


def test_cross_message_xgetcount_m2_blocks_without_plan_mutation():
    c = client()
    cid = 'alpha21_count_m2_cross_message'
    start(c, cid)
    assert post(c, cid, 'a21_count_trade', 'Use Wall Types')['route'] == 'active_task_slot_edit'
    assert post(c, cid, 'a21_count_func', 'Use XGETCOUNT')['route'] == 'active_task_slot_edit'
    data = post(c, cid, 'a21_count_unit_m2', 'Unit m2')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    assert data['pending_clarification_id']
    rr = data['reducer_result']
    assert rr['conflict_type'] == 'function_unit_conflict'
    assert rr['plan_mutated'] is False
    plan = c.get(f'/api/plan/{cid}').json()
    assert plan['plan_summary']['costx_function'] == 'XGETCOUNT'
    assert plan['plan_summary']['unit'] is None


def test_valid_xgetcount_no_and_nr_still_apply():
    c = client()
    cid_no = 'alpha21_count_no_valid'
    plan_no = complete_common(c, cid_no, function_text='Use XGETCOUNT', unit_text='Unit no')
    assert plan_no['plan_summary']['costx_function'] == 'XGETCOUNT'
    assert plan_no['plan_summary']['unit'] == 'no'
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': cid_no, 'client_event_id': 'a21_count_no_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    assert snap['setup_completeness']['ready_for_future_engine'] is True
    assert_safety(snap)

    cid_nr = 'alpha21_count_nr_valid'
    plan_nr = complete_common(c, cid_nr, function_text='Use XGETCOUNT', unit_text='Unit nr')
    assert plan_nr['plan_summary']['costx_function'] == 'XGETCOUNT'
    assert plan_nr['plan_summary']['unit'] == 'nr'


def test_xgetwallarea_m2_passes_and_no_blocks():
    c = client()
    cid = 'alpha21_wallarea_m2_valid'
    complete_common(c, cid)
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': cid, 'client_event_id': 'a21_wallarea_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    assert snap['setup_completeness']['ready_for_future_engine'] is True

    cid_bad = 'alpha21_wallarea_no_invalid'
    start(c, cid_bad)
    post(c, cid_bad, 'a21_wallarea_bad_trade', 'Use Wall Types')
    post(c, cid_bad, 'a21_wallarea_bad_function', 'Use XGETWALLAREA')
    data = post(c, cid_bad, 'a21_wallarea_bad_unit', 'Unit no')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    assert data['reducer_result']['conflict_type'] == 'function_unit_conflict'


def test_setup_and_snapshot_validation_block_dirty_invalid_pair():
    plan = {
        'trade_profile': 'Wall Types',
        'costx_function': 'XGETCOUNT',
        'unit': 'm2',
        'zone_mode': 'rebuild',
        'dynamic_zones': [{'zone_id': 1, 'values': ['Old', 'New'], 'head_assignment': 'Head2'}],
        'heading_assignments': {'1': 'Head2'},
        'levels': ['GF', 'L1'],
    }
    setup = setup_completeness_from_parts(
        workbook_ref={'filename': 'Test.xlsx'},
        trade_profile=plan['trade_profile'],
        costx_function=plan['costx_function'],
        unit=plan['unit'],
        zone_mode=plan['zone_mode'],
        dynamic_zones=plan['dynamic_zones'],
        heading_assignments=plan['heading_assignments'],
        levels=plan['levels'],
    )
    assert setup['ready_for_future_engine'] is False
    assert 'function_unit_compatibility' in setup['missing_required']
    validation = validate_snapshot_from_plan(task_status='collecting', workbook_ref={'filename': 'Test.xlsx'}, plan=plan)
    assert validation.valid is False
    assert 'Function/unit compatibility conflict' in validation.issues


def test_reinforcement_custom_weight_t_still_passes_contract():
    c = client()
    cid = 'alpha21_reo_weight_t_valid'
    start(c, cid)
    attach(c, cid)
    data = post(c, cid, f'{cid}_trade', 'Use Reinforcement')
    assert data['route'] == 'active_task_slot_edit_needs_clarification'
    data = post(c, cid, f'{cid}_resolve', 'Use XGETCUSTOM with Reinforcement Weight unit t')
    assert data['route'] == 'clarification_resolved'
    for suffix, text in [
        ('zone', 'Zone 1: Old and New'),
        ('head', 'Use Head 2 for Zone 1'),
        ('levels', 'Levels GF to L3'),
    ]:
        data = post(c, cid, f'{cid}_{suffix}', text)
        assert data['route'] == 'active_task_slot_edit'
    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': cid, 'client_event_id': f'{cid}_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': cid, 'client_event_id': f'{cid}_adapter'}).json()
    assert adapter['route'] == 'builder_adapter_dry_run'
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': cid, 'client_event_id': f'{cid}_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    assert_safety(contract)
