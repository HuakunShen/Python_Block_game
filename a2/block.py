"""Assignment 2 - Blocky

=== CSC148 Fall 2017 ===
Diane Horton and David Liu
Department of Computer Science,
University of Toronto


=== Module Description ===

This file contains the Block class, the main data structure used in the game.
"""
from typing import Optional, Tuple, List
import random
import math
from renderer import COLOUR_LIST, TEMPTING_TURQUOISE, BLACK, colour_name


HIGHLIGHT_COLOUR = TEMPTING_TURQUOISE
FRAME_COLOUR = BLACK


class Block:
    """A square block in the Blocky game.

    === Public Attributes ===
    position:
        The (x, y) coordinates of the upper left corner of this Block.
        Note that (0, 0) is the top left corner of the window.
    size:
        The height and width of this Block.  Since all blocks are square,
        we needn't represent height and width separately.
    colour:
        If this block is not subdivided, <colour> stores its colour.
        Otherwise, <colour> is None and this block's sublocks store their
        individual colours.
    level:
        The level of this block within the overall block structure.
        The outermost block, corresponding to the root of the tree,
        is at level zero.  If a block is at level i, its children are at
        level i+1.
    max_depth:
        The deepest level allowed in the overall block structure.
    highlighted:
        True iff the user has selected this block for action.
    children:
        The blocks into which this block is subdivided.  The children are
        stored in this order: upper-right child, upper-left child,
        lower-left child, lower-right child.
    parent:
        The block that this block is directly within.

    === Representation Invariations ===
    - len(children) == 0 or len(children) == 4
    - If this Block has children,
        - their max_depth is the same as that of this Block,
        - their size is half that of this Block,
        - their level is one greater than that of this Block,
        - their position is determined by the position and size of this Block,
          as defined in the Assignment 2 handout, and
        - this Block's colour is None
    - If this Block has no children,
        - its colour is not None
    - level <= max_depth
    """
    position: Tuple[int, int]
    size: int
    colour: Optional[Tuple[int, int, int]]
    level: int
    max_depth: int
    highlighted: bool
    children: List['Block']
    parent: Optional['Block']

    def __init__(self, level: int,
                 colour: Optional[Tuple[int, int, int]] = None,
                 children: Optional[List['Block']] = None) -> None:
        """Initialize this Block to be an unhighlighted root block with
        no parent.

        If <children> is None, give this block no children.  Otherwise
        give it the provided children.  Use the provided level and colour,
        and set everything else (x and y coordinates, size,
        and max_depth) to 0.  (All attributes can be updated later, as
        appropriate.)
        """
        self.position = (0, 0)
        self.size = 0
        self.colour = colour
        self.level = level
        self.max_depth = 0
        self.highlighted = False
        if children is None:
            self.children = []
        else:
            self.children = children
        self.parent = None

    def rectangles_to_draw(self) -> List[Tuple[Tuple[int, int, int],
                                               Tuple[int, int],
                                               Tuple[int, int],
                                               int]]:
        """
        Return a list of tuples describing all of the rectangles to be drawn
        in order to render this Block.

        This includes (1) for every undivided Block:
            - one rectangle in the Block's colour
            - one rectangle in the FRAME_COLOUR to frame it at the same
              dimensions, but with a specified thickness of 3
        and (2) one additional rectangle to frame this Block in the
        HIGHLIGHT_COLOUR at a thickness of 5 if this block has been
        selected for action, that is, if its highlighted attribute is True.

        The rectangles are in the format required by method Renderer.draw.
        Each tuple contains:
        - the colour of the rectangle
        - the (x, y) coordinates of the top left corner of the rectangle
        - the (height, width) of the rectangle, which for our Blocky game
          will always be the same
        - an int indicating how to render this rectangle. If 0 is specified
          the rectangle will be filled with its colour. If > 0 is specified,
          the rectangle will not be filled, but instead will be outlined in
          the FRAME_COLOUR, and the value will determine the thickness of
          the outline.

        The order of the rectangles does not matter.
        """
        lst = []
        if self.children == []:

            lst.append((self.colour, self.position, (self.size, self.size), 0))
            lst.append((FRAME_COLOUR, self.position, (self.size, self.size), 3))

        else:
            for i in self.children:
                lst.extend(i.rectangles_to_draw())

        if self.highlighted is True:
            lst.append((HIGHLIGHT_COLOUR, self.position, (self.size, self.size),
                        5))
        return lst

    def swap(self, direction: int) -> None:
        """Swap the child Blocks of this Block.

        If <direction> is 1, swap vertically.  If <direction> is 0, swap
        horizontally. If this Block has no children, do nothing.
        """
        if self.children != []:
            if direction == 1:
                self.children[0], self.children[3] = self.children[3], \
                                                     self.children[0]
                self.children[1], self.children[2] = self.children[2], \
                                                     self.children[1]
            elif direction == 0:
                self.children[0], self.children[1] = self.children[1], \
                                                     self.children[0]
                self.children[2], self.children[3] = self.children[3], \
                                                     self.children[2]
        else:
            pass

        self.update_block_locations(self.position, self.size)

    def rotate(self, direction: int) -> None:
        """Rotate this Block and all its descendants.

        If <direction> is 1, rotate clockwise.  If <direction> is 3, rotate
        counterclockwise. If this Block has no children, do nothing.
        """
        if self.children != []:
            if direction == 1:
                temp = self.children[0]
                for i in range(3):      # rotate the 4 children of current level
                    self.children[i] = self.children[i + 1]
                self.children[3] = temp
                for i in self.children:      # rotate the children's children
                    i.rotate(1)
            elif direction == 3:        # rotate the 4 children of current level
                self.children.insert(0, self.children.pop(3))
                for i in self.children:      # rotate the children's children
                    i.rotate(3)
        else:
            pass
        self.update_block_locations(self.position, self.size)

    def smash(self) -> bool:
        """Smash this block.

        If this Block can be smashed,
        randomly generating four new child Blocks for it.  (If it already
        had child Blocks, discard them.)
        Ensure that the RI's of the Blocks remain satisfied.

        A Block can be smashed iff it is not the top-level Block and it
        is not already at the level of the maximum depth.

        Return True if this Block was smashed and False otherwise.
        """
        if 0 < self.level < self.max_depth:
            self.children = []
            for _ in range(4):
                self.children.append(random_init(self.level + 1,
                                                 self.max_depth))
            self.update_block_locations(self.position, self.size)
            return True
        return False

    def update_block_locations(self, top_left: Tuple[int, int],
                               size: int) -> None:
        """
        Update the position and size of each of the Blocks within this Block.

        Ensure that each is consistent with the position and size of its
        parent Block.

        <top_left> is the (x, y) coordinates of the top left corner of
        this Block.  <size> is the height and width of this Block.
        """
        self.position = top_left
        self.size = size
        halved_size = round(shize / 2.0)

        if len(self.children) != 0:
            self.children[0].update_block_locations(
                (top_left[0] + alved_size, top_left[1]), halved_size)

            self.children[1].update_block_locations(top_left, halved_size)

            self.children[2].update_block_locations(
                (top_left[0], top_left[1] + halved_size), halved_size)

            self.children[3].update_block_locations((top_left[0] + halved_size,
                                                     top_left[1] + halved_size),
                                                    halved_size)

            for i in range(4):
                self.children[i].size = halved_size
                self.children[i].parent = self
                self.children[i].max_depth = self.max_depth
                self.children[i]._set_max_depth(self.max_depth)

    def _set_max_depth(self, max_depth):
        """A helper method of update_block_locations, using recursion to set
        max_depth for single every block in the block"""
        for child in self.children:
            child.max_depth = max_depth
            child._set_max_depth(child.max_depth)

    def _get_child_block(self, location: Tuple[int, int], level: int) \
            -> 'Block':
        """A helper method of get_selected_block. This method returns the child
        Block in the given location and level. It is put to a separate function
        for readability.
        Precondition: self.children != []"""
        for child in self.children:
            block = child.get_selected_block(location, level)
            if block is not None:
                return block

    def get_selected_block(self, location: Tuple[int, int], level: int) \
            -> 'Block':
        """Return the Block within this Block that includes the given location
        and is at the given level. If the level specified is lower than
        the lowest block at the specified location, then return the block
        at the location with the closest level value.

        <location> is the (x, y) coordinates of the location on the window
        whose corresponding block is to be returned.
        <level> is the level of the desired Block.  Note that
        if a Block includes the location (x, y), and that Block is subdivided,
        then one of its four children will contain the location (x, y) also;
        this is why <level> is needed.

        Preconditions:
        - 0 <= level <= max_depth
        """
        within_x = (self.position[0] <= location[0] <= self.position[0] +
                    self.size)
        within_y = (self.position[1] <= location[1] <= self.position[
            1] + self.size)
        within = within_x and within_y

        if within and level == self.level:
            return self

        elif within and level > self.level:
            block = None
            if self.children != []:
                block = self._get_child_block(location, level)
            else:
                block = self.get_selected_block(location, level - 1)
            return block

        elif within_x and not within_y and self.level == 0:
            return self.get_selected_block((location[0], self.size), level)

        elif within_y and not within_x and self.level == 0:
            if location[0] < 0:
                return self.get_selected_block((0, location[1]), level)
            elif location[0] > self.size:
                return self.get_selected_block((self.size, location[1]), level)

        elif location[0] < 0 and location[1] < 0:
            return self

        elif location[0] > self.size and location[1] > self.size:
            return self.get_selected_block((0, 0), 0)

    def flatten(self) -> List[List[Tuple[int, int, int]]]:
        """Return a two-dimensional list representing this Block as rows
        and columns of unit cells.

        Return a list of lists L, where, for 0 <= i, j < 2^{self.level}
            - L[i] represents column i and
            - L[i][j] represents the unit cell at column i and row j.
        Each unit cell is represented by 3 ints for the colour
        of the block at the cell location[i][j]

        L[0][0] represents the unit cell in the upper left corner of the Block.
        """
        if self.children == [] and self.level == self.max_depth:
            return [[self.colour]]

        elif self.children == [] and self.level < self.max_depth:
            lst = []
            difference = self.max_depth - self.level
            for i in range(2 ** difference):
                lst2 = []
                for _ in range(2 ** difference):
                    lst2.append(self.colour)
                lst.append(lst2)
            return lst

        else:
            lst = []
            for i in range(len(self.children)):
                lst.append(self.children[i].flatten())

            lst1 = lst[1]

            for i in range(len(lst[1])):
                lst1[i].extend(lst[2][i])
            lst2 = lst[0]
            for i in range(len(lst[0])):
                lst2[i].extend(lst[3][i])
            return lst1 + lst2


