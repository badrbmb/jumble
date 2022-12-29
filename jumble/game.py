
"""
Contains class definitions to play the game
"""

import random
import string
import requests

class Game:
    """Create a game instance"""


    def __init__(self) -> list:
        """Attribute a random grid to size 9"""
        self.grid = [random.choice(string.ascii_uppercase) for _ in range(9)]

    def is_valid(self, word: str) -> bool:
        """Check if a given world is valid"""

        # check it's a string
        if not isinstance(word, str):
            return False

        # check not empty string
        if len(word.strip()) == 0:
            return False

        # check if the given world is a subset of the desired solution
        letters = self.grid.copy() # Consume letters from the grid
        for letter in word:
            if letter in letters:
                letters.remove(letter)
            else:
                return False

        # check if the given world is real word
        response = requests.get(f"{Game.URL}/{word}")
        # make sure status code is 200
        response.raise_for_status()
        # get reponse
        return response.json()['found']
