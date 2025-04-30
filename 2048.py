"""
Created on Oct 16 17:51:54 2022

@author: Erqian Chen
"""

import tkinter as tk
from tkinter import messagebox, filedialog
from typing import Optional, List, Tuple

# You may import any submodules of tkinter here if you wish
# You may also import anything from the typing module
# All other additional imports will result in a deduction of up to 100% of your A3 mark

from Game2048_support import *


def combine_right(tiles):
    """
    Merge tiles forward right, the implement is call the combine_left and reverse
    note it is deep copy for tiles paramer, so it does not change tiles value.
    param tiles: represent all tiles.
    """
    tiles = reverse(tiles)
    tiles, score_added = combine_left(tiles)
    return reverse(tiles), score_added


def combine_up(tiles):
    """
    Merge tiles forward up, the implement is call the combine_left and reverse
    note it is deep copy for tiles paramer, so it does not change tiles value.
    param tiles: represent all tiles.
    """
    tiles = transpose(tiles)
    tiles, score_added = combine_left(tiles)
    return transpose(tiles), score_added


def combine_down(tiles):
    """
    Merge tiles forward down, the implement is call the combine_right and reverse
    note it is deep copy for tiles paramer, so it does not change tiles value.
    param tiles: represent all tiles
    """
    tiles = transpose(tiles)
    tiles, score_added = combine_right(tiles)
    return transpose(tiles), score_added


def stack_right(tiles):
    """
    Move current tiles forward right only one step
    note it is deep copy for tiles paramer, so it does not change tiles value.
    param tiles: represent all tiles.
    """
    return reverse(stack_left(reverse(tiles)))


def stack_up(tiles):
    """
    Move current tiles forward up only one step
    note it is deep copy for tiles paramer, so it does not change tiles value.
    param tiles: represent all tiles.
    """
    return transpose(stack_left(transpose(tiles)))


def stack_down(tiles):
    """
    move current tiles forward down only one step
    note it is deep copy for tiles paramer, so it does not change tiles value.
    param tiles: represent all tiles.
    """
    return transpose(stack_right(transpose(tiles)))


