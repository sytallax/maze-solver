import random
from tkinter import Canvas, Tk
from typing import Optional


class Point:
    """A specific point on a Window identified by x, y
    coordinates. An `x` of 0 is the left of the Window and a `y` of 0 is
    the top of the Window."""

    def __init__(self, x: int = 0, y: int = 0) -> None:
        self.x = x
        self.y = y

    def __repr__(self) -> str:
        return f"Point(x={self.x}, y={self.y})"


class Line:
    """A connection between two Points."""

    def __init__(self, a: Point, b: Point) -> None:
        self.a = a
        self.b = b

    def draw(self, canvas: Canvas, fill_color: str) -> None:
        """Draw a line between two points (`a` and `b`) on the given
        canvas. The line color should be specified (ex: \"black\" or
        \"red\"."""

        canvas.create_line(
            self.a.x, self.a.y, self.b.x, self.b.y, fill=fill_color, width=2
        )


class Window:
    """The main GUI window, made by a TKinter widget."""

    def __init__(self, width: int, height: int) -> None:
        self.__root = Tk()
        self.__root.title("Window")

        self.canvas = Canvas(width=width, height=height)
        self.canvas.pack()

        self.is_window_running = False
        self.__root.protocol("WM_DELETE_WINDOW", self.close)

    def redraw(self) -> None:
        """Re-render the window's visuals"""
        self.__root.update_idletasks()
        self.__root.update()

    def wait_for_close(self) -> None:
        """Tell the window that it is running. Redraw the window
        indefinitely while it's running."""
        self.is_window_running = True
        while self.is_window_running:
            self.redraw()

    def close(self) -> None:
        """Set the running state of the window to False. A protocol
        defined at init deletes the window when called."""
        self.is_window_running = False

    def draw_line(self, line: Line, fill_color: str) -> None:
        """Draw a line of the given color on the Window."""
        line.draw(self.canvas, fill_color)


class Cell:
    """A Cell is the most atomic idea of our maze.

    Think of a cell like individual squares on a grid. Each cell can
    have up to 4 walls, places where you cannot go through. A path can
    move to an adjacent cell if there isn't a wall in the way.

    Cells do not have coordinates until they are drawn to our Window."""

    def __init__(
        self,
        window: Optional[Window] = None,
    ) -> None:
        self.has_left_wall = True
        self.has_right_wall = True
        self.has_top_wall = True
        self.has_bottom_wall = True
        self._x1: Optional[int] = None
        self._y1: Optional[int] = None
        self._x2: Optional[int] = None
        self._y2: Optional[int] = None
        self.visited = False
        self._win = window

    def draw(self, x1: int, y1: int, x2: int, y2: int) -> None:
        """Draw the cell with its walls on it's window."""
        if not self._win:
            return

        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

        left_wall = Line(Point(x1, y1), Point(x1, y2))
        if self.has_left_wall:
            self._win.draw_line(left_wall, "white")
        else:
            self._win.draw_line(left_wall, "#2c2c2e")

        right_wall = Line(Point(x2, y1), Point(x2, y2))
        if self.has_right_wall:
            self._win.draw_line(right_wall, "white")
        else:
            self._win.draw_line(right_wall, "#2c2c2e")

        top_wall: Line = Line(Point(x1, y1), Point(x2, y1))
        if self.has_top_wall:
            self._win.draw_line(top_wall, "white")
        else:
            self._win.draw_line(top_wall, "#2c2c2e")

        bottom_wall = Line(Point(x1, y2), Point(x2, y2))
        if self.has_bottom_wall:
            self._win.draw_line(bottom_wall, "white")
        else:
            self._win.draw_line(bottom_wall, "#2c2c2e")

    def draw_move(self, to_cell: "Cell", undo: bool = False) -> None:
        """Draw a line from the center of this Cell to the center of
        the given cell. The `undo` flag changes the color of the line
        from red to gray."""
        if not self._win:
            return

        if not self._x1 or not self._x2 or not self._y1 or not self._y2:
            raise ValueError("cell has no coordinates")
        if not to_cell._x1 or not to_cell._x2 or not to_cell._y1 or not to_cell._y2:
            raise ValueError("cell has no coordinates")

        self_half_length = abs(self._x2 - self._x1) // 2
        self_x_center = self_half_length + self._x1
        self_y_center = self_half_length + self._y1

        to_half_length = abs(to_cell._x2 - to_cell._x1) // 2
        to_x_center = to_half_length + to_cell._x1
        to_y_center = to_half_length + to_cell._y1

        if undo:
            fill_color = "gray"
        else:
            fill_color = "red"

        move_line = Line(
            Point(self_x_center, self_y_center), Point(to_x_center, to_y_center)
        )
        self._win.draw_line(move_line, fill_color)


