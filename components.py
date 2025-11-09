import turtle
import random
import time

ALIEN_IMG = "Images/Alien.gif"
BUNKER_IMG = "Images/Bunker_[life].gif"
CANON_IMG = "Images/Canon.gif"

BULLET_SHAPE = ((-1, 12), (1, 12), (1, -12), (-1, -12))
WINDOW_SIZE = (900, 900)
GAME_WIDTH = 700
GAME_HEIGHT = 800
GAME_BORDER = [
    (-GAME_WIDTH / 2, GAME_HEIGHT / 2),
    (GAME_WIDTH / 2, GAME_HEIGHT / 2),
    (GAME_WIDTH / 2, -GAME_HEIGHT / 2),
    (-GAME_WIDTH / 2, -GAME_HEIGHT / 2),
]

FONT_BIG = ("Arial", 24, "bold")

BULLET_PROP = 0.01
ALIEN_SCORE = 50


class GameBrain:
    def __init__(self, highscore: int):
        self.screen_width = WINDOW_SIZE[0]
        self.screen_height = WINDOW_SIZE[1]

        self.life = 3
        self.stage = 1
        self.alien_trajectory = 0
        self.alien_velocity = 0.2
        self.canon_moving_right = False
        self.canon_moving_left = False
        self.canon_shooting = False
        self.last_shoot = time.time()

        self.alien_pos_y = 240
        self.alien_pos_x = -200
        self.bunker_pos_y = -200
        self.bunker_pos_x = -GAME_WIDTH / 2 + GAME_WIDTH / 5

        self.all_aliens: list[Alien] = []
        self.all_bunker: list[Bunker] = []
        self.all_bullets: list[Bullet] = []

        self.window = turtle.Screen()
        self.ui = Ui(highscore)
        self.canon = Canon()

        self.setup()

    def setup(self):
        self.window.tracer(0)
        self.screen_setup()
        self.ui_setup()
        self.canon.spawn()
        self.window.listen()
        self.window.onkeypress(fun=self.toggle_move_right_on, key="d")
        self.window.onkeyrelease(fun=self.toggle_move_right_off, key="d")

        self.window.onkeypress(fun=self.toggle_move_left_on, key="a")
        self.window.onkeyrelease(fun=self.toggle_move_left_off, key="a")

    def toggle_move_right_on(self):
        self.canon_moving_right = True

    def toggle_move_right_off(self):
        self.canon_moving_right = False

    def toggle_move_left_on(self):
        self.canon_moving_left = True

    def toggle_move_left_off(self):
        self.canon_moving_left = False

    def toggle_shoot_on(self):
        self.canon_shooting = True

    def toggle_shoot_off(self):
        self.canon_shooting = False

    def prep_gamestart(self):
        self.spawn_aliens()
        self.spawn_bunkers()
        self.window.onkeypress(fun=self.toggle_shoot_on, key="space")
        self.window.onkeyrelease(fun=self.toggle_shoot_off, key="space")

    def shoot_canon(self):
        if time.time() - self.last_shoot > 0.5:
            bullet = self.canon.shoot()
            self.all_bullets.append(bullet)
            self.last_shoot = time.time()

    def screen_setup(self):
        self.window.setup(self.screen_width, self.screen_height)
        self.window.register_shape("Bullet", BULLET_SHAPE)
        self.window.register_shape(ALIEN_IMG)
        self.window.register_shape(CANON_IMG)
        for i in range(1, 6):
            img = BUNKER_IMG.replace("[life]", str(i))
            self.window.register_shape(img)

    def ui_setup(self):
        self.ui.draw_borders()
        self.ui.draw_scoreboard()
        self.ui.draw_life()

    def spawn_aliens(self):
        for i in range(11 * 4):
            alien = Alien(self.alien_velocity)
            self.all_aliens.append(alien)

        counter = 0
        for alien in self.all_aliens:
            counter += 1
            alien.spawn((self.alien_pos_x, self.alien_pos_y))
            if counter == 11:
                counter = 0
                self.alien_pos_y += 40
                self.alien_pos_x -= 40 * 10
            else:
                self.alien_pos_x += 40

    def spawn_bunkers(self):
        for i in range(4):
            bunker = Bunker()
            self.all_bunker.append(bunker)
            bunker.spawn((self.bunker_pos_x, self.bunker_pos_y))
            self.bunker_pos_x += GAME_WIDTH / 5

    def move_bullets(self):
        for bullet in self.all_bullets:
            bullet.move()

    def check_hits_enemy(self):
        for bullet in self.all_bullets:
            if bullet.origin == "friendly":
                for alien in self.all_aliens:
                    if alien.xcor() - 30 < bullet.xcor() < alien.xcor() + 30:
                        if alien.ycor() - 30 < bullet.ycor() < alien.ycor() + 30:
                            self.all_bullets.remove(bullet)
                            self.all_aliens.remove(alien)
                            bullet.destroy()
                            alien.destroy()
                            self.ui.score += ALIEN_SCORE
                            self.ui.update_score()

    def check_hits_friendly(self):
        for bullet in self.all_bullets:
            if bullet.origin == "enemy":
                if self.canon.xcor() - 30 < bullet.xcor() < self.canon.xcor() + 30:
                    if self.canon.ycor() - 30 < bullet.ycor() < self.canon.ycor() + 30:
                        self.life -= 1
                        self.ui.update_life(self.life)
                        self.all_bullets.remove(bullet)
                        bullet.destroy()

    def check_hits_bunker(self):
        for bullet in self.all_bullets:
            for bunker in self.all_bunker:
                if bunker.xcor() - 50 < bullet.xcor() < bunker.xcor() + 50:
                    if bunker.ycor() - 40 < bullet.ycor() < bunker.ycor() + 40:
                        self.all_bullets.remove(bullet)
                        bullet.destroy()
                        if bunker.reduce_life():
                            self.all_bunker.remove(bunker)

    def check_bullets_out_of_bounds(self):
        for bullet in self.all_bullets:
            if bullet.ycor() > GAME_HEIGHT or bullet.ycor() < -GAME_HEIGHT:
                self.all_bullets.remove(bullet)
                bullet.destroy()

    def get_outermost_alien(
        self, left: bool = False, right: bool = False, bot: bool = False
    ) -> dict[str:float]:
        value_dict = {}
        if left:
            min_x = 0
            for alien in self.all_aliens:
                if alien.xcor() < min_x:
                    min_x = alien.xcor()
            value_dict["left"] = min_x

        if right:
            min_x = 0
            for alien in self.all_aliens:
                if alien.xcor() > min_x:
                    min_x = alien.xcor()
            value_dict["right"] = min_x

        if bot:
            min_y = GAME_HEIGHT
            for alien in self.all_aliens:
                if alien.ycor() < min_y:
                    min_y = alien.ycor()
            value_dict["bot"] = min_y

        return value_dict

    def move_aliens(self):
        border_dict = self.get_outermost_alien(right=True, left=True)
        if border_dict["left"] <= -GAME_WIDTH / 2 + 30:
            for alien in self.all_aliens:
                alien.move_down()
                self.alien_trajectory = 0
        if border_dict["right"] >= GAME_WIDTH / 2 - 30:
            for alien in self.all_aliens:
                alien.move_down()
                self.alien_trajectory = 1

        for alien in self.all_aliens:
            alien.move_side(self.alien_trajectory)

    def shoot_aliens(self):
        for alien in self.all_aliens:
            bullet = alien.try_shoot()
            if bullet:
                self.all_bullets.append(bullet)

    def check_game_over(self) -> bool:
        border_dict = self.get_outermost_alien(bot=True)
        if self.life <= 0:
            return True
        elif border_dict["bot"] <= self.bunker_pos_y:
            return True
        else:
            return False

    def check_stage_clear(self) -> bool:
        if len(self.all_aliens) == 0:
            return True
        else:
            return False

    def reset(self):
        for bunker in self.all_bunker:
            bunker.destroy()
        for bullet in self.all_bullets:
            bullet.destroy()

        self.all_aliens: list[Alien] = []
        self.all_bunker: list[Bunker] = []
        self.all_bullets: list[Bullet] = []

        self.alien_pos_y = 240
        self.alien_pos_x = -200
        self.bunker_pos_y = -200
        self.bunker_pos_x = -GAME_WIDTH / 2 + GAME_WIDTH / 5

        self.alien_trajectory = 0

    def next_stage(self):
        self.stage += 1
        self.alien_velocity += 0.1
        self.ui.show_stage(self.stage)
        self.window.update()
        time.sleep(2)
        self.ui.stage_drawer.clear()
        self.window.update()

        self.prep_gamestart()
        self.window.update()