# Write your classes here
class Model:
    """
    The game's the main function is :
    tiles move, tiles merge, and decide current tiles is win or lost.
    In addition, load game and save game is implement is here.
    """

    def __init__(self):
        """
        Constructs a new 2048 model instance. This includes setting up a new game 
        """
        self.new_game()

    def new_game(self):
        """
        Sets, or resets, the game state to an initial game state. Any information is set to its initial
        state, the tiles are all set to empty, and then two new starter tiles are randomly generated.
        """
        self.tiles = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self.add_tile()
        self.add_tile()
        self.remain_num = MAX_UNDOS

        self.score = [0]
        self.all_move_tiles = [self.tiles]

    def get_score(self) -> int:
        """return current tiles scores"""
        return self.score[-1]

    def get_undos_remaining(self) -> int:
        """return current game undo times"""
        return self.remain_num

    def use_undo(self) -> None:
        """
        execute undo , if undo times is 0, or current state is started state, do nothing
        else change current tiles and score using last time tiles and score.
        """
        print("current tiles numbers = ", len(self.all_move_tiles))
        if self.remain_num <= 0:
            return
        if len(self.all_move_tiles) == 1:
            return
        self.all_move_tiles.pop(-1)
        self.tiles = self.all_move_tiles[-1]
        self.score.pop(-1)
        self.remain_num -= 1

    def get_tiles(self) -> List[List[Optional[int]]]:
        """
        Return the current tiles matrix. Each internal list represents a row of the grid, ordered from
        top to bottom. Each item in each row list is the integer value on the tile occupying that
        space, or None if no tile is occupying that space.     
        """
        return self.tiles

    def add_tile(self) -> None:
        """
        Randomly generate a new tile at an empty location and
        add it to the current tiles matrix.
        
        """
        pos, val = generate_tile(self.tiles)
        self.tiles[pos[0]][pos[1]] = val

    def move_left(self) -> None:
        """
        Moves all tiles to their left extreme, merging where necessary. This involves stacking all tiles
        to the left, merging to the left, and then restacking to the left to fill in any gaps created. If
        you are keeping track of a score, this method should also add any points gained
        from the move to the total score.
        
        In other words this function do four things
        1. move left current tiles until state does not change.
        2. merge current tiles, and calculate this step score.
        3. continue move left, until state does not change.
        4. add this move's score into game model.
        """
        self.tiles = self.__stack_left(self.tiles)
        self.tiles, score = self.__combine_left(self.tiles)
        self.tiles = self.__stack_left(self.tiles)
        self.score.append(self.score[-1] + score)

    def move_right(self) -> None:
        """
        Moves all tiles to their right extreme, merging where necessary. 
        This can be achieved by reversing the tiles matrix, moving left, 
        and then reversing the matrix again. If you are keeping track of 
        a score , this method should also result in gained points being 
        added to the total score.
        """
        self.tiles = self.__stack_right(self.tiles)
        self.tiles, score = self.__combine_right(self.tiles)
        self.tiles = self.__stack_right(self.tiles)
        self.score.append(self.score[-1] + score)

    def move_up(self) -> None:
        """
        Moves all tiles to their top extreme, merging where necessary. This can be achieved by
        transposing the tiles matrix, moving left, and then transposing the matrix again. If you are
        keeping track of a score, this method should also result in gained points being
        added to the total score.
        """
        self.tiles = self.__stack_up(self.tiles)
        self.tiles, score = self.__combine_up(self.tiles)
        self.tiles = self.__stack_up(self.tiles)
        self.score.append(self.score[-1] + score)

    def move_down(self) -> None:
        """
         Moves all tiles to their bottom extreme, merging where necessary. This can be achieved by
         transposing the tiles matrix, moving right, and then transposing the matrix again. If you
         are keeping track of a score, this method should also result in gained points
         being added to the total score.
        """
        self.tiles = self.__stack_down(self.tiles)
        self.tiles, score = self.__combine_down(self.tiles)
        self.tiles = self.__stack_down(self.tiles)
        self.score.append(self.score[-1] + score)

    def attempt_move(self, move: str) -> bool:
        """
        Makes the appropriate move according to the move string provided. Returns True if the
        move resulted in a change to the game state, else False. The move provided must be one
        of wasd (this is a pre-condition, not something that must be handled within this method).
        """
        back = self.tiles
        if move == LEFT:
            self.move_left()
        elif move == UP:
            self.move_up()
        elif move == DOWN:
            self.move_down()
        elif move == RIGHT:
            self.move_right()
        else:
            return False

        self.all_move_tiles.append(self.tiles)
        print("current tiles : ", len(self.all_move_tiles))
        return back != self.tiles

    def has_won(self) -> bool:
        """
        Returns True if the game has been won, else False. The game has been won if a 2048 tile
        exists on the grid.
        """
        for tile in self.tiles:
            if 2048 in tile:
                return True
        return False

    def has_lost(self) -> bool:
        """
        Returns True if the game has been lost, else False. The game has been lost if there are
        no remaining empty places in the grid, but no move would result in a change to the game
        state.
        """
        for tile in self.tiles:
            if None in tile:
                return False
        
        back = self.tiles
        if self.__combine_left(back)[1] != 0 or \
                self.__combine_right(back)[1] != 0 or \
                self.__combine_up(back)[1] != 0 or \
                self.__combine_down(back)[1] != 0:
            return False
        return True

    def __combine_left(self, tiles):
        """
        Call a3_support combine_left. The move will mix two tiles together.
        """
        return combine_left(tiles)

    def __combine_right(self, tiles):
        """
        Call a3_support combine_left and reverse. The move will mix two tiles together.
        """
        tiles, score_added = combine_left(reverse(tiles))
        return reverse(tiles), score_added

    def __combine_up(self, tiles):
        """
        Call a3_support combine_left and transpose. The move will mix two tiles together.
        """
        tiles, score_added = combine_left(transpose(tiles))
        return transpose(tiles), score_added

    def __combine_down(self, tiles):
        """
        Call combine_right and transpose. The move will mix two tiles together.
        """
        tiles, score_added = combine_right(transpose(tiles))
        return transpose(tiles), score_added

    def __stack_left(self, tiles):
        """
        Call a3_support stack_left. The move will move left if it can.
        """
        back = stack_left(tiles)
        if back == tiles:
            return back
        else:
            return self.__stack_left(back)

    def __stack_right(self, tiles):
        """
        Call a3_support stack_left and reverse. The move will move right if it can.
        """
        back = reverse(stack_left(reverse(tiles)))
        if back == tiles:
            return back
        else:
            return self.__stack_right(back)

    def __stack_up(self, tiles):
        """
        Call a3_support stack_left and transpose. The move will move up if it can.
        """
        back = transpose(stack_left(transpose(tiles)))
        if back == tiles:
            return back
        else:
            return self.__stack_up(back)

    def __stack_down(self, tiles):
        """
        Call stack_right and transpose. The move will move down if it can.
        """
        back = transpose(stack_right(transpose(tiles)))
        if back == tiles:
            return back
        else:
            return self.__stack_down(back)

    def save_game(self, filename):
        """
        save the game into file.
        the saved content include all move step, score, undo times, is written file.
        In addition, first line and second line is not game content, it is used to secret current file.
        when load file, if first line and second line is equal to secret key, then it is the game file.    
        """
        fp = open(filename, 'w')
        fp.write("!@#$%^&*()\n")
        fp.write("!@#$%^&*()\n")

        fp.write(str(self.remain_num) + "\n")
        for (score, tiles) in zip(self.score, self.all_move_tiles):
            fp.write(str(score) + '\n')

            for tile in tiles:
                for i in tile:
                    fp.write(str(i) + " ")

            fp.write("\n")

        fp.close()

    def load_game(self, filename):
        """
        Load game model from file from saved before.
        First check fist line and second line, if it is not secret key, it is not game file, return False.
        Next line is undo times.
        Next line is score and this tiles, and so on.
        """
        self.all_move_tiles.clear()
        self.score.clear()
        try:
            fp = open(filename, 'r')

            first = fp.readline()
            if first != "!@#$%^&*()\n":
                fp.close()
                return False

            second = fp.readline()
            if second != "!@#$%^&*()\n":
                fp.close()
                return False

            self.remain_num = int(fp.readline())
            all_contents = fp.readlines()
            for i in range(0, len(all_contents), 2):
                score = int(all_contents[i])
                tiles = self.convert_list(all_contents[i + 1])
                self.score.append(score)
                self.all_move_tiles.append(tiles)

            fp.close()

            self.tiles = self.all_move_tiles[-1]

            return True
        except FileNotFoundError:
            return False

    def convert_list(self, line):
        """
        Represent a tiles.
        return two dimension list, it represent current tiles.
        """
        tilestr = line.split(" ")
        tiles = []
        k = 0
        for i in range(NUM_ROWS):
            tmp = []
            for j in range(NUM_COLS):
                if tilestr[k] == "None":
                    tmp.append(None)
                else:
                    tmp.append(int(tilestr[k]))
                k += 1
            tiles.append(tmp)
        return tiles


