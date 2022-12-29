"""
Gather all scripts to generate the materials for the game
Starting from a list of pun ideas:
- find the 4 hint words associated to a master word to guess
"""

import logging
import random
import re
from functools import lru_cache
from typing import List, Optional

import pandas as pd
import requests
from fuzzywuzzy import fuzz
from requests.exceptions import HTTPError
from tenacity import (RetryError, retry, retry_if_exception_type,
                      stop_after_attempt, wait_random)
from tqdm import tqdm

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DIFFICULTY_LEVELS = ['Tough nut to crack', 'Wee bit of a challenge', 'Walk in the park']
MAX_RETRY = 5
MIN_CANDIDATES = 3
MAX_WORDS = 1000
EXCLUDE_WORDS = [
    'surname', 'given name', 'acronym', 'initial', 'obsolete spelling',
    'abbreviation', 'archaic'
]

@retry(
    retry=retry_if_exception_type(HTTPError),
    stop=stop_after_attempt(5),
    wait=wait_random(0, 2)
)
@lru_cache()
def make_datamuse_request(hint: str, max_words: int =MAX_WORDS) -> dict:
    """Make request to Datamuse to query condidate words given a hint"""

    base_url = 'https://api.datamuse.com/words'
    code = '?sp='
    add_definition = 'md=d'
    max_words = f'max={max_words}'

    url = f"{base_url}{code}{hint}&{add_definition}&{max_words}"

    response = requests.get(url)

    response.raise_for_status()

    return response.json()


def get_hint_placeholder(hint_letters: str) -> str:
    """Returns the hint placeholder with disjoined letters to be sent to datamuse request"""

    hint = None
    while True:
        # get desired hint world lenght
        # if we pick 2 letters, return a 4 letter word, if we pick 3 letters, return a 5/6 letters words
        len_hint = random.randint(4, 5) \
            if len(hint_letters)==2 else random.randint(5, 7)

        # form placeholder word hint with provided letters and given length
        hint = ''.join(hint_letters)
        hint = list(hint.zfill(len_hint).replace('0', '?'))
        # reshuffle word hint
        random.shuffle(hint)
        # cast as string
        hint = ''.join(hint)
        # make sure all letters are disjoint
        cond = max([len(t) for t in hint.split('?')])
        if cond == 1:
            break
    return hint

@retry(
    retry=retry_if_exception_type(ValueError),
    stop=stop_after_attempt(MAX_RETRY)
)
def get_hint_word_candidates(
    hint_letters: str,
    min_candidates: int = MIN_CANDIDATES,
    verbose: bool = False
)-> pd.DataFrame:
    """Get hint words using the provided hint letters"""

    hint = get_hint_placeholder(hint_letters)

    if verbose:
        logger.info(f"""
        Looking for candidates with letters={hint}
        """)

    # get word candidates from data muse
    candidates = make_datamuse_request(hint)

    # process to apply diffuiculty level and find good candidate
    df = pd.DataFrame(candidates)
    # replace all Nans with None
    df = df.where(pd.notnull(df), None)
    # exclude given names
    # make sure definition is included
    if 'defs' not in df.columns:
        df['defs'] = None

    def _to_drop(x: Optional[list], exclude_words: List[str] = EXCLUDE_WORDS):
        """Decide to drop a given row given conditions"""
        # drop words without description
        if x is None:
            return True
        # exlude some specific cases out of scope
        cond = [any([i in t.lower() for t in x]) for i in exclude_words]
        return any(cond)


    df = df[~df['defs'].apply(lambda x: _to_drop(x))].copy()

    if len(df) < min_candidates:
        # retry another combination recursively
        raise ValueError(
            f"min number of candidates = {min_candidates} not reached!"
            )

    # assign difficulty bucket
    df['level'] = pd.qcut(df['score'], q=3,
                          labels=DIFFICULTY_LEVELS)

    # sample random world at chosen difficulty level
    return df


@retry(
    retry=retry_if_exception_type(RetryError),
    stop=stop_after_attempt(MAX_RETRY)
)
def get_all_hints(master_word: str, master_id: int, n_hints:List[int]) ->pd.DataFrame:
    """Get all possible hints for a given word"""
    try:
        # form 4 hint words
        shuffled_master = list(master_word)
        # shuffle letters
        random.shuffle(shuffled_master)


        df_all_hint_candidates = pd.DataFrame()
        for i, n in enumerate(n_hints):

            # pick n letters from the master word
            hint_letters = shuffled_master[:n]

            # get possible hint candidates
            df_candidates = get_hint_word_candidates(hint_letters)

            # assign hint number
            df_candidates['hint'] = i+1

            # store in df
            df_all_hint_candidates = pd.concat(
                [df_all_hint_candidates, df_candidates], axis=0
                )


            # drop letters from master
            shuffled_master = shuffled_master[len(hint_letters):]

    except RetryError:
        # bad luck with the shuffling, try another one
        logger.warning(f"Retry for {master_word}, {master_id}, {n_hints}")
        df_all_hint_candidates = get_all_hints(
            master_word=master_word,
            master_id=master_id,
            n_hints=n_hints
            )

    # assign master id
    df_all_hint_candidates['master_id'] = master_id

    return df_all_hint_candidates


def sanitize_hints(row) -> str:
    """Remove any mention of the hint word in defs"""
    hint_word = row['word']
    # convert definitions to string
    defs = '\n'.join([t.strip() for t in row['defs']])
    # remove mentions of hint word
    fuzz_match = set([
        re.sub("[^a-zA-Z]", ' ', u).strip()
        for u in defs.split(' ') if fuzz.token_sort_ratio(hint_word, u) > 70
    ])
    for m in fuzz_match:
        defs = defs.replace(m, '?'.ljust(len(hint_word), '?'))

    return defs

def generate_all_hints(df_puns: pd.DataFrame) ->pd.DataFrame:
    """get all hints for all master words"""

    df_all_hints = pd.DataFrame()

    for _, row in tqdm(df_puns.iterrows(), total=len(df_puns)):

        # get a given master word
        master_word = row['solution'].replace(' ', '')
        master_id = row['id']

        # get world count
        words_count = len(master_word)
        # get how many 2 letter hint words are needed
        n_hints = [2]*(words_count//2)
        if words_count%2 != 0:
            # last word need to be a 3 letter one to match all master letters
            n_hints[0] = 3

        try:
            # get associated hints
            df_hints = get_all_hints(
                master_word=master_word, master_id=master_id, n_hints=n_hints
                )
            # store in all df
            df_all_hints = pd.concat([df_all_hints, df_hints], axis=0)
        except Exception as e:
            logger.error(f'Failed getting hints for {master_word} with error {e}')

    # format hints
    df_all_hints['defs'] = df_all_hints.apply(lambda x: sanitize_hints(x), axis=1)

    return df_all_hints

if __name__ == "__main__":

    # get list of puns
    # change path to
    path = '~/code/badrbmb/jumble/data/ideas_puns.csv'
    df_puns = pd.read_csv(path)

    logger.info("Generate hints: START")

    df_all_hints = generate_all_hints(df_puns)

    # save hints to csv
    out_path = '~/code/badrbmb/jumble/data/hints.csv'
    df_all_hints.to_csv(out_path, index=0)

    logger.info("Generate hints: OVER")
