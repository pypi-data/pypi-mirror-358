from time import sleep

from rich import print


def empty_room(_player):  # _player so that it takes the same parameters as the other rooms
    print("[blue]You enter an empty room. There's nothing to do.[/blue]")
    sleep(1)
