from copy import copy

import pandas as pd

class BattleshipBoard:
    def __init__(self, ship_sizes = [5, 4, 3, 3, 2], width=10, height=10):
        # Set a maximum board size (values larger than 676 will break the row labels)
        MAX_WIDTH, MAX_HEIGHT = 30, 30

        # Check if the board is too large
        if width > MAX_WIDTH or height > MAX_HEIGHT:
            raise ValueError(f"Board dimensions cannot exceed {MAX_WIDTH}x{MAX_HEIGHT}.")

        largest_ship_size = max(ship_sizes)
        if largest_ship_size > max(width, height):
            raise ValueError("Impossible board: A ship size is larger than the board's largest dimension.")
        # Check if all ship sizes are greater than or equal to 2
        if any(size < 2 for size in ship_sizes):
            raise ValueError("All ship sizes must be greater than or equal to 2.")
        if width < 2 or height < 2:
            raise ValueError("Board width and height must be greater than or equal to 2.")

        self.original_ship_sizes = copy(ship_sizes)
        self.ship_sizes = ship_sizes
        self.width = width
        self.height = height
        self.grid = [[' ' for _ in range(width)] for _ in range(height)]
        self.possibility_grid = [[0 for _ in range(width)] for _ in range(height)]
        self.sunken_ships = []
        self.played_positions = []

    def _apply_gradient(self, val):
        # Normalize the possibilities to get a gradient effect
        # Assumes possibility values are between 0 and some upper bound
        # Normalize based on the maximum value in the possibility grid
        max_val = max(max(row) for row in self.possibility_grid)
        if max_val > 0:  # Avoid division by zero
            normalized_val = val / max_val
        else:
            normalized_val = 0

        # Use a color palette from seaborn
        # This can be adjusted to any color palette of your choice
        color = f"background-color: rgba(0, 0, 255, {normalized_val});"
        if val == max_val:
            color += " font-weight: bold;"
        return color

    def _render_color(self, val):
        # Apply color styling for hits and misses
        if val == 'X':  # Hit
            return "color: green; font-weight: bold;"
        elif val == 'O':  # Miss
            return "color: red; font-weight: bold;"
        elif isinstance(val, int):  # Possibility values
            return self._apply_gradient(val)
        else:
            return ""

    def print_board(self, possibilities = False):
        def _fill_cell(grid, i, j, possibilities):
            return grid[i][j] if possibilities else '\u2022'

        if possibilities:
            self.calculate_possibilities()

        # Create a board for display with hits, misses, and possibility counts
        display_board = [
            [
                self.grid[i][j] if self.grid[i][j] in ['X', 'O']
                # else self.possibility_grid[i][j]
                else _fill_cell(self.possibility_grid, i, j, possibilities)
                for j in range(self.width)
            ]
            for i in range(self.height)
        ]

        # Create a proper index for rows, handling cases with more than 26 rows
        if self.height <= 26:
            row_labels = [chr(i + 65) for i in range(self.height)]
        else:
            row_labels = [f"{chr(65 + (i // 26) - 1)}{chr(65 + (i % 26))}" if i >= 26 else chr(65 + i) for i in range(self.height)]

        # Create a proper index for columns, handling cases with more than 10 columns
        column_labels = list(range(1, self.width + 1))

        # Create the DataFrame using the adjusted indices
        df = pd.DataFrame(display_board, index=row_labels, columns=column_labels)

        # Apply styling
        styled_df = df.style.map(self._render_color)
        return styled_df

    def mark_hit(self, row, col):
        row_index = ord(row.upper()) - 65
        col_index = col - 1

        # Check if this position has already been played
        if (row, col) in self.played_positions:
            raise ValueError(f"Position {row}{col} has already been played.")

        if self._is_valid_position(row_index, col_index):
            self.grid[row_index][col_index] = 'X'
            self.possibility_grid[row_index][col_index] = 0  # No possibilities where there's a hit
            self.played_positions.append((row, col))
        else:
            print(f"Invalid position. It must be within A-{chr(64 + self.height)} and 1-{self.width}.")

    def mark_miss(self, row, col):
        row_index = ord(row.upper()) - 65
        col_index = col - 1

        # Check if this position has already been played
        if (row, col) in self.played_positions:
            raise ValueError(f"Position {row}{col} has already been played.")

        if self._is_valid_position(row_index, col_index):
            self.grid[row_index][col_index] = 'O'
            self.possibility_grid[row_index][col_index] = 0  # No possibilities where there's a miss
            self.played_positions.append((row, col))
        else:
            print(f"Invalid position. It must be within A-{chr(64 + self.height)} and 1-{self.width}.")

    def undo_play(self, row, col):
        row_index = ord(row.upper()) - 65
        col_index = col - 1

        if (row, col) not in self.played_positions:
            raise ValueError(f"Position {row}{col} has not been played.")

        if self._is_valid_position(row_index, col_index):
            self.grid[row_index][col_index] = ' '
            self.played_positions.remove((row, col))
        else:
            print(f"Invalid position. It must be within A-{chr(64 + self.height)} and 1-{self.width}.")

    def unsink_ship(self, ship_size):
        """
        Unmark a ship as sunk and add the ship size back to the list.
        Then, recalculate the possibility grid.
        """
        # Add the ship size back to the ship_sizes list if it exists
        if ship_size not in self.original_ship_sizes:
            raise ValueError(f"No ship of size {ship_size} to unsink.")
        if ship_size in self.sunken_ships:
            self.sunken_ships.remove(ship_size)
            self.ship_sizes.append(ship_size)
        else:
            raise ValueError(f"No ship of size {ship_size} to unsink.")

    def _is_valid_position(self, row, col):
        return 0 <= row < self.height and 0 <= col < self.width

    def mark_ship_sunk(self, ship_size):
        """
        Mark a ship as sunk and remove the ship size from the list.
        Then, recalculate the possibility grid.
        """
        # Remove the ship size from the ship_sizes list if it exists
        print(f"Sinking ship of size {ship_size}.")
        if ship_size in self.ship_sizes:
            self.ship_sizes.remove(ship_size)
            self.sunken_ships.append(ship_size)
        else:
            # raise ValueError(f"No ship of size {ship_size} to sink.")
            print(f"No ship of size {ship_size} to sink.")

    def calculate_possibilities(self):
        # Reset possibility grid
        self.possibility_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

        for ship_size in self.ship_sizes:
            # Check horizontally
            for row in range(self.height):
                for col in range(self.width - ship_size + 1):
                    if all(self.grid[row][col + i] == ' ' for i in range(ship_size)):
                        for i in range(ship_size):
                            self.possibility_grid[row][col + i] += 1

            # Check vertically
            for col in range(self.width):
                for row in range(self.height - ship_size + 1):
                    if all(self.grid[row + i][col] == ' ' for i in range(ship_size)):
                        for i in range(ship_size):
                            self.possibility_grid[row + i][col] += 1

    def find_best_targets(self):
        max_possibility = 0
        best_targets = []

        # Iterate over the board to find the cell(s) with the highest possibility
        for row in range(self.height):
            for col in range(self.width):
                # We only consider cells that have not been hit or missed yet
                if self.grid[row][col] == ' ':
                    if self.possibility_grid[row][col] > max_possibility:
                        max_possibility = self.possibility_grid[row][col]
                        best_targets = [(self._index_to_label(row), col+1)]  # Reset the list with the new best target
                    elif self.possibility_grid[row][col] == max_possibility:
                        best_targets.append((self._index_to_label(row), col+1))  # Add the cell to the list of best targets

        return best_targets

    def _index_to_label(self, index):
        # This method converts an index to a row label
        if self.height <= 26:
            return chr(65 + index)
        else:
            # Handle row labels for boards with more than 26 rows
            return f"{chr(65 + (index // 26) - 1)}{chr(65 + (index % 26))}" if index >= 26 else chr(65 + index)
