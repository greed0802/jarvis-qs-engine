# Builder Contract to Legacy Mapping

This mapping is for future bridge planning only. Alpha.25 does not connect the legacy Builder engine.

| Legacy Builder need | v5 contract field | Status | Future action |
|---|---|---|---|
| Workbook input | `contract.workbook_ref` | metadata only | add workbook-read approval and safe path resolver |
| Trade/profile | `contract.builder_setup.trade_profile` | mapped | confirm exact legacy enum names |
| CostX function | `contract.builder_setup.costx_function` | mapped | confirm allowed legacy function set |
| Custom quantity | `contract.builder_setup.custom_quantity` | conditional | enforce required when XGETCUSTOM |
| Unit | `contract.builder_setup.unit` | mapped | confirm unit aliases and display casing |
| Zone mode | `contract.builder_setup.zone_mode` | mapped | confirm rebuild/preserve-source behavior |
| Dynamic zones | `contract.builder_setup.dynamic_zones` | mapped | confirm legacy zone/head data structure |
| Heading assignments | `contract.builder_setup.heading_assignments` | mapped | confirm Head1/Head2/Head3 casing |
| Levels | `contract.builder_setup.levels` | mapped | confirm level token casing and mezzanine aliases |
| Aliases | `contract.builder_setup.aliases` | mapped | confirm when aliases are applied before formula generation |
| Item codes | `contract.builder_setup.item_code_settings` | partial | define stricter item-code schema |
| Formula integrity | none yet | missing | add pre/post formula integrity contract later |
| Preview output | none yet | missing | add preview result schema later |
| Export output | none yet | missing | add output manifest schema later |
| Background job | none yet | missing | add job runner boundary before long execution |

## Bridge principle

The legacy Builder must receive a frozen, validated contract, never raw chat text or mutable active task state.
