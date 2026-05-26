def test_boq_alpha35_regression():
    result = run_jarvis(input_case="alpha35")

    golden = load_golden("case_alpha35.xlsx")

    diffs = compare_boQ_outputs(result, golden)

    assert diffs == [], f"BOQ REGRESSION FAILED: {diffs}"