from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION


def client():
    return TestClient(app)


def post(c, cid, eid, text):
    return c.post('/api/chat', json={'conversation_id': cid, 'client_event_id': eid, 'text': text}).json()


def test_alpha22_version_locks():
    data = client().get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def assert_builder_start(data, alias=None):
    assert data['route'] == 'new_builder_task_shell'
    assert data['route_confidence'] >= 90
    assert data['fallback_used'] is False
    assert data['tool_candidates'] == ['builder']
    if alias:
        assert data['reducer_result']['qs_alias']['alias'] == alias


def test_qs_aliases_start_builder_shell_without_engine():
    c = client()
    cases = [
        ('alpha22_boq', 'Create a BOQ', 'boq'),
        ('alpha22_bill', 'Prepare a Bill of Quantities', 'bill_of_quantities'),
        ('alpha22_sov', 'Create a Schedule of Values', 'schedule_of_values'),
        ('alpha22_trade_schedule', 'Prepare a Trade Schedule', 'trade_schedule'),
        ('alpha22_tender_boq', 'Create a Tender BOQ', 'boq'),
        ('alpha22_nrm', 'Prepare an NRM-style BOQ', 'boq'),
        ('alpha22_bq_ireland', 'Create a BQ for Ireland project', 'bq'),
        ('alpha22_ph', 'Create a PH Bill of Quantities', 'ph_bill_of_quantities'),
    ]
    for cid, text, alias in cases:
        data = post(c, cid, cid+'_evt', text)
        assert_builder_start(data)
        assert data['active_task_status'] == 'waiting_for_file'
        assert data['readiness']['safety']['workbook_read'] is False
        assert data['readiness']['safety']['engine_called'] is False
        assert data['readiness']['safety']['excel_created'] is False
        assert data['readiness']['safety']['legacy_builder_called'] is False


def test_negative_guards_do_not_start_builder():
    c = client()
    meeting = post(c, 'alpha22_meeting', 'a22_meeting_001', 'Schedule a meeting tomorrow')
    assert meeting['route'] == 'general_stub'
    assert meeting['active_task_id'] is None
    assert meeting['confidence_reason'] == 'negative_guard:casual_non_tool_phrase'
    assert meeting['confidence_engine']['negative_guard_detail'] == 'schedule_meeting'
    assert meeting['fallback_used'] is False

    definition = post(c, 'alpha22_define', 'a22_define_001', 'What is a Schedule of Values?')
    assert definition['route'] == 'general_stub'
    assert definition['active_task_id'] is None
    assert definition['confidence_reason'] == 'negative_guard:casual_non_tool_phrase'
    assert definition['confidence_engine']['negative_guard_detail'] == 'definition_request'
    assert definition['fallback_used'] is False


def test_ambiguous_no_active_task_routes_to_choose_tool_not_fallback():
    c = client()
    data = post(c, 'alpha22_format_no_task', 'a22_format_001', 'Format')
    assert data['route'] == 'choose_tool'
    assert data['requires_clarification'] is True
    assert data['fallback_used'] is False
    assert data['tool_candidates'] == ['formatter']


def test_active_builder_ambiguous_phrases_do_not_fallback_or_mutate():
    c = client()
    cid = 'alpha22_active_ambiguous'
    start = post(c, cid, 'a22_active_001', 'Build me a BOQ')
    task_id = start['active_task_id']
    same = post(c, cid, 'a22_active_002', 'same')
    assert same['route'] == 'active_task_slot_edit_needs_clarification'
    assert same['active_task_id'] == task_id
    assert same['reducer_result']['plan_mutated'] is False
    assert same['requires_clarification'] is True
    assert same['fallback_used'] is False

    fmt = post(c, cid, 'a22_active_003', 'format')
    assert fmt['route'] == 'formatter_handoff_needs_confirmation'
    assert fmt['active_task_id'] == task_id
    assert fmt['reducer_result']['plan_mutated'] is False
    assert fmt['tool_candidates'] == ['formatter']
    assert fmt['fallback_used'] is False


def test_active_builder_qs_alias_preserves_current_task_priority():
    c = client()
    cid = 'alpha22_active_alias_guard'
    start = post(c, cid, 'a22_guard_001', 'Build me a BOQ')
    task_id = start['active_task_id']
    data = post(c, cid, 'a22_guard_002', 'Create a Schedule of Values')
    assert data['route'] == 'active_task_new_command_confirmation'
    assert data['active_task_id'] == task_id
    assert data['requires_clarification'] is True
    assert data['fallback_used'] is False
    assert data['reducer_result']['plan_mutated'] is False


def test_valid_zone_value_same_still_reaches_slot_reducer():
    c = client()
    cid = 'alpha22_same_zone_value'
    post(c, cid, 'a22_same_001', 'Build me a BOQ')
    post(c, cid, 'a22_same_002', 'Zone 1: Old and New')
    data = post(c, cid, 'a22_same_003', 'Add Same to Zone 1')
    assert data['route'] == 'active_task_slot_edit'
    plan = c.get(f'/api/plan/{cid}').json()
    assert plan['plan_summary']['zones'][0]['values'] == ['Old', 'New', 'Same']
