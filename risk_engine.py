# risk_engine.py

def calculate_risk_score(probability: int, impact: int) -> int:
    """Calculate risk score using probability × impact."""
    probability = int(probability)
    impact = int(impact)

    if not 1 <= probability <= 5:
        raise ValueError("Probability must be between 1 and 5.")

    if not 1 <= impact <= 5:
        raise ValueError("Impact must be between 1 and 5.")

    return probability * impact


def classify_risk(score: int) -> str:
    """Classify risk based on its score."""
    if not 1 <= score <= 25:
        raise ValueError("Risk score must be between 1 and 25.")

    if score <= 4:
        return "Low"
    elif score <= 9:
        return "Medium"
    elif score <= 16:
        return "High"
    return "Critical"


def assess_risk(probability: int, impact: int) -> dict:
    """Return the score, priority, and suggested action."""
    score = calculate_risk_score(probability, impact)
    level = classify_risk(score)

    actions = {
        "Low": "Accept and monitor the risk.",
        "Medium": "Plan preventive actions and review regularly.",
        "High": "Prioritize mitigation and assign an owner.",
        "Critical": "Take immediate action and escalate for review."
    }

    return {
        "score": score,
        "level": level,
        "recommended_action": actions[level]
    }