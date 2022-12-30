from sqlalchemy.orm import Session
from sqlalchemy import func, select

from typing import List
from jumble import models, schemas


####### Master word section #######

def read_master_word(db: Session, master_word_id: int):
    """Function should query the db for the master word matching id"""
    return db.query(models.MasterWord).filter(
        models.MasterWord.id == master_word_id
        ).first()


def read_master_words(db: Session, skip: int = 0, limit: int = 100):
    """Function should return all master words with a skip and limit param"""
    return db.query(models.MasterWord).offset(skip).limit(limit).all()


def read_master_word_by_solution(db: Session, solution: str):
    """Function should query the db for the master word with a matching solution"""
    return db.query(models.MasterWord).filter(
        models.MasterWord.solution == solution
        ).first()


def read_master_words_by_solutions(db: Session, solutions: List[str]):
    """Function should query the db for the master word with a matching solutions"""
    return db.query(models.MasterWord).filter(
        models.MasterWord.solution in solutions
        ).all()


def create_master_word_orm(db: Session, new_master_word: models.MasterWord):
    """Function to create a new naster word with ORM in the database"""
    # add master word to db
    db.add(new_master_word)
    db.commit()
    db.refresh(new_master_word)
    return new_master_word


def create_master_word(db: Session, master_word: schemas.MasterWordCreate):
    """Function to create a new naster word in the database"""
    # add master word to db
    new_master_word = models.MasterWord(**master_word.dict())
    return create_master_word_orm(db=db, new_master_word=new_master_word)


####### Jumbles section #######


def read_jumble(db: Session, jumble_id: int):
    """Function should query the db for the jumble matching id"""
    return db.query(models.Jumble).filter(
        models.Jumble.id == jumble_id
        ).first()


def read_jumbles(db: Session, skip: int = 0, limit: int = 100):
    """Function should return all jumbles with a skip and limit param"""
    return db.query(models.Jumble).offset(skip).limit(limit).all()


def create_jumble(db: Session, jumble: schemas.JumbleCreate, master_word_id: int):
    """Function should create a jumble given a master word in the database"""
    # add tweet to db
    new_jumble = models.Jumble(**jumble.dict(), master_word_id=master_word_id)
    db.add(new_jumble)
    db.commit()
    db.refresh(new_jumble)
    return new_jumble


def read_master_word_jumbles(db: Session, master_word_id: int):
    """Function should return all the jumbles for a given master word"""

    # query the master word
    master_word = read_master_word(db, master_word_id=master_word_id)

    # make use of SQL Alchemy's master_word.jumbles sugar syntax
    if master_word is None:
        return None
    else:
        return master_word.jumbles


####### Jumble Option section #######


def create_jumble_option(
    db: Session, jumble_option: schemas.JumbleOptionCreate, jumble_id: int
    ):
    """Function should create a new jumble option in the database"""
    # add jumble option to db
    new_jumble_option = models.JumbleOption(
        **jumble_option.dict(), jumble_id=jumble_id
        )
    db.add(new_jumble_option)
    db.commit()
    db.refresh(new_jumble_option)
    return new_jumble_option


def read_jumble_options(db: Session, jumble_id: int):
    """
    Get the jumble options from a given master word"""
    # query the master word
    jumble = read_jumble(db, jumble_id=jumble_id)

    # make use of SQL Alchemy's sugar syntax
    if jumble is None:
        return None

    return jumble.jumble_options


def read_single_jumble_option(
    db: Session, jumble_id: int,
    level: schemas.DifficultyLevel,
    order: str = schemas.JumbleOptionScoreSort
    ):
    """
    Get one random jumble option from a jumble id and difficulty level
    """
    # query the master word
    jumble = read_jumble(db, jumble_id=jumble_id)

    # make use of SQL Alchemy's sugar syntax
    if jumble is None:
        return None

    query = select(jumble.jumble_options).where(
        models.JumbleOption.level == level.name
        )
    if order == schemas.JumbleOptionScoreSort.score_asc:
        return query.order_by(models.JumbleOption.score).first()
    if order == schemas.JumbleOptionScoreSort.score_dsc:
        return query.order_by(models.JumbleOption.score.desc()).first()
    else:
        # random order
        return query.order_by(func.random()).first()
