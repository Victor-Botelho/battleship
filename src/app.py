import streamlit as st
from game import BattleshipBoard


AUTHOR_URL = 'https://github.com/Victor-Botelho/'
REPO_URL = 'https://github.com/Victor-Botelho/battleship'
GITHUB_LOGO_URL = 'https://github.githubassets.com/images/modules/logos_page/GitHub-Mark.png'


def sanitize_ship_sizes_input(input: str):
    return [int(x.strip()) for x in input.split(',')]

def get_grid_position(input: str):
    # Converts grid position from string (e.g., "A7") to format ("A", 7)
    row = input[0].upper()
    col = int(input[1:])
    return row, col



# Initialize the game board only once
if 'board' not in st.session_state:
    # Create a placeholder object, which will be replaced by the actual BattleshipBoard instance
    st.session_state.board = None

# Title of the app
st.title('Battleship strategizer')
st.warning('This is a work in progress. Please report any issues through the GitHub repository. To deal with errors raised, simply change some widget value to trigger a re-run.')

# A simple text
st.write('Hello! This project should help you to strategize your battleship game. It optimizes the placement of your torpedos to sink the enemy ships as fast as possible. This was inspired by Digital Genius\' [video on YouTube](https://www.youtube.com/watch?v=8FctDuTfcO8).')

st.header('Board configuration')
st.write('Let\'s start by passing the game board size and the number of ships in the game.')

# Create columns for game configuration inputs
col1, col2, col3 = st.columns(3)

width = col1.number_input('Game board width', value=10)
height = col2.number_input('Game board height', value=10)
ship_sizes_input = col3.text_input('Ship sizes (separated by commas)', value='5, 4, 3, 3, 2')
ship_sizes = sanitize_ship_sizes_input(ship_sizes_input)

# Initialize the BattleshipBoard object once with the user's configuration
if st.button('Initialize Board'):
    st.session_state.board = BattleshipBoard(
        ship_sizes=ship_sizes, width=width, height=height)
    st.warning(f'Your game board is a grid of size {width}x{height}. Your ships have the following sizes: {ship_sizes}.')

st.header('Play the game')

# Check if the board has been initialized
if st.session_state.board is not None:
    board = st.session_state.board
    # Input for the latest torpedo launch
    # st.write('Now, input the result of your latest torpedo launch.')
    action = st.radio('What will be your next action?', ('Launch a torpedo', 'Mark a ship as sunk'))

    # col1, col2, col3 = st.columns(3)
    if action == 'Launch a torpedo':
        position_input = st.text_input('Torpedo grid position (e.g., "A7")')
        is_hit = st.checkbox('IT\'S A HIT! 💥')
    if action == 'Mark a ship as sunk':
        ship_sunk = st.number_input('Ship sunk (input ship size if sunk, leave as 0 if not)', min_value=0, value=0, step=1)

    # Action button to submit the play
    if st.button('Submit Play'):
        if action == 'Launch a torpedo':
            message = f'You launched a torpedo at position {position_input}.'
            row, col = get_grid_position(position_input)
            if is_hit:
                board.mark_hit(row, col)
                message += ' It\'s a hit! 💥'
            else:
                board.mark_miss(row, col)
                message += ' It\'s a miss! 🌊'
            st.warning(message)
        if action == 'Mark a ship as sunk':
            if ship_sunk > 0:
                board.mark_ship_sunk(ship_sunk)
                st.warning(f'Congratulations! You sunk a ship of size {ship_sunk}! 🚢')

    col1, col2 = st.columns(2)

    # Create an expander widget
    with col1.expander('Game state'):
        st.write(f'Ships floating: {board.ship_sizes}')
        st.write(f'Ships sunk: {board.sunken_ships}')
        pretty_played_positions = [f'{x[0]}{x[1]}' for x in board.played_positions]
        st.write(f'Played positions: {pretty_played_positions}')
    with col2.expander('More options'):
        more_options = st.radio('What to do?', ('Undo a play', 'Unsink ship'))
        if more_options == 'Undo a play':
            undo_position = st.text_input('Position to undo (e.g., "A7")')
            if st.button('Undo play'):
                row, col = get_grid_position(undo_position)
                board.undo_play(row, col)
        if more_options == 'Unsink ship':
            unsink_ship_size = st.number_input('Ship size to unsink', min_value=0, value=0, step=1)
            if st.button('Unsink ship'):
                board.unsink_ship(unsink_ship_size)


    # Display the current state of the board
    display_possibilities = st.checkbox('Display probabilities')
    best_targets = board.find_best_targets()
    best_targets_strings = [f"{target[0]}{target[1]}" for target in best_targets]
    if display_possibilities:
        st.write(f'Best targets: {best_targets_strings}')
    st.dataframe(board.print_board(possibilities=display_possibilities))
else:
    st.write('Please initialize the game board with the "Initialize Board" button above.')


st.markdown(f'[Source code]({REPO_URL}) | Nov 2023 | [Victor Botelho]()')