def random_init(level: int, max_depth: int) -> 'Block':
    """Return a randomly-generated Block with level <level> and subdivided
    to a maximum depth of <max_depth>.

    Throughout the generated Block, set appropriate values for all attributes
    except position and size.  They can be set by the client, using method
    update_block_locations.

    Precondition:
        level <= max_depth
    """
    colour = COLOUR_LIST[random.randint(0, 3)]
    children = []
    if level < max_depth:
        random_num = random.random()
        if random_num < math.exp(-0.25 * level):
            for _ in range(4):
                children.append(random_init(level + 1, max_depth))
    else:
        colour = COLOUR_LIST[random.randint(0, 3)]

    return Block(level, colour, children)


def attributes_str(b: Block, verbose) -> str:
    """Return a str that is a concise representation of the attributes of <b>.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Note: These are attributes that every Block has.
    """
    answer = f'pos={b.position}, size={b.size}, level={b.level}, '
    if verbose:
        answer += f'highlighted={b.highlighted}, max_depth={b.max_depth}'
    return answer


def print_block(b: Block, verbose=False) -> None:
    """Print a text representation of Block <b>.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Precondition: b is not None.
    """
    print_block_indented(b, 0, verbose)


def print_block_indented(b: Block, indent: int, verbose) -> None:
    """Print a text representation of Block <b>, indented <indent> steps.

    Include attributes position, size, and level.  If <verbose> is True,
    also include highlighted, and max_depth.

    Precondition: b is not None.
    """
    if len(b.children) == 0:
        # b a leaf.  Print its colour and other attributes
        print(f'{"  " * indent}{colour_name(b.colour)}: ' +
              f'{attributes_str(b, verbose)}')
    else:
        # b is not a leaf, so it doesn't have a colour.  Print its
        # other attributes.  Then print its children.
        print(f'{"  " * indent}{attributes_str(b, verbose)}')
        for child in b.children:
            print_block_indented(child, indent + 1, verbose)


