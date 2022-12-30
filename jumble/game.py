from typing import List
from dataclasses import dataclass
from jumble import schemas, crud
from jumble.database import SessionLocal
import random

"""
Contains class definitions to play the game
"""

@dataclass
class Game:
    """Create a game instance"""
    to_exclude: List[int]
    difficulty_level: schemas.DifficultyLevel

    def __post_init__(self):
        """generate random master word and excecute queries"""
        with SessionLocal() as db:
            self.master_word = crud.read_rnd_master_word(db=db, exclude_ids=[])

            # get associated jumbles and options
            self.jumble_solution = {
                i.id: crud.read_single_jumble_option(
                    jumble_id=i.id, db=db, level=self.difficulty_level,
                    order=schemas.JumbleOptionScoreSort.rdn
                    )
                for i in self.master_word.jumbles
                }


    @property
    def solution(self) -> str:
        return self.master_word.solution

    @property
    def jumbles(self) -> dict:
        out = {}
        for jumble_id, jumble_solution in self.jumble_solution.items():
            # shuffle jumble options
            shuffled = list(jumble_solution.word)
            random.shuffle(shuffled)
            out[jumble_id] = {
                'solution': jumble_solution.word,
                'shuffled': shuffled,
                'placeholder': jumble_solution.placeholder,
                'hint': jumble_solution.defs
            }
        return out

    @property
    def image_url(self) -> str:
        return self.master_word.image_url

    @property
    def dialogue(self) -> str:
        return self.master_word.dialogue

    @property
    def to_complete(self) -> str:
        return self.master_word.to_complete
