# Alpha.25 Build Discipline

This build follows the Jarvis route/governance rule:

```text
Classify once. Route once. Contract once. Execute only behind explicit approval.
```

## Patch rules for future FIRE work

1. No scattered if/else phrase patches outside the owning route family.
2. No new duplicate route owner.
3. No helper may directly start a tool.
4. No route may be added without owner, contract, safety policy, tests, and fallback behavior.
5. Protected Builder boundary files must be hash-checked before and after any approved touch.
6. If a protected file must be touched later, isolate the change first and test it before merging.
7. Registry metadata can describe future tools, but registry execution must stay disabled unless explicitly approved.

## Alpha.25 status

Alpha.25 is documentation/audit only. The legacy Builder bridge is not connected.
