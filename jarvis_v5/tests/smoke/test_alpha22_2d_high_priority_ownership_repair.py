from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION, PACKAGE_ROOT


def client():
    return TestClient(app)


def post(c, cid, eid, text, attachments=None):
    payload = {"conversation_id": cid, "client_event_id": eid, "text": text}
    if attachments is not None:
        payload["attachments"] = attachments
    return c.post('/api/chat', json=payload).json()


def attach_fixture(c, cid, eid='attach'):
    with open(PACKAGE_ROOT / 'tests' / 'fixtures' / 'Test.xlsx', 'rb') as fh:
        return c.post(
            '/api/attach',
            data={'conversation_id': cid, 'client_event_id': f'{cid}_{eid}', 'text': 'Here'},
            files={'file': ('Test.xlsx', fh, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        ).json()


def start_builder(c, cid):
    return post(c, cid, f'{cid}_start', 'Build me a BOQ')


def test_alpha22_2d_version_locks():
    data = client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_no_active_feedback_wording_stays_in_language_gate_but_active_feedback_still_logs():
    c = client()
    no_task = post(c, 'a222d_feedback_no_task', 'a222d_fb_write', 'Make my bug report clearer')
    assert no_task['route'] == 'general_stub'
    assert no_task['router_step'] == 'no_active_task_language_gate'
    assert no_task['fallback_used'] is False
    assert no_task['confidence_engine']['control_taken'] is True
    assert no_task['confidence_engine']['negative_guard'] == 'format_text_not_workbook'

    start_builder(c, 'a222d_feedback_active')
    active = post(c, 'a222d_feedback_active', 'a222d_fb_active', 'Preview is broken')
    assert active['route'] == 'feedback_read_only'
    assert active['router_step'] == 'feedback_router'
    assert active['confidence_engine']['control_taken'] is False


def test_expanded_no_active_gate_soft_builder_choose_tool_and_qs_help():
    c = client()
    cases = [
        ('soft', 'Create the measurement workbook structure', 'new_builder_task_shell', 'no_active_task_language_gate'),
        ('tool', 'Classify this task first', 'choose_tool', 'no_active_task_language_gate'),
        ('qshelp', 'How should a senior QS review quantities?', 'general_stub', 'no_active_task_language_gate'),
    ]
    for suffix, text, route, step in cases:
        data = post(c, f'a222d_gate_{suffix}', f'a222d_gate_{suffix}', text)
        assert data['route'] == route
        assert data['router_step'] == step
        assert data['fallback_used'] is False
        assert data['confidence_engine']['control_taken'] is True


def test_conflict_guard_exposes_conflicts_and_normalization_evidence():
    c = client()
    for idx, text in enumerate(['Use Count with m2', 'Use Count, the unit should be m2', 'Use XGETWALLAREA unit no']):
        cid = f'a222d_conflict_{idx}'
        start_builder(c, cid)
        data = post(c, cid, f'a222d_conflict_{idx}_edit', text)
        rr = data['reducer_result']
        assert data['route'] == 'active_task_slot_edit_needs_clarification'
        assert data['router_step'] == 'slot_reducer'
        assert data['confidence_engine']['control_taken'] is False
        assert rr['plan_mutated'] is False
        assert rr['conflicts']
        assert rr['conflicts'][0]['conflict_type'] == 'function_unit_conflict'
        assert rr['normalization']
        assert 'raw_text' in rr['normalization']
        assert 'canonical_text' in rr['normalization']


def test_multiclause_setup_normalization_collects_multiple_slots_and_reaches_contract():
    c = client()
    cid = 'a222d_multislot_full_flow'
    start = start_builder(c, cid)
    assert start['route'] == 'new_builder_task_shell'
    attach = attach_fixture(c, cid)
    assert attach['route'] == 'attachment_bind'
    edit = post(
        c,
        cid,
        'a222d_multislot_edit',
        'Use Wall Types XGETWALLAREA unit m2. Zone 1: Old and New. Use Head 2 for Zone 1. Levels GF to L3.',
    )
    rr = edit['reducer_result']
    assert edit['route'] == 'active_task_slot_edit'
    assert edit['router_step'] == 'slot_reducer'
    assert edit['confidence_engine']['control_taken'] is False
    assert rr['plan_mutated'] is True
    assert set(['trade_profile', 'costx_function', 'unit', 'dynamic_zones', 'heading_assignments', 'levels']).issubset(set(rr['changed_slots']))
    assert rr['normalization']['raw_text']
    assert rr['normalization']['canonical_text']

    snap = c.post('/api/builder/create-snapshot', json={'conversation_id': cid, 'client_event_id': 'a222d_snap'}).json()
    assert snap['route'] == 'builder_snapshot_created'
    assert snap['blocked'] is False
    adapter = c.post('/api/builder/adapter-dry-run', json={'conversation_id': cid, 'client_event_id': 'a222d_adapter'}).json()
    assert adapter['route'] == 'builder_adapter_dry_run'
    assert adapter['blocked'] is False
    contract = c.post('/api/builder/engine-contract', json={'conversation_id': cid, 'client_event_id': 'a222d_contract'}).json()
    assert contract['route'] == 'builder_engine_contract_created'
    assert contract['blocked'] is False
    assert contract['workbook_read'] is False
    assert contract['engine_called'] is False
    assert contract['excel_created'] is False
    assert contract['legacy_builder_called'] is False
