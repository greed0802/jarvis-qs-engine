# Legacy Builder Input Inventory

Purpose: list what the legacy Builder engine is expected to need before any future connection. This is an audit inventory only. Alpha.25 does not import, call, or execute the legacy Builder.

| Input family | Expected legacy need | Alpha.25 status |
|---|---|---|
| Workbook | Real workbook file path or safe workbook handle | Not connected; v5 currently keeps metadata-only `workbook_ref` |
| Trade/profile | Wall Types, Doors/Windows, Structural Steel, Concrete/Reo, etc. | Present in v5 contract as `builder_setup.trade_profile` |
| CostX function | XGETWALLAREA, XGETCOUNT, XGETCUSTOM, etc. | Present in v5 contract as `builder_setup.costx_function` |
| Custom quantity | Required for XGETCUSTOM | Present when set; must be required before future execution |
| Unit | m2, m3, m, no, t, etc. | Present in v5 contract as `builder_setup.unit` |
| Dynamic zones | Zone IDs, values, and head assignment | Present in v5 contract as `builder_setup.dynamic_zones` |
| Heading assignments | Zone-to-Head mapping | Present as `builder_setup.heading_assignments` |
| Levels | Level list including mezzanine aliases | Present as `builder_setup.levels` |
| Aliases | Mezzanine/Mezz and similar controlled aliases | Present as `builder_setup.aliases` |
| Item code settings | Item code behavior | Present as `builder_setup.item_code_settings`, may need stricter schema later |
| Zone mode | Rebuild/preserve-source mode | Present as `builder_setup.zone_mode` |
| Output path | Where preview/export file should be written | Missing; future output manifest required |
| Preview result | Rows, warnings, formula integrity status | Missing; future preview result schema required |
| Export result | Final workbook manifest and download details | Missing; future export result schema required |
| Error handling | Recoverable error object and rollback behavior | Missing; future engine failure contract required |

## Current bridge conclusion

The v5 contract contains most setup fields, but real execution still needs workbook-read permission, an output manifest, preview/export result schemas, formula-integrity integration, and an explicit approval policy.
