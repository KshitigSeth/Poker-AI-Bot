"""
Comprehensive game state management for Texas Hold'em poker.
Handles full game flow including betting rounds, pot management, and hand resolution.
"""
from typing import List, Optional, Dict, Tuple
from enum import Enum

from .deck import Deck, Card
from .hand_evaluator import HandEvaluator
from .player import Player, Action


class BettingRound(Enum):
    PREFLOP = "preflop"
    FLOP = "flop"
    TURN = "turn"
    RIVER = "river"


class GameState:
    """Manages the complete state of a Texas Hold'em poker game."""
    
    def __init__(self, players: List[Player], small_blind: int = 10, big_blind: int = 20):
        self.players = players
        self.deck = Deck()
        self.community_cards: List[Card] = []
        self.pot = 0
        self.side_pots: List[int] = []  # For all-in scenarios
        self.current_bet = 0
        self.small_blind = small_blind
        self.big_blind = big_blind
        self.dealer_position = 0
        self.current_round = BettingRound.PREFLOP
        self.action_position = 0
        self.hand_number = 0
        
    def start_new_hand(self) -> None:
        """Initialize a new hand of poker."""
        self.hand_number += 1
        self.deck.reset()
        self.community_cards.clear()
        self.pot = 0
        self.side_pots.clear()
        self.current_bet = 0
        self.current_round = BettingRound.PREFLOP
        
        # Reset all players for new hand
        for player in self.players:
            player.reset_for_new_hand()
        
        # Deal hole cards
        self.deal_hole_cards()
        
        # Post blinds
        self.post_blinds()
        
    def deal_hole_cards(self) -> None:
        """Deal two hole cards to each player."""
        for player in self.players:
            if not player.folded:
                cards = self.deck.deal(2)
                player.receive_cards(cards)
    
    def post_blinds(self) -> None:
        """Post small and big blinds."""
        small_blind_pos = (self.dealer_position + 1) % len(self.players)
        big_blind_pos = (self.dealer_position + 2) % len(self.players)
        
        # Post small blind
        sb_player = self.players[small_blind_pos]
        sb_amount = sb_player.bet(min(self.small_blind, sb_player.stack))
        self.pot += sb_amount
        
        # Post big blind
        bb_player = self.players[big_blind_pos]
        bb_amount = bb_player.bet(min(self.big_blind, bb_player.stack))
        self.pot += bb_amount
        self.current_bet = bb_amount
        
        # Set action position (first to act preflop)
        self.action_position = (big_blind_pos + 1) % len(self.players)
    
    def deal_flop(self) -> None:
        """Deal the flop (3 community cards)."""
        self.deck.deal_one()  # Burn card
        self.community_cards.extend(self.deck.deal(3))
        self.current_round = BettingRound.FLOP
        self.reset_betting_round()
    
    def deal_turn(self) -> None:
        """Deal the turn (4th community card)."""
        self.deck.deal_one()  # Burn card
        self.community_cards.extend(self.deck.deal(1))
        self.current_round = BettingRound.TURN
        self.reset_betting_round()
    
    def deal_river(self) -> None:
        """Deal the river (5th community card)."""
        self.deck.deal_one()  # Burn card
        self.community_cards.extend(self.deck.deal(1))
        self.current_round = BettingRound.RIVER
        self.reset_betting_round()
    
    def reset_betting_round(self) -> None:
        """Reset betting for a new betting round."""
        self.current_bet = 0
        for player in self.players:
            player.current_bet = 0
        
        # Set action to first active player after dealer
        self.action_position = (self.dealer_position + 1) % len(self.players)
        while (self.players[self.action_position].folded or 
               self.players[self.action_position].all_in):
            self.action_position = (self.action_position + 1) % len(self.players)
    
    def execute_action(self, player: Player, action: Action, amount: int = 0) -> bool:
        """Execute a player's action. Returns True if action was valid."""
        if player.folded or player.all_in:
            return False
        
        if action == Action.FOLD:
            player.fold()
            
        elif action == Action.CHECK:
            if self.current_bet > player.current_bet:
                return False  # Cannot check when there's a bet to call
            
        elif action == Action.CALL:
            amount_to_call = self.current_bet - player.current_bet
            if amount_to_call <= 0:
                return False  # Nothing to call
            actual_amount = player.bet(amount_to_call)
            self.pot += actual_amount
            
        elif action == Action.RAISE:
            total_bet = self.current_bet + amount
            amount_to_bet = total_bet - player.current_bet
            
            if amount_to_bet > player.stack:
                # All-in
                actual_amount = player.bet(player.stack)
                self.pot += actual_amount
                self.current_bet = player.current_bet
            else:
                actual_amount = player.bet(amount_to_bet)
                self.pot += actual_amount
                self.current_bet = total_bet
        
        # Record action in history
        player.action_history.add_action(action, amount, self.current_round.value)
        return True
    
    def is_betting_round_complete(self) -> bool:
        """Check if the current betting round is complete."""
        active_players = [p for p in self.players if not p.folded]
        
        if len(active_players) <= 1:
            return True
        
        # Check if all active players have matched the current bet or are all-in
        for player in active_players:
            if not player.all_in and player.current_bet < self.current_bet:
                return False
        
        return True
    
    def get_active_players(self) -> List[Player]:
        """Get list of players still in the hand."""
        return [p for p in self.players if not p.folded]
    
    def get_next_to_act(self) -> Optional[Player]:
        """Get the next player to act, or None if betting round is complete."""
        if self.is_betting_round_complete():
            return None
        
        start_pos = self.action_position
        current_pos = start_pos
        
        while True:
            player = self.players[current_pos]
            if not player.folded and not player.all_in:
                # Check if this player needs to act
                if player.current_bet < self.current_bet:
                    return player
            
            current_pos = (current_pos + 1) % len(self.players)
            if current_pos == start_pos:
                break
        
        return None
    
    def determine_winners(self) -> List[Tuple[Player, int]]:
        """Determine winners and their winnings. Returns list of (player, amount) tuples."""
        active_players = self.get_active_players()
        
        if len(active_players) == 1:
            # Only one player left - they win everything
            winner = active_players[0]
            return [(winner, self.pot)]
        
        # Evaluate hands for showdown
        player_hands = []
        for player in active_players:
            all_cards = player.hole_cards + self.community_cards
            hand_strength = HandEvaluator.evaluate_hand(all_cards)
            player_hands.append((player, hand_strength))
        
        # Sort by hand strength (best first)
        player_hands.sort(key=lambda x: x[1], reverse=True)
        
        # Determine winners (handle ties)
        winners = []
        best_hand = player_hands[0][1]
        
        for player, hand_strength in player_hands:
            if hand_strength == best_hand:
                winners.append(player)
            else:
                break
        
        # Split pot among winners
        winnings_per_player = self.pot // len(winners)
        remainder = self.pot % len(winners)
        
        results = []
        for i, winner in enumerate(winners):
            amount = winnings_per_player
            if i < remainder:  # Distribute remainder starting from first winner
                amount += 1
            results.append((winner, amount))
        
        return results
    
    def advance_dealer(self) -> None:
        """Move dealer button to next position."""
        self.dealer_position = (self.dealer_position + 1) % len(self.players)
    
    def get_pot_odds(self, player: Player) -> float:
        """Calculate pot odds for a player."""
        amount_to_call = self.current_bet - player.current_bet
        if amount_to_call <= 0:
            return float('inf')  # No cost to call
        
        total_pot_after_call = self.pot + amount_to_call
        return total_pot_after_call / amount_to_call
    
    def get_effective_stack_sizes(self) -> Dict[str, int]:
        """Get effective stack sizes for all players."""
        return {player.name: player.stack for player in self.players}
    
    def __str__(self) -> str:
        player_info = []
        for i, player in enumerate(self.players):
            prefix = "D" if i == self.dealer_position else " "
            player_info.append(f"{prefix}{player}")
        
        return (f"Hand #{self.hand_number} - {self.current_round.value.title()}\n"
                f"Community: {self.community_cards}\n"
                f"Pot: ${self.pot}\n"
                f"Players: {', '.join(player_info)}")
