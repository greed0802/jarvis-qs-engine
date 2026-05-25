# Workbook Access Boundary Policy — v1

Jarvis must not read workbook contents until a future approved alpha explicitly enables workbook reading.

## Required gates before any future read
1. Active Builder task exists.
2. Workbook metadata is attached and bound to the active task.
3. Snapshot is current.
4. Adapter dry run is current.
5. Engine contract is ready.
6. Boundary audit is clean.
7. Preflight is ready.
8. User explicitly approves preview execution.
9. `WORKBOOK_READ_ENABLED=true` in config.
10. Legacy Builder callable and Excel output policies are explicitly enabled for the approved scope.

## Blocked in alpha.27
- Opening workbook files.
- Parsing workbook sheets.
- Resolving executable workbook paths.
- Reading cells or formulas.
- Following external/network paths.

Alpha.27 may only display existing metadata such as workbook ID, filename, and source.