class Ui(turtle.Turtle):
    def __init__(self, highscore: int):
        super().__init__()
        self.speed("fastest")
        self.hideturtle()

        self.score_drawer = turtle.Turtle()
        self.life_drawer = turtle.Turtle()
        self.stage_drawer = turtle.Turtle()

        self.score = 0
        self.highscore = highscore

        self.setup()

    def setup(self):
        self.score_drawer.speed("fastest")
        self.life_drawer.speed("fastest")
        self.stage_drawer.speed("fastest")
        self.score_drawer.hideturtle()
        self.life_drawer.hideturtle()
        self.stage_drawer.hideturtle()
        self.life_drawer.color("red")

    def draw_borders(self):
        x = GAME_BORDER[-1][0]
        y = GAME_BORDER[-1][1]
        self.teleport(x, y)
        for corner in GAME_BORDER:
            x = corner[0]
            y = corner[1]
            self.goto(x, y)

    def draw_scoreboard(self):
        self.score_drawer.teleport(GAME_BORDER[0][0], GAME_BORDER[0][1])
        self.score_drawer.write(f"Score: {self.score}", font=FONT_BIG)
        self.teleport(GAME_BORDER[1][0], GAME_BORDER[1][1])
        self.write(f"Highscore: {self.highscore}", font=FONT_BIG, align="right")

    def draw_life(self):
        self.life_drawer.teleport(GAME_BORDER[3][0], GAME_BORDER[3][1])
        self.life_drawer.write("❤❤❤", font=FONT_BIG)

    def update_score(self):
        self.score_drawer.clear()
        self.score_drawer.teleport(GAME_BORDER[0][0], GAME_BORDER[0][1])
        self.score_drawer.write(f"Score: {self.score}", font=FONT_BIG)

    def update_life(self, life: int):
        life_score = ""
        for i in range(life):
            life_score += "❤"
        self.life_drawer.clear()
        self.life_drawer.teleport(GAME_BORDER[3][0], GAME_BORDER[3][1])
        self.life_drawer.write(life_score, font=FONT_BIG)

    def game_over_screen(self):
        self.teleport(0, 0)
        self.write("GAME OVER!", font=FONT_BIG, align="center")

    def show_stage(self, stage: int):
        self.stage_drawer.teleport(0, 0)
        self.stage_drawer.write(f"Stage {stage}", font=FONT_BIG, align="center")


