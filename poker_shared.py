import itertools
from collections import Counter

RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
SUITS = ['♠', '♥', '♦', '♣']
HAND_RANKINGS = [
    "High Card", "One Pair", "Two Pair", "Three of a Kind",
    "Straight", "Flush", "Full House", "Four of a Kind",
    "Straight Flush", "Royal Flush"
]

def card_value(card):
    """Returns numerical value of a card."""
    return RANKS.index(card.rank)

def is_flush(cards):
    """Checks if all cards have the same suit."""
    suits = [card.suit for card in cards]
    return len(set(suits)) == 1

def is_straight(cards):
    """Checks if cards form a straight sequence."""
    values = sorted(card_value(card) for card in cards)
    return all(values[i] + 1 == values[i + 1] for i in range(len(values) - 1))

def get_hand_rank(cards):
    """Determines the best hand ranking."""
    values = sorted([card_value(card) for card in cards], reverse=True)
    counts = Counter(values)
    
    if is_flush(cards) and is_straight(cards):
        return "Royal Flush" if max(values) == RANKS.index('A') else "Straight Flush"
    if 4 in counts.values():
        return "Four of a Kind"
    if 3 in counts.values() and 2 in counts.values():
        return "Full House"
    if is_flush(cards):
        return "Flush"
    if is_straight(cards):
        return "Straight"
    if 3 in counts.values():
        return "Three of a Kind"
    if list(counts.values()).count(2) == 2:
        return "Two Pair"
    if 2 in counts.values():
        return "One Pair"
    return "High Card"

def evaluate_hand(cards):
    """Evaluates the best possible hand from a set of 7 cards."""
    best_rank = "High Card"
    for combo in itertools.combinations(cards, 5):
        rank = get_hand_rank(combo)
        if HAND_RANKINGS.index(rank) > HAND_RANKINGS.index(best_rank):
            best_rank = rank
    return best_rank
