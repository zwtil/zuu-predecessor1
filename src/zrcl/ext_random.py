import random

HALVED_WEIGHTS = {
    0: 0.5,
    1: 0.25,
    2: 0.125,
    3: 0.0625,
    4: 0.03125,
    5: 0.015625,
}


def weighted_choice(choices=HALVED_WEIGHTS, sumk=1):
    values = list(choices.keys())
    probabilities = list(choices.values())

    # Normalize the probabilities to sum to 1
    total = sum(probabilities)
    normalized_probabilities = [p / total for p in probabilities]

    res = random.choices(values, normalized_probabilities, k=1)[0]
    return res + weighted_choice(choices, sumk - 1) if sumk > 1 else res