class Maze:
    """A 2-dimensional grid of Cells that represents a maze."""

    def __init__(
        self,
        x1: int,
        y1: int,
        num_rows: int,
        num_cols: int,
        cell_size_x: int,
        cell_size_y: int,
        win: Optional[Window] = None,
    ) -> None:
        self.x1 = x1
        self.y1 = y1
        self.num_rows = num_rows
        self.num_cols = num_cols
        self.cell_size_x = cell_size_x
        self.cell_size_y = cell_size_y
        self.win = win
        self._create_cells()

    def _create_cells(self) -> None:
        """Create a matrix of `self.num_cols` length and `self.num_rows`
        width and populate it with Cell objects. The Cells are created
        up to down, column by column."""

        self._cells: list[list[Cell]] = [
            [] * self.num_rows for _ in range(self.num_cols)
        ]
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                self._cells[col].append(Cell(self.win))
                self._draw_cell(col, row)

        self._break_entrance_and_exit()
        self._break_walls_r(self.num_cols // 2, self.num_rows // 2)
        self._reset_cells_visited()

    def _draw_cell(
        self,
        col: int,
        row: int,
    ) -> None:
        """Draw the cell at the given matrix indices. Coordinates are
        calculated from the cell_size properties."""
        x1 = self.x1 + (self.cell_size_x * col)
        y1 = self.y1 + (self.cell_size_y * row)

        x2 = x1 + self.cell_size_x
        y2 = y1 + self.cell_size_y

        self._cells[col][row].draw(x1, y1, x2, y2)
        self._animate()

    def _animate(self) -> None:
        """After each cell is created with `self._draw_cell`, the Window
        will be redrawn to visualize the creation of the Maze."""
        if self.win is not None:
            self.win.redraw()

    def _break_wall(self, col: int, row: int, wall: str) -> None:
        """Remove the specified wall from the Cell and redraw it."""
        if wall == "top":
            self._cells[col][row].has_top_wall = False
        elif wall == "bottom":
            self._cells[col][row].has_bottom_wall = False
        elif wall == "left":
            self._cells[col][row].has_left_wall = False
        elif wall == "right":
            self._cells[col][row].has_right_wall = False

        self._draw_cell(col, row)

    def _break_entrance_and_exit(self) -> None:
        """Remove the left wall from the entrance cell and remove the
        right wall from the exit cell."""
        self._break_wall(0, 0, "left")
        self._break_wall(self.num_cols - 1, self.num_rows - 1, "right")

    def _break_walls_r(self, col: int, row: int) -> None:
        """Recursively and randomly break one wall from each cell."""
        self._cells[col][row].visited = True

        while True:
            possible_cells_to_visit: list[tuple[int, int]] = []
            if col - 1 >= 0 and self._cells[col - 1][row].visited is False:
                possible_cells_to_visit.append((col - 1, row))

            if col + 1 < self.num_cols and self._cells[col + 1][row].visited is False:
                possible_cells_to_visit.append((col + 1, row))

            if row - 1 >= 0 and self._cells[col][row - 1].visited is False:
                possible_cells_to_visit.append((col, row - 1))

            if row + 1 < self.num_rows and self._cells[col][row + 1].visited is False:
                possible_cells_to_visit.append((col, row + 1))

            if len(possible_cells_to_visit) == 0:
                return

            next_col, next_row = random.choice(possible_cells_to_visit)

            if col < next_col:
                self._break_wall(col, row, "right")
                self._break_wall(next_col, next_row, "left")

            if col > next_col:
                self._break_wall(col, row, "left")
                self._break_wall(next_col, next_row, "right")

            if row < next_row:
                self._break_wall(col, row, "bottom")
                self._break_wall(next_col, next_row, "top")

            if row > next_row:
                self._break_wall(col, row, "top")
                self._break_wall(next_col, next_row, "bottom")

            self._break_walls_r(next_col, next_row)

    def _reset_cells_visited(self) -> None:
        """After all cells have been visited by `self._break_walls_r`,
        reset all Cell's visited properties to False."""
        for col in range(self.num_cols):
            for row in range(self.num_rows):
                self._cells[col][row].visited = False

    def solve(self) -> bool:
        """Solve the maze!"""
        return self._solve_r(col=0, row=0)

    def _solve_r(self, col: int, row: int) -> bool:
        """Recursively travel through the maze and find the exit without
        running into walls."""

        self._animate()
        current_cell = self._cells[col][row]
        current_cell.visited = True
        if col == (self.num_cols - 1) and row == (self.num_rows - 1):
            return True

        possible_cells_to_visit: list[tuple[int, int]] = []

        if col - 1 >= 0 and self._cells[col - 1][row].visited is False:
            possible_cells_to_visit.append((col - 1, row))

        if col + 1 < self.num_cols and self._cells[col + 1][row].visited is False:
            possible_cells_to_visit.append((col + 1, row))

        if row - 1 >= 0 and self._cells[col][row - 1].visited is False:
            possible_cells_to_visit.append((col, row - 1))

        if row + 1 < self.num_rows and self._cells[col][row + 1].visited is False:
            possible_cells_to_visit.append((col, row + 1))

        if len(possible_cells_to_visit) == 0:
            return False

        for next_col, next_row in possible_cells_to_visit:
            next_cell = self._cells[next_col][next_row]

            if col < next_col and (
                not current_cell.has_right_wall and not next_cell.has_left_wall
            ):
                current_cell.draw_move(next_cell)
                if self._solve_r(next_col, next_row):
                    return True
                current_cell.draw_move(next_cell, undo=True)

            if col > next_col and (
                not current_cell.has_left_wall and not next_cell.has_right_wall
            ):
                current_cell.draw_move(next_cell)
                if self._solve_r(next_col, next_row):
                    return True
                current_cell.draw_move(next_cell, undo=True)

            if row < next_row and (
                not current_cell.has_bottom_wall and not next_cell.has_top_wall
            ):
                current_cell.draw_move(next_cell)
                if self._solve_r(next_col, next_row):
                    return True
                current_cell.draw_move(next_cell, undo=True)
                
            if row > next_row and (
                not current_cell.has_top_wall and not next_cell.has_bottom_wall
            ):
                current_cell.draw_move(next_cell)
                if self._solve_r(next_col, next_row):
                    return True
                current_cell.draw_move(next_cell, undo=True)

        return False


def main() -> None:
    win = Window(800, 600)
    maze = Maze(50, 50, 10, 14, 50, 50, win=win)
    maze.solve()
    win.wait_for_close()


if __name__ == "__main__":
    main()
