from Game import Game
from arcade_machine_sdk import GameMeta
import pygame

pygame.init()

metadata = (GameMeta()
            .with_title("CENTIPEDE")
            .with_description("Classic")
            .with_release_date("2/02/2026")
            .with_group_number(9)
            .add_tag("Shooter")
            .add_author("Juan Simancas, Gabriel Garanton"))

game = Game(metadata)
if __name__ == "__main__":

    game.run_independently()
