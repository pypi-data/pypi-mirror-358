from random import randint
from time import sleep

from rich import print


def zombie_room(player):
    options = ["fight", "flee"]
    print()
    print("[dark_orange]You stumble into a room full of zombies.[/dark_orange]")
    sleep(1)
    print("Do you fight or flee?")
    choice = input(">> ").lower()
    if choice not in options:
        print("You cannot do that.")
        zombie_room(player)
    elif choice == "flee":
        sleep(1)
        player.consume_energy(2)
    elif choice == "fight":
        number = randint(0, 5)
        sleep(1)
        if player.inventory.get("sword"):
            player.take_damage(2)
        else:
            player.take_damage(5)
        print("You killed all the zombies.")
        if number == 5:
            sleep(1)
            print("A zombie dropped a sword.")
            player.pick_up_item("sword")
