from pydantic import BaseModel
from enum import Enum

# Difficulty section

class DifficultyLevel(Enum):
    easy = "Walk in the park"
    medium = "Wee bit of a challenge"
    hard = "Tough nut to crack"


# Score sort section

class ScoreSort(Enum):
    score_asc = "Ascending"
    score_dsc = "Descending"
    rdn = "Random"

# Master word section

class MasterWordBase(BaseModel):
    to_complete: str
    solution: str
    dialogue: str
    image_url: str


class MasterWordCreate(MasterWordBase):
    pass


class MasterWord(MasterWordBase):
    id: int

    class Config:
        orm_mode = True

# Jumbles section

class JumbleBase(BaseModel):
    pass


class JumbleCreate(JumbleBase):
    pass


class Jumble(JumbleBase):
    id: int
    master_word_id: int

    class Config:
        orm_mode = True


# Jumbles options section

class JumbleOptionBase(BaseModel):
    word: str
    score: int
    defs: str
    level: str


class JumbleOptionCreate(JumbleOptionBase):
    jumble_id: int


class JumbleOption(JumbleOptionBase):
    id: int
    master_word_id: int

    class Config:
        orm_mode = True
