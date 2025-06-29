"""
Deck and Card classes for poker game management.
"""
import random
from typing import List, Optional
from enum import Enum


class Suit(Enum):
    SPADES = '♠'
    HEARTS = '♥'
    DIAMONDS = '♦'
    CLUBS = '♣'


class Rank(Enum):
    TWO = ('2', 2)
    THREE = ('3', 3)
    FOUR = ('4', 4)
    FIVE = ('5', 5)
    SIX = ('6', 6)
    SEVEN = ('7', 7)
    EIGHT = ('8', 8)
    NINE = ('9', 9)
    TEN = ('T', 10)
    JACK = ('J', 11)
    QUEEN = ('Q', 12)
    KING = ('K', 13)
    ACE = ('A', 14)
    
    def __init__(self, symbol, numeric_value):
        self.symbol = symbol
        self.numeric_value = numeric_value


class Card:
    """Represents a playing card with rank and suit."""
    
    def __init__(self, rank: Rank, suit: Suit):
        self.rank = rank
        self.suit = suit
    
    def __repr__(self) -> str:
        return f"{self.rank.symbol}{self.suit.value}"
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, Card):
            return False
        return self.rank == other.rank and self.suit == other.suit
    
    def __hash__(self) -> int:
        return hash((self.rank, self.suit))
    
    def __lt__(self, other) -> bool:
        return self.rank.numeric_value < other.rank.numeric_value
    
    def __le__(self, other) -> bool:
        return self.rank.numeric_value <= other.rank.numeric_value
    
    def __gt__(self, other) -> bool:
        return self.rank.numeric_value > other.rank.numeric_value
    
    def __ge__(self, other) -> bool:
        return self.rank.numeric_value >= other.rank.numeric_value


class Deck:
    """Standard 52-card deck with shuffle and dealing capabilities."""
    
    def __init__(self, shuffled: bool = True):
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        if shuffled:
            self.shuffle()
    
    def shuffle(self) -> None:
        """Shuffle the deck."""
        random.shuffle(self.cards)
    
    def deal(self, num_cards: int = 1) -> List[Card]:
        """Deal specified number of cards from the top of the deck."""
        if num_cards > len(self.cards):
            raise ValueError(f"Cannot deal {num_cards} cards, only {len(self.cards)} remaining")
        
        dealt_cards = []
        for _ in range(num_cards):
            dealt_cards.append(self.cards.pop())
        return dealt_cards
    
    def deal_one(self) -> Card:
        """Deal a single card."""
        return self.deal(1)[0]
    
    def cards_remaining(self) -> int:
        """Get number of cards remaining in deck."""
        return len(self.cards)
    
    def reset(self, shuffled: bool = True) -> None:
        """Reset deck to full 52 cards."""
        self.cards = [Card(rank, suit) for rank in Rank for suit in Suit]
        if shuffled:
            self.shuffle()
    
    def remove_cards(self, cards_to_remove: List[Card]) -> None:
        """Remove specific cards from deck (useful for simulations)."""
        for card in cards_to_remove:
            if card in self.cards:
                self.cards.remove(card)
    
    def __len__(self) -> int:
        return len(self.cards)
    
    def __repr__(self) -> str:
        return f"Deck({len(self.cards)} cards)"