class GameGrid(tk.Canvas):
    """
    the game implement as MVC pattern, this class is view, represent game view.
    """

    def __init__(self, master: tk.Tk, **kwargs) -> None:
        """
        game view ctor function, setting the title for game and create_rectangle as tile view.
        """
        super().__init__(master=master, width=BOARD_WIDTH, height=BOARD_HEIGHT,
                         background=BACKGROUND_COLOUR)

        self.tile_size = (BOARD_WIDTH - (NUM_ROWS + 1) * BUFFER) / NUM_ROWS
        master.title("CSSE1001/7030 2022 Semester 2 A3")
        master.resizable(width=True, height=True)

        self.grid = [[None for _ in range(NUM_COLS)] for _ in range(NUM_ROWS)]
        self.pack()

    def _get_bbox(self, position: Tuple[int, int]) -> Tuple[int, int, int, int]:
        """
        Return the bounding box for the (row, column) position, in the form.
        """
        midx, midy = self._get_midpoint(position)
        return int(midx - self.tile_size / 2), int(midy - self.tile_size / 2), int(midx + self.tile_size / 2), int(
            midy + self.tile_size / 2)

    def _get_midpoint(self, position: Tuple[int, int]) -> Tuple[int, int]:
        """ 
        Return the graphics coordinates for the center of the cell at the given (row, col) position.
        """
        row = position[0]
        col = position[1]
        if row < 0 or col < 0 or row >= NUM_ROWS or col >= NUM_COLS:
            return None

        return int(self.tile_size / 2 + BUFFER + (BUFFER + self.tile_size) * col), \
               int(self.tile_size / 2 + BUFFER + (BUFFER + self.tile_size) * row)

    def clear(self) -> None:
        """ 
        Clears all items. in fact, destory all rectangle and text.
        """
        super().delete('all')

    def redraw(self, tiles: List[List[Optional[int]]]) -> None:
        """
        Clears and redraws the entire grid based on the given tiles.
        """
        for row in range(NUM_ROWS):
            for col in range(NUM_COLS):
                box = self._get_bbox((row, col))
                x_min, y_min, x_max, y_max = box
                self.grid[row][col] = None

                super().create_rectangle(x_min, y_min, x_max, y_max, fill=COLOURS[tiles[row][col]],
                                         outline=COLOURS[tiles[row][col]])

                if tiles[row][col] is not None:
                    self.create_text(self._get_midpoint((row, col)), text=(tiles[row][col]), font=TILE_FONT,
                                     fill=FG_COLOURS[tiles[row][col]])


