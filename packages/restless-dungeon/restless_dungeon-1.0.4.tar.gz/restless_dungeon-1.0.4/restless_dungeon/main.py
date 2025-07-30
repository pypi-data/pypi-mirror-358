from rich import print

from restless_dungeon.game import Game


def main():
    game = Game()
    try:
        game.run()
    except KeyboardInterrupt:
        print("\n[red bold]Quitting? I don't think so.\nYou Lose.\nGAME OVER[/red bold]")
        quit()


if __name__ == "__main__":
    main()
