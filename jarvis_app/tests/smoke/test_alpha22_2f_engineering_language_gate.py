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


def test_alpha22_2f_version_scope_metadata():
    c = client()
    version = c.get('/api/version').json()
    assert version['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert version['scope'] == 'workbook_read_policy_review_no_content_read'
    assert version['scope_metadata']['engineering_language_gate'] is True
    assert version['scope_metadata']['no_engine'] is True
    assert version['engines_connected']['builder'] is False
    assert version['execution_locks']['workbook_read_enabled'] is False
    assert version['execution_locks']['excel_output_enabled'] is False


def test_active_engineering_explanations_do_not_enter_reducer():
    c = client()
    cid = 'a222f_active_engineering_help'
    start_builder(c, cid)
    samples = [
        'Hi Jarvis, explain what MPa means.',
        'What is kPa?',
        'Explain concrete compressive strength.',
        'Explain CostX functions generally.',
        'How should a senior QS review quantities?',
        'Use unit psi for engineering QA.',
    ]
    for idx, text in enumerate(samples):
        data = post(c, cid, f'a222f_active_eng_{idx}', text)
        assert data['route'] == 'active_task_non_mutating_language'
        assert data['router_step'] == 'active_task_non_mutating_language_gate'
        assert data['confidence_engine']['control_taken'] is False
        assert data['fallback_used'] is False
        assert 'reducer_result' not in data


def test_no_active_engineering_help_and_choose_tool_are_owned_by_gate():
    c = client()
    help_case = post(c, 'a222f_no_active_eng_help', 'a222f_help', 'Explain concrete compressive strength in MPa and psi.')
    assert help_case['route'] == 'general_stub'
    assert help_case['router_step'] == 'no_active_task_language_gate'
    assert help_case['fallback_used'] is False
    assert help_case['confidence_engine']['control_taken'] is True

    choose_case = post(c, 'a222f_no_active_eng_tool', 'a222f_tool', 'Audit pressure units.')
    assert choose_case['route'] == 'choose_tool'
    assert choose_case['router_step'] == 'no_active_task_language_gate'
    assert choose_case['fallback_used'] is False
    assert choose_case['requires_clarification'] is True
    assert choose_case['confidence_engine']['control_taken'] is True


def test_builder_slot_edits_still_reach_slot_reducer_and_unit_evidence_is_visible():
    c = client()
    cid = 'a222f_slot_edits'
    start_builder(c, cid)
    setup = post(c, cid, 'a222f_setup', 'Use Wall Types XGETWALLAREA unit sq. m. Zone 1: Old and New. Use Head 2 for Zone 1. Levels GF to L3.')
    assert setup['route'] == 'active_task_slot_edit'
    assert setup['router_step'] == 'slot_reducer'
    assert setup['confidence_engine']['control_taken'] is False
    rr = setup['reducer_result']
    assert set(['trade_profile', 'costx_function', 'unit', 'dynamic_zones', 'heading_assignments', 'levels']).issubset(set(rr['changed_slots']))
    assert rr['normalization']['canonical_unit'] == 'm2'
    assert rr['normalization']['unit_normalized'] is True


def test_unsupported_engineering_unit_does_not_mutate_builder_unit_when_explanation_context():
    c = client()
    cid = 'a222f_eng_unit_non_mutating'
    start_builder(c, cid)
    data = post(c, cid, 'a222f_eng_unit', 'Use unit psi for engineering QA.')
    assert data['route'] == 'active_task_non_mutating_language'
    plan = c.get('/api/plan/' + cid).json()
    assert plan['plan_summary'].get('unit') in (None, '')
