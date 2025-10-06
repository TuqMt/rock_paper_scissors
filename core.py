import random


CHOICES = {
'rock': '✊',
'scissors': '✌️',
'paper': '✋',
}


WIN_RULES = {
('rock', 'scissors'),
('scissors', 'paper'),
('paper', 'rock'),
}




class GameLogic:
    def __init__(self):
        self.score = {'player': 0, 'computer': 0, 'ties': 0}


    def computer_choice(self):
        return random.choice(list(CHOICES.keys()))


    def judge(self, player_choice, computer_choice):
        if player_choice == computer_choice:
            self.score['ties'] += 1
            return 'tie'
        elif (player_choice, computer_choice) in WIN_RULES:
            self.score['player'] += 1
            return 'win'
        else:
            self.score['computer'] += 1
            return 'lose'


    def reset(self):
        self.score = {'player': 0, 'computer': 0, 'ties': 0}