class StatusBar(tk.Frame):
    """
    The class is used to show game status, include current score, undo times, new game button and undo bottom.
    """

    def __init__(self, master: tk.Tk, **kwargs):
        """
        Create views as status bar.
        """
        super(StatusBar, self).__init__(master, bg=LIGHT, width=BOARD_WIDTH, height=120)
        self.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

        frame1 = tk.Frame(self, bg=LIGHT, width=BOARD_WIDTH, height=120)
        frame1.pack(side=tk.RIGHT, padx=20)

        self.btn_new_game = tk.Button(frame1, text="New Game")
        self.btn_new_game.pack(side=tk.TOP, fill=tk.BOTH, expand=1, ipady=10, pady=5)

        self.btn_undo = tk.Button(frame1, text="Undo Move", )
        self.btn_undo.pack(side=tk.TOP, fill=tk.BOTH, expand=1, ipady=10, pady=5)

        frame2 = tk.Frame(self, width=BOARD_WIDTH, bg=BACKGROUND_COLOUR)
        frame2.pack(side=tk.LEFT, padx=20)

        self.txt_score = tk.Label(frame2, text="SCORE", font=('Arial bold', 20), fg=COLOURS[None], bg=BACKGROUND_COLOUR)
        self.txt_score.pack(side=tk.TOP, pady=0)

        self.lab_score = tk.Label(frame2, text="0", font=('Arial bold', 15), fg=LIGHT, bg=BACKGROUND_COLOUR)
        self.lab_score.pack(side=tk.TOP, pady=0)

        frame3 = tk.Frame(self, width=BOARD_WIDTH, height=120, bg=BACKGROUND_COLOUR)
        frame3.pack(side=tk.LEFT, padx=20)

        self.txt_undos = tk.Label(frame3, text="UNDOS", font=('Arial bold', 20), fg=COLOURS[None], bg=BACKGROUND_COLOUR)
        self.txt_undos.pack(side=tk.TOP, pady=0)

        self.lab_undos = tk.Label(frame3, text=str(MAX_UNDOS), font=('Arial bold', 15), fg=LIGHT, bg=BACKGROUND_COLOUR)
        self.lab_undos.pack(side=tk.TOP, pady=0)

    def redraw_infos(self, score: int, undos: int) -> None:
        """ 
        Updates the score and undos labels to reflect the information was given. 
        """
        self.lab_undos.config(text=undos)
        self.lab_score.config(text=score)

    def set_callbacks(self, new_game_command: callable, undo_command: callable) -> None:
        """
        Sets the commands for the new game and undo buttons to the given commands.
        The arguments here are references to functions to be called when the buttons are pressed.
        """
        self.btn_new_game.config(command=new_game_command)
        self.btn_undo.config(command=undo_command)


class MenuBar(tk.Menu):
    """
    The game menu bar, include four function: new game, load game, quit and save game.
    """

    def __init__(self, master):
        """
        the ctor for game
        """
        super().__init__(master)
        master.config(menu=self)

        self.filemenu = tk.Menu(self)
        self.add_cascade(label='File', menu=self.filemenu)

        # filemenu.add_command(label="Save game")
        # filemenu.add_command(label="Load game")
        # filemenu.add_command(label="New game")
        # filemenu.add_command(label="Quit")

    def set_callbacks(self, new_game_command: callable, quit: callable,
                      load_game: callable, save_game: callable) -> None:
        """
        Similarly to StatusBar, set call back for four button.
        """
        self.filemenu.add_command(label="Save game", command=save_game)
        self.filemenu.add_command(label="Load game", command=load_game)
        self.filemenu.add_command(label="New game", command=new_game_command)
        self.filemenu.add_command(label="Quit", command=quit)


