import pandas as pd
from sqlalchemy.orm import Session

from jumble import crud, models
from jumble.database import SessionLocal

# Temp variables until populated for all master words
IMAGE_URL = 'https://storage.cloud.google.com/jumble-bucket/images/1.png'
DIALOGUE = """
Character 1: "Yo, did you see those dinos at the museum yesterday?"
Character 2: "They were so old, I can't even imagine how long they've been around for."
"""


def create_jumble_options(row_h: pd.Series):
    """Create jumble options from pd.Series"""
    new_jumble_option = dict(row_h[['word', 'score', 'defs', 'level', 'placeholder']])
    # make sure no comma seperate valeus exist in defs
    return models.JumbleOption(**new_jumble_option)


def create_master_word(row: pd.Series, df_hints: pd.DataFrame):
    """Create master words from pd.Series and using a DataFrame of options"""

    new_master = dict(row)
    new_master.pop('id')
    # add temp image and dialogue for now
    new_master.update({'image_url': IMAGE_URL, 'dialogue': DIALOGUE})
    new_master = models.MasterWord(**new_master)

    jumbles = []
    for _, df_h in df_hints[df_hints['master_id']==row['id']].groupby('hint'):
        new_jumble = models.Jumble()
        jumble_options = df_h.apply(
            lambda row: create_jumble_options(row), axis=1
            ).values.tolist()
        # assign jumble options to jumble
        new_jumble.jumble_options = jumble_options
        jumbles.append(new_jumble)
    # assign jumbles to master
    new_master.jumbles = jumbles

    return new_master


def create_master_words(
    df_masters: pd.DataFrame, df_options: pd.DataFrame, db: Session
    ):
    """create new master words from dataframes"""

    # generate list of all master words
    master_words = df_masters.apply(
    lambda row: create_master_word(row, df_hints=df_options), axis=1
    ).values.tolist()

    n_size = len(master_words)

    # check is master words exist
    existing_words = crud.read_master_words_by_solutions(
        db, solutions=[t.solution for t in master_words]
        )
    if len(existing_words) > 0:
        # handle update
        print(f'Found {len(existing_words)} in db, dropping ...')
        existing_solutions = [t.solution for t in master_words]
    else:
        existing_solutions = []

    # insert in db only new words
    pushed = [
        crud.create_master_word_orm(new_master_word=u, db=db)
        for u in master_words
        if u.solution not in existing_solutions
        ]

    print(f'Successfull insert of {len(pushed)}/{n_size} new rows!')
    return pushed



if __name__ == "__main__":

    # load material from csvs

    path_masters = '~/code/badrbmb/jumble/data/ideas_puns.csv'
    path_options = '~/code/badrbmb/jumble/data/hints.csv'

    df_masters = pd.read_csv(path_masters)
    df_options = pd.read_csv(path_options)

    # replace all delimiter `,`  by ;
    df_options['defs'] = df_options['defs'].replace(',', ';', regex=True)

    with SessionLocal() as db:
        new_words = create_master_words(
            df_masters=df_masters, df_options=df_options, db=db
            )
