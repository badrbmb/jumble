import streamlit as st
from jumble.game import Game
from jumble import schemas


st.set_page_config(
    page_title="Joanimble",
    page_icon="random",
    layout="wide"
)

# define side bar
with st.sidebar:

    with st.expander(label="How to play?"):
        st.markdown(
            """
            The objective is to find the letters that are in the answer to the **given clue** at the bottom of the page
            - Start by unscramble the letters on the left, one letter to each square, to form ordinary words
            - Use the letters in shaded area to guess the missing part of the clue
            - You can refer to the **image** and the **dialogue** to help guess the missing part of the clue

            ❤️ ~Enjoy ❤️
            """
        )

    difficulty_level = st.radio(
        label='Too hard, or too easy for ya?\n\nChange difficulty level below:',
        options=[t.value for t in list(schemas.DifficultyLevel)],
        )

# define the game to play
game = Game(
    difficulty_level=schemas.DifficultyLevel(difficulty_level),
    to_exclude=[]
    )


# define main layout
st.markdown("![Joanimble](https://storage.googleapis.com/jumble-bucket/jumble-logo.png)")


col1, col2, col3 = st.columns([3, 3, 1])

with col1:

    st.write(game.jumbles)

with col2:
    st.write(game.image_url)

with col3:
    st.write(game.dialogue)

_, col2 = st.columns([3, 4])

with col2:
    st.write(game.to_complete)

st.write(game.solution)
