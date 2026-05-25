from pathlib import Path
import hashlib

from fastapi.testclient import TestClient

from jarvis_v5.app import app
from jarvis_v5.config import APP_VERSION, PACKAGE_ROOT


def test_alpha25_version_and_execution_locks():
    data = TestClient(app).get('/api/version').json()
    assert data['version'] == APP_VERSION == 'v5.0.0-alpha.36.3'
    assert data['engines_connected']['builder'] is False
    locks = data['execution_locks']
    assert locks['builder_engine_execution_enabled'] is False
    assert locks['legacy_builder_callable'] is False
    assert locks['workbook_read_enabled'] is False
    assert locks['excel_output_enabled'] is False


def test_alpha25_audit_docs_exist():
    docs = PACKAGE_ROOT / 'docs'
    required = [
        'ALPHA_25_SCOPE.md',
        'ALPHA_25_BUILD_DISCIPLINE.md',
        'LEGACY_BUILDER_INPUT_INVENTORY.md',
        'V5_BUILDER_CONTRACT_INVENTORY.md',
        'BUILDER_CONTRACT_TO_LEGACY_MAPPING.md',
        'LEGACY_BUILDER_BRIDGE_GAP_AUDIT.md',
        'FUTURE_BUILDER_EXECUTION_POLICY.md',
        'PROTECTED_BUILDER_BOUNDARY_HASH_MANIFEST_ALPHA_25.md',
    ]
    for name in required:
        path = docs / name
        assert path.exists(), name
        assert path.read_text().strip(), name


def test_alpha25_protected_builder_boundary_hashes_match_manifest():
    manifest = (PACKAGE_ROOT / 'docs' / 'PROTECTED_BUILDER_BOUNDARY_HASH_MANIFEST_ALPHA_25.md').read_text()
    protected = [
        'jarvis_v5/tools/builder/adapter_dry_run.py',
        'jarvis_v5/tools/builder/engine_contract_adapter.py',
        'jarvis_v5/tools/builder/engine_preflight.py',
        'jarvis_v5/tools/builder/legacy_engine_bridge.py',
        'jarvis_v5/tools/builder/contract_fixture_replay.py',
        'jarvis_v5/core/snapshot_store.py',
        'jarvis_v5/core/adapter_store.py',
        'jarvis_v5/core/engine_contract_store.py',
        'jarvis_v5/core/engine_preflight_store.py',
        'jarvis_v5/core/engine_execution_store.py',
    ]
    root = PACKAGE_ROOT.parent
    for rel in protected:
        digest = hashlib.sha256((root / rel).read_bytes()).hexdigest()
        assert f'`{digest}` | `{rel}`' in manifest
