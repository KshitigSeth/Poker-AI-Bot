import random
from collections import Counter
from poker_shared import evaluate_hand

# Define card values and suits
SUITS = ['♠', '♥', '♦', '♣']
RANKS = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

class Card:
    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit
    
    def __repr__(self):
        return f"{self.rank}{self.suit}"

class Deck:
    def __init__(self):
        self.cards = [Card(rank, suit) for suit in SUITS for rank in RANKS]
        random.shuffle(self.cards)
    
    def draw(self, num=1):
        return [self.cards.pop() for _ in range(num)]

class Player:
    def __init__(self, name, balance=1000):
        self.name = name
        self.hand = []
        self.balance = balance
        self.current_bet = 0
        self.folded = False

    def receive_cards(self, cards):
        self.hand.extend(cards)

    def place_bet(self, amount):
        if amount > self.balance:
            raise ValueError(f"{self.name} cannot bet {amount}, insufficient funds.")
        self.balance -= amount
        self.current_bet += amount

    def fold(self):
        self.folded = True

    def __repr__(self):
        return f"{self.name}: {self.hand} (Balance: ${self.balance})"

class PokerGame:
    def __init__(self, players):
        self.players = [Player(name) for name in players]
        self.deck = Deck()
        self.community_cards = []
        self.pot = 0
        self.current_bet = 0
        self.round = 0
        self.active_players = self.players[:]
    
    def deal_hole_cards(self):
        for player in self.players:
            player.receive_cards(self.deck.draw(2))
    
    def deal_community_cards(self, num):
        self.community_cards.extend(self.deck.draw(num))
    
    def betting_round(self):
        for player in self.active_players:
            if not player.folded:
                action = input(f"{player.name}, action (call, raise, fold): ")
                if action == "fold":
                    player.fold()
                elif action == "raise":
                    amount = int(input("Enter raise amount: "))
                    player.place_bet(amount)
                    self.current_bet = amount
                elif action == "call":
                    player.place_bet(self.current_bet)
                self.pot += player.current_bet

    def showdown(self):
        best_hand = None
        winner = None
        for player in self.players:
            if not player.folded:
                hand = evaluate_hand(player.hand + self.community_cards)
                print(f"{player.name}'s best hand: {hand}")
                if best_hand is None or HAND_RANKINGS.index(hand) > HAND_RANKINGS.index(best_hand):
                    best_hand = hand
                    winner = player
        print(f"Winner: {winner.name} with {best_hand}!")
        winner.balance += self.pot
        self.pot = 0
    
    def play(self):
        self.deal_hole_cards()
        print("Hole Cards Dealt")
        self.betting_round()
        self.deal_community_cards(3)  # Flop
        print("Flop: ", self.community_cards)
        self.betting_round()
        self.deal_community_cards(1)  # Turn
        print("Turn: ", self.community_cards)
        self.betting_round()
        self.deal_community_cards(1)  # River
        print("River: ", self.community_cards)
        self.betting_round()
        self.showdown()

# Running a test game
if __name__ == "__main__":
    game = PokerGame(["Alice", "Bob", "Charlie"])
    game.play()