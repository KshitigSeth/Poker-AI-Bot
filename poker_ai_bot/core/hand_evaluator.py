"""
Advanced hand evaluation system for poker hands.
Handles all Texas Hold'em hand rankings with proper comparison.
"""
import itertools
from typing import List, Tuple, Optional
from collections import Counter
from enum import IntEnum

from .deck import Card, Rank, Suit


class HandRank(IntEnum):
    """Hand rankings in ascending order of strength."""
    HIGH_CARD = 1
    ONE_PAIR = 2
    TWO_PAIR = 3
    THREE_OF_A_KIND = 4
    STRAIGHT = 5
    FLUSH = 6
    FULL_HOUSE = 7
    FOUR_OF_A_KIND = 8
    STRAIGHT_FLUSH = 9
    ROYAL_FLUSH = 10


class HandStrength:
    """Represents the strength of a poker hand for comparison."""
    
    def __init__(self, rank: HandRank, primary_value: int, 
                 secondary_value: int = 0, kickers: List[int] = None):
        self.rank = rank
        self.primary_value = primary_value
        self.secondary_value = secondary_value
        self.kickers = kickers or []
    
    def __lt__(self, other) -> bool:
        if self.rank != other.rank:
            return self.rank < other.rank
        if self.primary_value != other.primary_value:
            return self.primary_value < other.primary_value
        if self.secondary_value != other.secondary_value:
            return self.secondary_value < other.secondary_value
        
        # Compare kickers
        for my_kicker, other_kicker in zip(self.kickers, other.kickers):
            if my_kicker != other_kicker:
                return my_kicker < other_kicker
        return False
    
    def __eq__(self, other) -> bool:
        return (self.rank == other.rank and 
                self.primary_value == other.primary_value and
                self.secondary_value == other.secondary_value and
                self.kickers == other.kickers)
    
    def __gt__(self, other) -> bool:
        return not (self < other or self == other)
    
    def __repr__(self) -> str:
        return f"HandStrength({self.rank.name}, {self.primary_value}, {self.secondary_value}, {self.kickers})"


class HandEvaluator:
    """Evaluates poker hands and determines winners."""
    
    @staticmethod
    def is_flush(cards: List[Card]) -> bool:
        """Check if all cards have the same suit."""
        if len(cards) < 5:
            return False
        suits = [card.suit for card in cards]
        return len(set(suits)) == 1
    
    @staticmethod
    def is_straight(values: List[int]) -> bool:
        """Check if values form a straight sequence."""
        if len(values) < 5:
            return False
        
        # Handle Ace-low straight (A,2,3,4,5)
        if values == [14, 5, 4, 3, 2]:
            return True
        
        # Regular straights
        return all(values[i] - 1 == values[i + 1] for i in range(len(values) - 1))
    
    @staticmethod
    def get_straight_high_card(values: List[int]) -> int:
        """Get the high card value for a straight."""
        # Handle Ace-low straight (A,2,3,4,5) - high card is 5
        if values == [14, 5, 4, 3, 2]:
            return 5
        return max(values)
    
    @classmethod
    def evaluate_hand(cls, cards: List[Card]) -> HandStrength:
        """Evaluate the best 5-card hand from given cards."""
        if len(cards) < 5:
            raise ValueError("Need at least 5 cards to evaluate a hand")
        
        best_hand = None
        
        # Try all combinations of 5 cards
        for five_cards in itertools.combinations(cards, 5):
            hand_strength = cls._evaluate_five_cards(list(five_cards))
            if best_hand is None or hand_strength > best_hand:
                best_hand = hand_strength
        
        return best_hand
    
    @classmethod
    def _evaluate_five_cards(cls, cards: List[Card]) -> HandStrength:
        """Evaluate exactly 5 cards."""
        values = sorted([card.rank.numeric_value for card in cards], reverse=True)
        value_counts = Counter(values)
        
        is_flush = cls.is_flush(cards)
        is_straight = cls.is_straight(values)
        
        # Royal Flush (A, K, Q, J, 10 of same suit)
        if is_flush and is_straight and max(values) == 14 and min(values) == 10:
            return HandStrength(HandRank.ROYAL_FLUSH, 14)
        
        # Straight Flush
        if is_flush and is_straight:
            high_card = cls.get_straight_high_card(values)
            return HandStrength(HandRank.STRAIGHT_FLUSH, high_card)
        
        # Four of a Kind
        if 4 in value_counts.values():
            quad_value = [v for v, c in value_counts.items() if c == 4][0]
            kicker = [v for v, c in value_counts.items() if c == 1][0]
            return HandStrength(HandRank.FOUR_OF_A_KIND, quad_value, 0, [kicker])
        
        # Full House
        if 3 in value_counts.values() and 2 in value_counts.values():
            trips_value = [v for v, c in value_counts.items() if c == 3][0]
            pair_value = [v for v, c in value_counts.items() if c == 2][0]
            return HandStrength(HandRank.FULL_HOUSE, trips_value, pair_value)
        
        # Flush
        if is_flush:
            return HandStrength(HandRank.FLUSH, 0, 0, values)
        
        # Straight
        if is_straight:
            high_card = cls.get_straight_high_card(values)
            return HandStrength(HandRank.STRAIGHT, high_card)
        
        # Three of a Kind
        if 3 in value_counts.values():
            trips_value = [v for v, c in value_counts.items() if c == 3][0]
            kickers = sorted([v for v, c in value_counts.items() if c == 1], reverse=True)
            return HandStrength(HandRank.THREE_OF_A_KIND, trips_value, 0, kickers)
        
        # Two Pair
        pairs = [v for v, c in value_counts.items() if c == 2]
        if len(pairs) == 2:
            pairs.sort(reverse=True)
            kicker = [v for v, c in value_counts.items() if c == 1][0]
            return HandStrength(HandRank.TWO_PAIR, pairs[0], pairs[1], [kicker])
        
        # One Pair
        if len(pairs) == 1:
            pair_value = pairs[0]
            kickers = sorted([v for v, c in value_counts.items() if c == 1], reverse=True)
            return HandStrength(HandRank.ONE_PAIR, pair_value, 0, kickers)
        
        # High Card
        return HandStrength(HandRank.HIGH_CARD, 0, 0, values)
    
    @classmethod
    def compare_hands(cls, hand1: List[Card], hand2: List[Card]) -> int:
        """Compare two hands. Returns 1 if hand1 wins, -1 if hand2 wins, 0 if tie."""
        strength1 = cls.evaluate_hand(hand1)
        strength2 = cls.evaluate_hand(hand2)
        
        if strength1 > strength2:
            return 1
        elif strength1 < strength2:
            return -1
        else:
            return 0
    
    @classmethod
    def get_hand_description(cls, cards: List[Card]) -> str:
        """Get a human-readable description of the hand."""
        strength = cls.evaluate_hand(cards)
        
        descriptions = {
            HandRank.HIGH_CARD: "High Card",
            HandRank.ONE_PAIR: "One Pair",
            HandRank.TWO_PAIR: "Two Pair",
            HandRank.THREE_OF_A_KIND: "Three of a Kind",
            HandRank.STRAIGHT: "Straight",
            HandRank.FLUSH: "Flush",
            HandRank.FULL_HOUSE: "Full House",
            HandRank.FOUR_OF_A_KIND: "Four of a Kind",
            HandRank.STRAIGHT_FLUSH: "Straight Flush",
            HandRank.ROYAL_FLUSH: "Royal Flush"
        }
        
        return descriptions[strength.rank]
