from time import sleep

from rich import print


def walls_closing_room(player):
    print("You walk into a narrow hallway and hear a click.")
    sleep(1)
    print("[red]The walls creak and start moving towards you.[/red]")
    sleep(0.8)
    print("You sprint to the other side, escaping with minor scratches.")
    sleep(1)
    player.take_damage(3)
    sleep(1)
    player.consume_energy(5)
