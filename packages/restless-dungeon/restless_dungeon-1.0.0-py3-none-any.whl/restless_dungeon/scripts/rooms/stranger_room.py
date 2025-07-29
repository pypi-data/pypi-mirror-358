from math import floor
from random import randint
from time import sleep

from rich import print


def stranger_room(player):
    print("[yellow]You enter a dimly lit room. There is a strange man standing in the corner.[/yellow]")
    sleep(1)
    print("Do you approach the man?")
    choice = input(">> ").lower()
    confirms = ["yes", "y", "yep", "ok", "okay", "sure", "ye", "yeah", "yea",
                "yah"]
    if choice in confirms:
        if randint(0, 1) == 0:
            sleep(0.8)
            print("[green]The strange man turns to you and smiles.[/green]")
            sleep(1)
            print("You feel a warm and calming energy.")
            sleep(1)
            player.energy = player.max_energy
            print("[green]Your energy is restored.[green]")
            sleep(1)
            print(f"[green]Energy: {player.energy}[/green]")
        else:
            print("[red]The strange man turns to you and scowls.[/red]")
            sleep(1)
            print("[red]You feel a sharp pain and a cloud of fog enters your mind.[/red]")
            sleep(1)
            player.take_damage(floor(player.health / 100 * 20))  # damage 20% of current health (rounded)
            sleep(1)
            player.consume_energy(floor(player.energy / 100 * 50))  # consume 50% of current energy (rounded)
