from fastapi.testclient import TestClient

from jarvis_v5.app import app


def client():
    return TestClient(app)


def start_complete_wall_types(c, conversation_id="alpha19_wall_contract"):
    c.post('/api/chat', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_start", "text": "Build me a BOQ"})
    with open('jarvis_v5/tests/fixtures/Test.xlsx','rb') as f:
        c.post('/api/attach', data={"conversation_id": conversation_id, "client_event_id": conversation_id+"_attach", "text":"Here"}, files={"file": ("Test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    for suffix, text in [
        ("trade", "Use Wall Types"),
        ("function", "Use XGETWALLAREA"),
        ("unit", "Unit m2"),
        ("zone", "Zone 1: Old and New"),
        ("head", "Use Head 2 for Zone 1"),
        ("levels", "Levels GF to L3"),
    ]:
        c.post('/api/chat', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_"+suffix, "text": text})
    c.post('/api/builder/create-snapshot', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_snapshot"})
    c.post('/api/builder/adapter-dry-run', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_adapter"})
    return c.post('/api/builder/engine-contract', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_contract"}).json()


def start_complete_reinforcement(c, conversation_id="alpha19_reo_contract"):
    c.post('/api/chat', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_start", "text": "Build me a BOQ"})
    with open('jarvis_v5/tests/fixtures/Test.xlsx','rb') as f:
        c.post('/api/attach', data={"conversation_id": conversation_id, "client_event_id": conversation_id+"_attach", "text":"Here"}, files={"file": ("Test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")})
    c.post('/api/chat', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_reinforcement", "text": "Use Reinforcement"})
    for suffix, text in [
        ("resolve", "Use XGETCUSTOM with Reinforcement Weight unit t"),
        ("zone", "Zone 1: Old and New"),
        ("head", "Use Head 2 for Zone 1"),
        ("levels", "Levels GF to L3"),
    ]:
        c.post('/api/chat', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_"+suffix, "text": text})
    c.post('/api/builder/create-snapshot', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_snapshot"})
    c.post('/api/builder/adapter-dry-run', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_adapter"})
    return c.post('/api/builder/engine-contract', json={"conversation_id": conversation_id, "client_event_id": conversation_id+"_contract"}).json()


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


def test_alpha19_version_and_locks():
    data = client().get('/api/version').json()
    assert data['version'] == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    assert data['engines_connected']['builder_contract_fixture_replay'] is False
    assert data['execution_locks']['builder_engine_execution_enabled'] is False
    assert data['execution_locks']['legacy_builder_callable'] is False
    assert data['execution_locks']['workbook_read_enabled'] is False
    assert data['execution_locks']['excel_output_enabled'] is False


def test_wall_types_contract_fixture_replay_clean():
    c = client()
    conv = 'alpha19_wall_replay_clean'
    contract = start_complete_wall_types(c, conv)
    assert contract['route'] == 'builder_engine_contract_created'
    replay = c.post('/api/builder/contract-fixture-replay', json={
        "conversation_id": conv,
        "client_event_id": conv+"_replay",
        "fixture": "wall_types_xgetwallarea_zone1_head2_gf_l3_contract_v1",
        "write_report": False,
    }).json()
    assert replay['route'] == 'builder_contract_fixture_replay'
    assert replay['passed'] is True
    assert replay['diff_status'] == 'clean'
    assert replay['diffs'] == []
    assert replay['contract_schema_version'] == 'builder_contract_v1'
    assert_safety(replay)


def test_reinforcement_contract_fixture_replay_clean():
    c = client()
    conv = 'alpha19_reo_replay_clean'
    contract = start_complete_reinforcement(c, conv)
    assert contract['route'] == 'builder_engine_contract_created'
    replay = c.post('/api/builder/contract-fixture-replay', json={
        "conversation_id": conv,
        "client_event_id": conv+"_replay",
        "fixture": "reinforcement_xgetcustom_weight_t_zone1_head2_gf_l3_contract_v1",
        "write_report": False,
    }).json()
    assert replay['route'] == 'builder_contract_fixture_replay'
    assert replay['passed'] is True
    assert replay['diff_status'] == 'clean'
    assert replay['actual_stable']['builder_setup']['trade_profile'] == 'Concrete / Reinforcement'
    assert_safety(replay)


def test_contract_fixture_replay_detects_mismatch_without_engine():
    c = client()
    conv = 'alpha19_wall_replay_mismatch'
    contract = start_complete_wall_types(c, conv)
    assert contract['route'] == 'builder_engine_contract_created'
    replay = c.post('/api/builder/contract-fixture-replay', json={
        "conversation_id": conv,
        "client_event_id": conv+"_replay",
        "fixture": "wall_types_xgetwallarea_zone1_head2_gf_l3_contract_v1",
        "intentional_mismatch": True,
        "write_report": False,
    }).json()
    assert replay['route'] == 'builder_contract_fixture_replay'
    assert replay['passed'] is False
    assert replay['diff_status'] == 'mismatch'
    assert len(replay['diffs']) >= 1
    assert_safety(replay)


def test_contract_fixture_replay_visible_in_plan():
    c = client()
    conv = 'alpha19_plan_replay_visible'
    start_complete_wall_types(c, conv)
    replay = c.post('/api/builder/contract-fixture-replay', json={
        "conversation_id": conv,
        "client_event_id": conv+"_replay",
        "fixture": "wall_types_xgetwallarea_zone1_head2_gf_l3_contract_v1",
        "write_report": False,
    }).json()
    assert replay['passed'] is True
    plan = c.get(f'/api/plan/{conv}').json()
    assert plan['contract_fixture_replay']['found'] is True
    assert plan['contract_fixture_replay']['diff_status'] == 'clean'
    assert plan['contract_fixture_replay']['workbook_read'] is False
    assert plan['engine_execution']['status'] in ['not_requested', 'blocked_by_kill_switch']