class Game:
    """
    The game is designed by MVC pattern, this is a Controller, it is hold the model and all view class instance.
    """

    def __init__(self, master: tk.Tk) -> None:
        """
        Create model and all view in ctor.
        
        """
        self._master = master
        """ create title for 2048 game """
        self.title = tk.Label(master, text="2048", font=TITLE_FONT, bg="#FFD700", fg=LIGHT)
        self.title.pack(side=tk.TOP, expand=1, fill=tk.BOTH)

        master.bind("<Key>", self.attempt_move)
        master.focus_set()
        self.model = Model()
        self.game_grid = GameGrid(master)

        self.bar = StatusBar(master)
        self.bar.set_callbacks(self.start_new_game, self.undo_previous_move)

        self.menu = MenuBar(master)
        self.menu.set_callbacks(self.start_new_game, self.quit, self.load_game, self.save_game)

        self.draw()

    def load_game(self):
        """
        Load game when click button, load game from file. if file if not 2048, the warning info will show.
        """
        filename = filedialog.askopenfilename()
        ans = self.model.load_game(filename)
        if not ans:
            messagebox.showwarning("warning", "the file format is error")
        else:
            self.draw()

    def save_game(self):
        """
        Save current game as a file, in order to restore next time.
        """
        filename = filedialog.asksaveasfilename()
        self.model.save_game(filename)

    def quit(self):
        """
        Quit game. and destory view.
        note: the game does not save processing. so it will ask player for operator.
        
        """
        q = messagebox.askyesno("quit game", "do you want to quit game? ")
        if q:
            self._master.destroy()
        else:
            pass

    def draw(self) -> None:
        """ 
        Redraw any view classes based on the current model state.
        """
        self.game_grid.clear()
        self.game_grid.redraw(self.model.tiles)
        self.bar.redraw_infos(self.model.get_score(), self.model.get_undos_remaining())

    def undo_previous_move(self) -> None:
        """
        A handler for when the ‘Undo’ button is pressed in the status bar.
        This method should attempt to undo the last action, and then redraw the view
        classes with the updated model information.
        """
        self.model.use_undo()
        self.draw()

    def start_new_game(self) -> None:
        """
        A handler for when the ‘New Game’ button is pressed in the status bar.
        This method should cause the model to set its state,and redraw the view classes 
        to reflect these changes. 
        Note: The new game should not replicate the initial state of the previous game. 
        The new game state should be the result of calling the new_game method on the Model 
        instance.
        """
        self.model.new_game()
        self.draw()

    def attempt_move(self, event: tk.Event) -> None:
        """
        Attempt a move if the event represents a key press on character ‘a’, ‘w’, ‘s’, or ‘d’.
        Once a move has been made, this method should redraw the view, display the appropriate
        messagebox if the game has been won, or create a new tile after 150ms if the game has not been won.
        """
        key = event.char
        ret = self.model.attempt_move(key)

        print("ret = ", ret)
        if not ret:
            self.draw()
            return

        self.draw()
        if self.model.has_won():
            print("has won")
            messagebox.askokcancel("showinfo", WIN_MESSAGE)
            return

        self.game_grid.after(150, self.new_tile)

    def new_tile(self) -> None:
        """
        Adds a new tile to the model and redraws. If the game has been lost with the addition of the new tile,
        then the player should be prompted with the appropriate messagebox displaying the LOSS_MESSAGE.
        """
        print(self.model.tiles)
        self.model.add_tile()
        self.draw()
        if self.model.has_lost():
            messagebox.askokcancel("showinfo", LOSS_MESSAGE)
            print(LOSS_MESSAGE)


def play_game(root):
    """the function for game start"""
    game = Game(root)
    pass


if __name__ == '__main__':
    """ the main function for game """
    root = tk.Tk()
    play_game(root)
    root.mainloop()
