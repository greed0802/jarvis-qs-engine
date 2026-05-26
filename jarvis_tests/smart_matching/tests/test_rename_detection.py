from jarvis_tests.smart_matching.engine.rename_detector import detect_renamed_items

def test_rename_detection():

    old_items = [
        {
            "description": "100mm Concrete Block Wall"
        }
    ]

    new_items = [
        {
            "description": "100mm CMU Wall Partition"
        }
    ]

    matches = detect_renamed_items(
        old_items,
        new_items,
        threshold=40
    )

    assert len(matches) == 1