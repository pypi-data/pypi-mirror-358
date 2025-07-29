from rich import print
from time import sleep

def stair_room(player):
    print("You come across a staircase.")
    sleep(1)
    print("You can go up or down.")
    sleep(1)
    print("Which way do you climb?")
    choice = input(">> ").lower()
    if choice == "up":
        print("You reach the top of the stairs and find a door.")
        sleep(1)
    elif choice == "down":
        print("[red]As you descend, a deep growl fills the silence.[/red]")
        sleep(1)
        print("[red]You turn around and sprint up the stairs.[/red]")
        sleep(1)
        player.consume_energy(3)
        sleep(1)
        print("You reach the top of the stairs and find a door.")
    else:
        print("You cannot do that.")
        sleep(1)
        stair_room(player)