class Canon(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.velocity = 1

    def spawn(self):
        self.speed("fastest")
        self.penup()
        self.shape(CANON_IMG)
        self.goto((0, -325))

    def shoot(self):
        bullet = Bullet(origin="friendly")
        bullet.spawn(self.pos())
        return bullet

    def move_left(self):
        if self.xcor() > -GAME_WIDTH / 2 + 30:
            new_x = self.xcor() - self.velocity
            self.goto(x=new_x, y=self.ycor())

    def move_right(self):
        if self.xcor() < GAME_WIDTH / 2 - 30:
            new_x = self.xcor() + self.velocity
            self.teleport(x=new_x, y=self.ycor())


class Bullet(turtle.Turtle):
    def __init__(self, origin: str):
        """origin: 'friendly' | 'enemy'"""
        super().__init__()
        self.velocity = 1
        self.origin = origin

    def spawn(self, pos: tuple[int | float, int | float]):
        """pos: tuple with (x, y) coordinates"""
        self.penup()
        self.shape("Bullet")
        self.teleport(x=pos[0], y=pos[1])
        match self.origin:
            case "friendly":
                self.seth(90)

            case "enemy":
                self.seth(270)

            case _:
                raise ValueError

        self.forward(30)

    def move(self):
        self.forward(self.velocity)

    def destroy(self):
        self.hideturtle()
        self.teleport(GAME_WIDTH, GAME_HEIGHT)


class Alien(turtle.Turtle):
    def __init__(self, velocity: float):
        super().__init__()
        self.velocity: float = velocity

    def spawn(self, start_position: tuple[int | float, int | float]):
        self.speed("fastest")
        self.penup()
        self.shape(ALIEN_IMG)
        self.goto(start_position)

    def destroy(self):
        self.hideturtle()
        self.teleport(GAME_WIDTH, GAME_HEIGHT)

    def move_side(self, direction: int):
        """0 for right | 1 for left"""
        if direction == 0:
            self.forward(self.velocity)
        elif direction == 1:
            self.back(self.velocity)
        else:
            raise ValueError

    def move_down(self):
        self.teleport(x=self.pos()[0], y=self.pos()[1] - 40)

    def try_shoot(self, probability: int = BULLET_PROP) -> Bullet | None:
        dice = random.randint(0, int(100 / probability))
        if dice <= 1:
            bullet = Bullet(origin="enemy")
            bullet.spawn(self.pos())
            return bullet
        else:
            return None


class Bunker(turtle.Turtle):
    def __init__(self):
        super().__init__()
        self.life = 5

    def spawn(self, start_position: tuple[int | float, int | float]):
        self.speed("fastest")
        self.shape(BUNKER_IMG.replace("[life]", str(self.life)))
        self.penup()
        self.goto(start_position)

    def reduce_life(self) -> bool:
        """Returns True if bunker gets destroyed"""
        if self.life <= 1:
            self.destroy()
            return True
        else:
            self.life -= 1
            self.shape(BUNKER_IMG.replace("[life]", str(self.life)))
            return False

    def destroy(self):
        self.hideturtle()
        self.teleport(GAME_WIDTH, GAME_HEIGHT)