if __name__ == '__main__':
    import python_ta
    python_ta.check_all(config={
        'allowed-io': ['print_block_indented'],
        'allowed-import-modules': [
            'doctest', 'python_ta', 'random', 'typing',
            'block', 'goal', 'player', 'renderer', 'math'
        ],
        'max-attributes': 15
    })

    # This tiny tree with one node will have no children, highlighted False,
    # and will have the provided values for level and colour; the initializer
    # sets all else (position, size, and max_depth) to 0.
    b0 = Block(0, COLOUR_LIST[2])
    # Now we update position and size throughout the tree.
    b0.update_block_locations((0, 0), 750)
    print("=== tiny tree ===")
    # We have not set max_depth to anything meaningful, so it still has the
    # value given by the initializer (0 and False).
    print_block(b0, True)

    b1 = Block(0, children=[
        Block(1, children=[
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, COLOUR_LIST[2]),
        Block(1, children=[
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[1]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[0])
        ]),
        Block(1, children=[
            Block(2, COLOUR_LIST[0]),
            Block(2, COLOUR_LIST[2]),
            Block(2, COLOUR_LIST[3]),
            Block(2, COLOUR_LIST[1])
        ])
    ])
    b1.update_block_locations((0, 0), 750)
    print("\n=== handmade tree ===")
    # Similarly, max_depth is still 0 in this tree.  This violates the
    # representation invariants of the class, so we shouldn't use such a
    # tree in our real code, but we can use it to see what print_block
    # does with a slightly bigger tree.
    print_block(b1, True)

    # Now let's make a random tree.
    # random_init has the job of setting all attributes except position and
    # size, so this time max_depth is set throughout the tree to the provided
    # value (3 in this case).
    b2 = random_init(0, 3)
    # Now we update position and size throughout the tree.
    b2.update_block_locations((0, 0), 750)
    print("\n=== random tree ===")
    # All attributes should have sensible values when we print this tree.
    print_block(b2, True)
