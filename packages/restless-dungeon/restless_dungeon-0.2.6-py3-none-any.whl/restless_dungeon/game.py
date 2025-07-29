import os
from random import randint
from time import sleep

from rich import print

from restless_dungeon.scripts.player import Player
from restless_dungeon.scripts.rooms.empty_room import empty_room
from restless_dungeon.scripts.rooms.explosives_room import explosives_room
from restless_dungeon.scripts.rooms.rest_room import rest_room
from restless_dungeon.scripts.rooms.stair_room import stair_room
from restless_dungeon.scripts.rooms.stranger_room import stranger_room
from restless_dungeon.scripts.rooms.walls_closing_room import walls_closing_room
from restless_dungeon.scripts.rooms.zombie_room import zombie_room


def clear_screen():
    if os.name == 'nt':
        _ = os.system('cls')
    else:
        _ = os.system('clear')


class Game:
    def __init__(self):
        self.player = Player(self)
        self.last_room = 0
        self.first_room = True
        self.room = 1
        self.win_level = 15

    @staticmethod
    def end(death_type):
        print(f"You ran out of {death_type.lower()} and died.")
        print("[red]GAME OVER[/red]")
        quit()

    def enter_room(self):
        rooms = [empty_room, rest_room, zombie_room, walls_closing_room, stranger_room, explosives_room, stair_room]
        if self.first_room:
            number = randint(2, len(rooms) - 1)
            self.first_room = False
        else:
            while True:
                number = randint(0, len(rooms) - 1)
                if number != self.last_room:
                    break
        print(f"[green]Health:[/green] {self.player.health} / {self.player.max_health}")
        print(f"[green]Energy:[/green] {self.player.energy} / {self.player.max_energy}")
        print()
        print(f"Room {self.room}")
        print()
        rooms[number](self.player)
        self.last_room = number
        sleep(2)
        print()
        print()

    def run(self):
        clear_screen()
        print("[yellow]Welcome to the dungeon.[/yellow]")
        sleep(1)
        print()
        while self.room <= self.win_level:
            self.enter_room()
            while True:
                print("Are you ready to continue your journey?")
                choice = input(">> ").lower()
                continues = ["y", "ye", "ya", "yah", "yes", "yeah", "okay", "ok", "sure", "i guess", "yea",
                             "not really but okay"]
                if choice in continues:
                    print("You continue onwards.")
                    print()
                    sleep(1.5)
                    break
                else:
                    print("[red]In the dungeon, there is no escape.[/red]")
                    self.player.take_damage(2)
                    print()
                    sleep(1.5)
            self.room += 1
            clear_screen()
        print("[green]Congratulations! You reached the end of the dungeon and escaped.[/green]")
        print("[bold]You Win.[bold]")
