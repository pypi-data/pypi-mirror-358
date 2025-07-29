from time import sleep

from rich import print


def rest_room(player):
    print("[blue]You enter a peaceful room with a cosy bed.[/blue]")
    sleep(1)
    print("It is safe to rest. Do you sleep?")
    choice = input(">> ").lower()
    continues = ["y", "ye", "ya", "yah", "yes", "yeah", "okay", "ok", "sure", "i guess", "yea"]
    nos = ["n", "na", "no", "nah", "nope", "no way", "no thanks"]
    if choice in continues:
        print("You had a wonderful sleep.")
        sleep(1)
        player.rest()
    elif choice in nos:
        pass
    else:
        print("You cannot do that.")
        rest_room(player)
