from __future__ import annotations

from jarvis_v5.core.conversation_store import ConversationStore
from jarvis_v5.core.active_task_store import ActiveTaskStore
from jarvis_v5.core.attachment_store import AttachmentStore
from jarvis_v5.core.event_ledger import EventLedger
from jarvis_v5.core.snapshot_store import SnapshotStore
from jarvis_v5.core.adapter_store import AdapterDryRunStore
from jarvis_v5.core.engine_contract_store import EngineContractStore
from jarvis_v5.core.engine_preflight_store import EnginePreflightStore
from jarvis_v5.core.engine_execution_store import EngineExecutionStore


class StateKernel:
    """Canonical state access for Jarvis v5 alpha.1.

    Alpha.1 owns only state creation/loading/binding. It does not call any QS engines.
    """

    def __init__(self):
        self.conversations = ConversationStore()
        self.tasks = ActiveTaskStore()
        self.attachments = AttachmentStore()
        self.events = EventLedger()
        self.snapshots = SnapshotStore()
        self.adapters = AdapterDryRunStore()
        self.contracts = EngineContractStore()
        self.preflights = EnginePreflightStore()
        self.executions = EngineExecutionStore()
