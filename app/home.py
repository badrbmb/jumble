import streamlit as st
import streamlit_nested_layout
from PIL import Image
import requests
from io import BytesIO
from dataclasses import dataclass, asdict

from jumble import schemas
from jumble.game import Game

st.set_page_config(
    page_title="Joanimble",
    page_icon="random",
    layout="wide"
)

COLOR_DICT = {
    'correct': '#02d622',
    'missing': '#b5a904',
    'wrong': '#fc0303'
}


class Dict2Class(object):
    """Helper class to convert dict to class object"""
    def __init__(self, my_dict: dict):
        for key in my_dict:
            setattr(self, key, my_dict[key])

    def to_dict(self):
        return {key: value for key, value in self.__dict__.items()}


# Initialization of master word
if 'saved_game' not in st.session_state:
    st.session_state['saved_game'] = None

# Initialization of master word
if 'saved_difficulty' not in st.session_state:
    st.session_state['saved_difficulty'] = None

if 'to_exlude' not in st.session_state:
    st.session_state['to_exlude'] = []

if "reload" not in st.session_state:
    st.session_state['reload'] = False


def reset_values():
    # set saved game to None to force refresh
    st.session_state['saved_game'] = None


def load_game():
    if st.session_state['saved_game'] is None:
        game = Game(
            difficulty_level=schemas.DifficultyLevel(difficulty_level),
            # keep track of games to exclude
            to_exclude=st.session_state['to_exlude']
            )
    else:
        # load game from saved game
        game = Dict2Class(st.session_state['saved_game'])

    return game


def get_letter_status(input_letter, true_letter):
    if input_letter == '':
        return 'missing'
    else:
        if input_letter.lower() == true_letter.lower():
            return 'correct'
        else:
            return 'wrong'


def highlight_letter(color):
    st.markdown(
        f"""<hr style="height:5px;border:none;color:{color};background-color:{color};" /> """,
        unsafe_allow_html=True
        )


def load_image(url):
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def get_letter(idx, list_letters):
    try:
        return list_letters[idx]
    except IndexError:
        return '?'


def get_column_length(i, max_i):
    if i == max_i:
        return 2
    else:
        return 1

# define side bar
with st.sidebar:
    difficulty_level = st.radio(
        label='Too hard, or too easy for ya?\n\nChange difficulty level below:',
        options=[t.value for t in list(schemas.DifficultyLevel)],
        on_change=reset_values
        )
    # update difficulty level
    reload = difficulty_level != st.session_state['saved_difficulty']
    st.session_state['saved_difficulty'] = difficulty_level

    st.write('#')
    st.write('#')

    # option to reload
    play_again = st.button(label='Another round ?', on_click=reset_values)


# define the game to play
game = load_game()

# save in st.session_state
st.session_state['saved_game'] = game.to_dict()


if game.game_id is None:

    st.info("""
            Congratulations, you've exhausted all your available games!\n\n
            Reach out to your game admin. to have him prepare more for you 😘
            """)

else:

    # define main layout
    _, col2, _ = st.columns([1, 3, 1])
    with col2:
        st.markdown("![Joanimble](https://storage.googleapis.com/jumble-bucket/jumble-logo.png)")
        with st.expander(label="How to play?"):
            st.markdown(
                """
                The objective is to find the letters that are in the answer to the **given clue** at the bottom of the page
                - Start by unscramble the letters on the left, one letter to each square, to form ordinary words
                - Use the letters in with a shaded bar to guess the missing part of the clue
                - Click on **Check my jumbles** to see if you got the right letters:
                    - the shaded bar under each letter will indicate if it's the right one!
                    - your correct letters are automatically reported under **My correctly guessed letters** on the right.
                - You can refer to the **image** and the **dialogue** to help guess the missing part of the clue.
                ~Enjoy 😊
                """
            )


    col1, col2 = st.columns([2, 3])

    # fill jumbles data
    with col1:

        form_jumbles = st.form(
            key='jumbles-form',
            )

        # list to store correct letters
        correct_letters = []

        with form_jumbles:
            # get the max column number based on lenght of jumbles
            max_inner_cols = max([len(u['placeholder']) for u in game.jumbles.values()])

            for jumble_id, data in game.jumbles.items():
                st.text_input(
                    disabled=True,
                    label='-',
                    value=''.join(data['shuffled']).upper(),
                    key=jumble_id,
                    help=data['hint']
                    )
                # display letters to fill
                inner_cols = st.columns([1]*max_inner_cols)
                for i, letter in enumerate(data['placeholder']):
                    inner_col = inner_cols[i]
                    with inner_col:
                        input_letter = st.text_input(
                            label="-",
                            value='',
                            key=f"{jumble_id}_{i}",
                            max_chars=1,
                            )
                        letter_status = get_letter_status(
                            input_letter=input_letter,
                            true_letter=data['solution'][i]
                            )
                        if letter != '?':
                            highlight_letter(COLOR_DICT[letter_status])
                            if letter_status == "correct":
                                # add to correct letters
                                correct_letters.append(input_letter)

            st.write('#')
            submit = st.form_submit_button(
                label='Check my jumbles!',
                )

    # reduce gap in jumbles column
    st.markdown("""
                <style>
                [data-testid=column]:nth-of-type(1) [data-testid=stVerticalBlock]{
                    gap: 0rem;
                }
                </style>
                """,unsafe_allow_html=True
                )

    # fill image
    with col2:

        st.write('#')
        st.write('#')
        st.write('#')

        st.warning(game.dialogue.replace('Character', '\n\nCharacter'))

        url = 'https://storage.googleapis.com/jumble-bucket/images/1.png'

        _, inner_col1, _ = st.columns([1, 2, 1])
        with inner_col1:
            st.image(load_image(url), width=300)

        st.markdown("____")

        st.info(game.to_complete.replace('---', '...'))

        st.write('#')

        form_solution = st.form(
            key='form-solution',
            )

        with form_solution:
            # make sure each word in the solution clue is separate
            solution_parts = game.solution.split(' ')
            word_lenghts = [len(t) for t in solution_parts]

            inner_cols = st.columns([1]*len(solution_parts))
            user_solution = []
            for i, part_solution in enumerate(solution_parts):
                with inner_cols[i]:
                    user_input = st.text_input(
                        label='-',
                        key=f"solution-part-{i}",
                        max_chars=len(part_solution)
                    )
                    user_solution.append(user_input)

            submit_solution = form_solution.form_submit_button('Submit!')

        # display recap. of correclty found letters
        st.write("My correctly guessed letters: ")
        placeholder_letters = len(game.solution.replace(' ', ''))
        inner_cols = st.columns([1]*placeholder_letters)
        for i in range(placeholder_letters):
            value = get_letter(i, correct_letters)
            with inner_cols[i]:
                # try fetching
                letters_found = st.text_input(
                    label = '-',
                    value=value.upper(),
                    disabled=True,
                    key=f'placeholder-{i}'
                )

        if submit_solution:
            # check submission against solution
            user_solution = ' '.join([t.strip().lower() for t in user_solution])

            if user_solution == game.solution.lower():
                st.balloons()
                st.success('You rock!', icon='🙌')
                # update game id
                # save this party as done
                saved_games = st.session_state['to_exlude']
                saved_games.append(game.game_id)
                st.session_state['to_exlude'] = list(set(saved_games))
                # option to reload
                play_again = st.button(
                    label='Another round ?',
                    on_click=reset_values,
                    key='reset-after-success'
                    )
            else:
                st.error("Not the expected answer I'm afraid ... try again 💪!")
