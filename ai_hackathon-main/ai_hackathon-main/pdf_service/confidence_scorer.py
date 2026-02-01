def score_confidence(pages, tables):
    score = 1.0

    if not pages:
        score -= 0.5
    if len(tables) == 0:
        score -= 0.2

    return max(score, 0.0)
