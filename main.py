from components import GameBrain
import time


def main():
    with open("highscore.txt", mode="r") as file:
        highscore = int(file.read())

    game = GameBrain(highscore)
    game.prep_gamestart()
    game.window.update()
    game.ui.show_stage(game.stage)
    game.window.update()
    time.sleep(2)
    game.ui.stage_drawer.clear()
    game.window.update()

    while not game.check_game_over():
        start = time.time()
        if game.canon_moving_right:
            game.canon.move_right()
        elif game.canon_moving_left:
            game.canon.move_left()
        if game.canon_shooting:
            game.shoot_canon()

        game.window.update()
        game.check_bullets_out_of_bounds()
        game.move_aliens()
        game.check_hits_enemy()
        game.check_hits_friendly()
        game.check_hits_bunker()
        game.shoot_aliens()
        game.move_bullets()
        game.check_hits_enemy()

        if game.check_stage_clear():
            game.reset()
            game.next_stage()

        duration_diff = 0.004 - (time.time() - start)
        if duration_diff > 0:
            time.sleep(duration_diff)

    game.ui.game_over_screen()
    game.window.update()
    with open("highscore.txt", mode="w") as file:
        file.write(f"{game.ui.score}")
    game.window.exitonclick()


if __name__ == "__main__":
    main()
