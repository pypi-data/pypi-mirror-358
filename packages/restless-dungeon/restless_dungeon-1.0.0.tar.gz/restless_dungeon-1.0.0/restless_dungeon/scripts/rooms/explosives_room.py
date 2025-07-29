from time import sleep

from rich import print


def explosives_room(player):
    print("You walk into a room full of [red]explosives[/red].")
    sleep(1)
    print("[yellow]You hear a click beneath your feet as the explosives are triggered.[/yellow]")
    sleep(1)
    print("You can escape the blast if you sprint, or you can take the hit and preserve your energy.")
    sleep(1)
    print("Do you run for it?")
    choice = input(">> ").lower()
    confirms = ["y", "ye", "ya", "yah", "yes", "yeah", "okay", "ok", "sure", "i guess", "yea"]
    denies = ["n", "na", "no", "nah", "nope", "no way", "no thanks"]
    if choice in confirms:
        player.consume_energy(8)
        print("You escaped the blast.")
    elif choice in denies:
        player.take_damage(10)
        print("You survived the explosions.")
    else:
        print("You cannot do that.")
        sleep(1)
        explosives_room(player)
