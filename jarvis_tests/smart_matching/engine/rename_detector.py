from jarvis_tests.smart_matching.scoring.similarity_engine import similarity_score

def detect_renamed_items(old_items, new_items, threshold=80):

    matches = []

    for old in old_items:
        best_match = None
        best_score = 0

        for new in new_items:

            score = similarity_score(
                old["description"],
                new["description"]
            )

            if score > best_score:
                best_score = score
                best_match = new

        if best_score >= threshold:
            matches.append({
                "old_item": old,
                "new_item": best_match,
                "score": best_score
            })

    return matches