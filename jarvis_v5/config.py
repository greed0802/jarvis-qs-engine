from pathlib import Path

APP_VERSION = "v5.0.0-alpha.36.3"
APP_NAME = "Jarvis v5 Active Writing Report Preview False-positive Guard"
PACKAGE_ROOT = Path(__file__).resolve().parent
DATA_ROOT = PACKAGE_ROOT / "data"
CONVERSATIONS_DIR = DATA_ROOT / "conversations"
ACTIVE_TASKS_DIR = DATA_ROOT / "active_tasks"
ATTACHMENTS_DIR = DATA_ROOT / "attachments"
OUTPUTS_DIR = DATA_ROOT / "outputs"
EVENTS_DIR = DATA_ROOT / "events"
SNAPSHOTS_DIR = DATA_ROOT / "snapshots"
ADAPTERS_DIR = DATA_ROOT / "adapters"
CONTRACTS_DIR = DATA_ROOT / "contracts"
PREFLIGHTS_DIR = DATA_ROOT / "preflights"
EXECUTIONS_DIR = DATA_ROOT / "engine_execution_requests"
TEST_REPORTS_DIR = DATA_ROOT / "test_reports"
LEGACY_IMPORT_AUDITS_DIR = DATA_ROOT / "legacy_import_boundary_audits"

for _path in [CONVERSATIONS_DIR, ACTIVE_TASKS_DIR, ATTACHMENTS_DIR, OUTPUTS_DIR, EVENTS_DIR, SNAPSHOTS_DIR, ADAPTERS_DIR, CONTRACTS_DIR, PREFLIGHTS_DIR, EXECUTIONS_DIR, TEST_REPORTS_DIR, LEGACY_IMPORT_AUDITS_DIR]:
    _path.mkdir(parents=True, exist_ok=True)

# Alpha.18 hard kill switches. These are intentionally not user-toggleable.
BUILDER_ENGINE_EXECUTION_ENABLED = False
LEGACY_BUILDER_CALLABLE = False
WORKBOOK_READ_ENABLED = False
EXCEL_OUTPUT_ENABLED = False
