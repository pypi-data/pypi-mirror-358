from bfgdealer import DealerSolo as Dealer

MAX_REPETITIONS = 100


def test_opening_one_board():
    dealer = Dealer()
    for _ in range(MAX_REPETITIONS):
        board = dealer.get_set_hand(['0'], 'N')
        assert board.hands['N'].hcp >= 12
        assert board.hands['N'].hcp <= 23
