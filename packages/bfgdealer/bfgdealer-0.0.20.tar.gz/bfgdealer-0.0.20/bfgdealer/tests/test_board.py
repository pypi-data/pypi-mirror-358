from pathlib import Path
from termcolor import cprint

from bridgeobjects import load_pbn, Card
from bfgbidding import Hand

from ..src.board import Board


MODULE_COLOUR = 'blue'
BOARD_PATH = Path('tests', 'test_data', 'board.pbn')


event = load_pbn(BOARD_PATH)[0]
boards = {}
for raw_board in event.boards:
    board = Board()
    board.get_attributes_from_board(raw_board)
    boards[board.identifier] = board


def test_get_unplayed_cards():
    board = boards['0']
    assert Card('6H') in board.hands['E'].unplayed_cards
    assert Card('TH') not in board.hands['E'].unplayed_cards
    assert Card('QH') not in board.hands['E'].unplayed_cards

    assert Card('7H') in board.hands['S'].unplayed_cards
    assert Card('2H') not in board.hands['S'].unplayed_cards

    assert Card('AH') not in board.hands['W'].unplayed_cards

    assert Card('JH') not in board.hands['N'].unplayed_cards


def test_hand_type():
    board = boards['0']
    assert type(board.hands['W']) == Hand


def test_initialise_tricks():
    board = boards['0']
    assert len(board.tricks) == 2
    assert board.tricks[-1].leader == 'W'

    board = boards['1']
    assert len(board.tricks) == 1
    assert board.tricks[-1].leader == 'E'
