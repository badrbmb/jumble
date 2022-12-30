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
    st.write('# Choose a difficulty level:')

    difficulty_level = st.radio(
        label='Choose a difficulty level:',
        options=list(schemas.DifficultyLevel),
        )

# define the game to play
game = Game(
    difficulty_level=schemas.DifficultyLevel(difficulty_level),
    to_exclude=[]
    )


# define main layout
st.write('# Joanimble')

col1, col2, col3 = st.columns([3, 3, 1])

with col1:
    st.write("Unscramble these letters, one letter ot each square, to form ordinary words")

    st.write(game.jumbles)

with col2:
    st.write(game.image_url)

with col3:
    st.write(game.dialogue)

_, col2 = st.columns([3, 4])

with col2:
    st.write(game.to_complete)

st.write(game.solution)
