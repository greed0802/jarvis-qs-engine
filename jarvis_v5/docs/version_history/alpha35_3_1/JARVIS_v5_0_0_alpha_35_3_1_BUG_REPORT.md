# JARVIS v5.0.0-alpha.35.5 Bug Report

Fixed local Windows pytest cleanup failure where raw shutil.rmtree could fail with FileNotFoundError while deleting long nested generated report paths under jarvis_v5/data/test_reports/contract_fixture_replay.

No runtime workbook/read/route behavior changed.
