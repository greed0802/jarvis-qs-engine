from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client():
    return TestClient(app)


def post(c, cid, eid, text):
    return c.post('/api/chat', json={"conversation_id": cid, "client_event_id": eid, "text": text}).json()


def start_builder(c, cid):
    data = post(c, cid, f'{cid}_start', 'Build me a BOQ')
    assert data['route'] == 'new_builder_task_shell'
    return data


def test_alpha22_2e_version_scope_and_plan_active_task_wrapper():
    c = client()
    version = c.get('/api/version').json()
    assert version['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert version['scope'] == 'workbook_read_policy_review_no_content_read'
    assert version['engines_connected']['builder'] is False
    assert version['execution_locks']['workbook_read_enabled'] is False
    assert version['execution_locks']['excel_output_enabled'] is False

    cid = 'a222e_plan_wrapper'
    start = start_builder(c, cid)
    plan = c.get('/api/plan/' + cid).json()
    assert plan['found'] is True
    assert plan['active_task_id'] == start['active_task_id']
    assert plan['tool'] == 'builder'
    assert plan['active_task']['found'] is True
    assert plan['active_task']['task_id'] == start['active_task_id']
    assert plan['active_task']['tool'] == 'builder'


def test_active_task_non_mutating_language_gate_does_not_enter_slot_reducer():
    c = client()
    cid = 'a222e_active_language'
    start = start_builder(c, cid)
    samples = [
        'Hi Jarvis',
        'Thanks',
        'Format this sentence',
        'Clean this reply wording',
        'What is CostX?',
        'Explain CostX functions generally',
        'How should a senior QS review quantities?',
        'Make my bug report clearer',
    ]
    for idx, text in enumerate(samples):
        data = post(c, cid, f'a222e_active_lang_{idx}', text)
        assert data['active_task_id'] == start['active_task_id']
        assert data['route'] == 'active_task_non_mutating_language'
        assert data['router_step'] == 'active_task_non_mutating_language_gate'
        assert data['confidence_engine']['control_taken'] is False
        assert data.get('reducer_result') is None or (data.get('reducer_result') or {}).get('plan_mutated') is False


def test_active_setup_edits_stay_owned_by_slot_reducer_after_gate_cleanup():
    c = client()
    cid = 'a222e_active_edits'
    start_builder(c, cid)
    samples = [
        ('trade', 'Use Wall Types', ['trade_profile']),
        ('unit', 'Unit m2', ['unit']),
        ('multislot', 'Use Wall Types XGETWALLAREA unit m2. Zone 1: Old and New. Use Head 2 for Zone 1. Levels GF to L3.', ['trade_profile', 'costx_function', 'unit', 'dynamic_zones', 'heading_assignments', 'levels']),
    ]
    for suffix, text, expected_slots in samples:
        data = post(c, cid, f'a222e_edit_{suffix}', text)
        assert data['route'] == 'active_task_slot_edit'
        assert data['router_step'] == 'slot_reducer'
        assert data['confidence_engine']['control_taken'] is False
        changed = set((data.get('reducer_result') or {}).get('changed_slots') or [])
        assert set(expected_slots).issubset(changed)


def test_active_feedback_still_routes_to_feedback_but_writing_report_does_not():
    c = client()
    cid = 'a222e_feedback'
    start_builder(c, cid)
    writing = post(c, cid, 'a222e_feedback_writing', 'Rewrite this issue report')
    assert writing['route'] == 'active_task_non_mutating_language'
    assert writing['router_step'] == 'active_task_non_mutating_language_gate'
    assert writing['confidence_engine']['control_taken'] is False

    issue = post(c, cid, 'a222e_feedback_issue', 'Preview is broken')
    assert issue['route'] == 'feedback_read_only'
    assert issue['router_step'] == 'feedback_router'
    assert issue['confidence_engine']['control_taken'] is False


def test_unit_aliases_sqm_variants_and_squared_symbol_are_centralized():
    c = client()
    units = ['sqm', 'sq m', 'sq.m', 'sq. m', 'square metres', 'm²']
    for idx, unit in enumerate(units):
        cid = f'a222e_unit_alias_{idx}'
        start_builder(c, cid)
        data = post(c, cid, f'a222e_unit_alias_edit_{idx}', f'Use Wall Types XGETWALLAREA unit {unit}')
        assert data['route'] == 'active_task_slot_edit'
        assert data['router_step'] == 'slot_reducer'
        rr = data['reducer_result']
        assert rr['plan_mutated'] is True
        plan = c.get('/api/plan/' + cid).json()
        assert plan['plan_summary']['unit'] == 'm2'
        assert not (rr.get('conflicts') or [])
