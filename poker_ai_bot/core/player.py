"""
Enhanced player base class with action tracking and decision making interface.
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from enum import Enum

from .deck import Card


class Action(Enum):
    FOLD = "fold"
    CALL = "call"
    RAISE = "raise"
    CHECK = "check"
    ALL_IN = "all_in"


class ActionHistory:
    """Tracks a player's action history for analysis."""
    
    def __init__(self):
        self.actions = []
        self.bets = []
        self.round_actions = {"preflop": [], "flop": [], "turn": [], "river": []}
    
    def add_action(self, action: Action, amount: int = 0, round_name: str = ""):
        """Add an action to the history."""
        self.actions.append((action, amount))
        self.bets.append(amount)
        if round_name in self.round_actions:
            self.round_actions[round_name].append((action, amount))
    
    def get_total_invested(self) -> int:
        """Get total amount invested this hand."""
        return sum(self.bets)
    
    def clear(self):
        """Clear history for new hand."""
        self.actions.clear()
        self.bets.clear()
        for round_actions in self.round_actions.values():
            round_actions.clear()


class Player(ABC):
    """Base class for all poker players (human, AI, etc.)."""
    
    def __init__(self, name: str, stack: int = 1000):
        self.name = name
        self.stack = stack  # Total chips
        self.hole_cards: List[Card] = []
        self.current_bet = 0  # Amount bet in current betting round
        self.folded = False
        self.all_in = False
        self.action_history = ActionHistory()
        
    def receive_cards(self, cards: List[Card]) -> None:
        """Receive hole cards."""
        self.hole_cards = cards.copy()
    
    def bet(self, amount: int) -> int:
        """Bet or raise by specified amount. Returns actual amount bet."""
        if amount > self.stack:
            # All-in scenario
            actual_bet = self.stack
            self.stack = 0
            self.all_in = True
        else:
            actual_bet = amount
            self.stack -= amount
        
        self.current_bet += actual_bet
        return actual_bet
    
    def call(self, amount_to_call: int) -> int:
        """Call the specified amount. Returns actual amount called."""
        return self.bet(amount_to_call)
    
    def fold(self) -> None:
        """Fold the current hand."""
        self.folded = True
    
    def check(self) -> None:
        """Check (bet 0)."""
        pass  # No action needed
    
    def reset_for_new_hand(self) -> None:
        """Reset player state for a new hand."""
        self.hole_cards.clear()
        self.current_bet = 0
        self.folded = False
        self.all_in = False
        self.action_history.clear()
    
    def add_chips(self, amount: int) -> None:
        """Add chips to player's stack."""
        self.stack += amount
    
    def can_bet(self, amount: int) -> bool:
        """Check if player can bet the specified amount."""
        return self.stack >= amount and not self.folded and not self.all_in
    
    @abstractmethod
    def decide_action(self, game_state: 'GameState') -> tuple[Action, int]:
        """
        Decide what action to take given the current game state.
        Returns (action, amount) tuple.
        """
        pass
    
    def __str__(self) -> str:
        status = []
        if self.folded:
            status.append("FOLDED")
        if self.all_in:
            status.append("ALL-IN")
        
        status_str = f" ({', '.join(status)})" if status else ""
        return f"{self.name}: ${self.stack}{status_str}"
    
    def __repr__(self) -> str:
        return f"Player({self.name}, ${self.stack})"