import pygame as pg
import sys
import random as rnd


def Percentage(whole, perc, sign='-'):
    text3 = "{0} {1} ({0} * {2} / 100)".format(whole, sign, perc)
    return eval(text3)


def CenterX(surface): return center_pos[0] - (surface.get_width() / 2)
def CenterY(surface): return center_pos[1] - (surface.get_height() / 2)
def CenterPos(surface): return CenterX(surface), CenterY(surface)

pg.init()
clock = pg.time.Clock()
running = True
game_start = False
game_pause = False
game_ended = True
# can_play = False
is_level_finished = False
percent = 45

screen_width = 1500
screen_height = int(Percentage(screen_width, percent))
SCREEN = pg.display.set_mode((screen_width, screen_height))
# PAUSE
pause_font = pg.font.Font("Font/azonix.otf", 50)
intro_font = pg.font.Font("Font/azonix.otf", 100)

# STATUS SYSTEM
gameover_font = pg.font.Font("Font/azonix.otf", 100)
score_font = pg.font.Font("Font/azonix.otf", 30)
life_font = pg.font.Font("Font/azonix.otf", 30)
level_font = pg.font.Font("Font/azonix.otf", 50)

score_counter = 0
# target_score = (200, 400, 600)
target_score = (5, 10, 15)
target_score_iterator = 0

current_score = 0
current_life = 3
score_pos = (Percentage(screen_width, 95), Percentage(screen_height, 10))
center_pos = (screen_width / 2, screen_height / 2)

max_timelapse = 1000
min_timelapse = 70
current_timelapse = 70
level = [1, 2, 3]
current_level = level[0]
next_level_delay = 0
next_level_interval = 100

# BACKGROUND
bg_scroll_speed = 0.6
bg_pos_x = 0
is_bg_set = True
bg_image = None
bg_image_name = ("Sprites/galaxy1.jpg", "Sprites/galaxy2.jpg", "Sprites/galaxy4.jpg")
border_up_pos = [0, -100]
border_bot_pos = [0, screen_height]

# ENEMIES
enemy_sprites = ('Sprites/enemy1.png', 'Sprites/enemy2(3).png', 'Sprites/enemy2(2).png', 'Sprites/enemy2.png')
enemies = []
enemy_bullets = []
enemy1_speed = [3, 4, 4.5, 5]
enemy2_y = [-50, screen_height + 50]
enemy_shoot_interval = [0, 40, 50, 60, 80]
enemy_update = False
max_enemy_count = 20
max_score_counter = max_enemy_count
enemy_spawn_delay = 0
enemy_spawn_interval = 30
enemy_count = 2
enemy_counter = 0
enemy_counter_limit = enemy_count + 1
score_counter_limit = score_counter + 2

# POWER UP
powerup_obj = None
powerup_speed = 5

powerup_avail = False
can_spawn_powerup = False

# PLAYER (Static Values)
player = None
player_pos_y = 0
player_pos_x = 0
player_spawn_area = [50, rnd.randrange(0, screen_height)]
player_speed = 3
end_boost = 3

player_max_x = screen_width - 200
player_min_x = 20
player_max_y = screen_height - 100
player_min_y = 20

player_bullets = []
player_bullet_speed = 7

player_update = False
is_player_dead = False

player_bullet_height = 0
player_bullet_range = 650
player_bullet_damage = 3
player_bullet_SFX = pg.mixer.Sound("Audio/laserSFX_1.wav")

player_bullet_pos_L = []
player_bullet_pos_R = []

l_shooting = False
l_can_shoot = False

r_shooting = False
r_can_shoot = False

player_bullet_count_interval_L = 0
player_bullet_count_interval_R = 0

player_bullet_interval_R = player_bullet_interval_L = 40

# PLAYER (Dynamic Values)
max_upgrade = 3
player_current_upgrades = [player_bullet_speed, player_bullet_damage, player_bullet_range, player_speed,
                           bg_scroll_speed, player_bullet_interval_L, player_bullet_interval_R]


# CLASSES -------------------------------------------------------------------------------------------------------------

class GameObject:
    def __init__(self, sprite, pos, speed, name):
        self.sprite = pg.image.load(sprite).convert_alpha()
        self.pos = pos
        self.speed = speed
        self.name = name
        self.size = self.sprite.get_size()
        self.width = self.GetSprite().get_width()
        self.height = self.GetSprite().get_height()
        self.corners = [0, pos[0], 0, pos[1]]

    # GETTERS
    def GetName(self): return self.name

    def GetSprite(self): return self.sprite

    def GetPos(self): return self.pos

    def GetSpeed(self): return self.speed

    def GetName(self): return self.name

    def GetSize(self): return self.size

    def GetHeight(self): return self.height

    def GetLeft(self): return self.corners[0]

    def GetBottom(self): return self.corners[1]

    def GetRight(self): return self.corners[2]

    def GetTop(self): return self.corners[3]

    def GetCorners(self): return self.corners

    # SETTERS
    def SetPos(self, new_pos): pass

    def SetSpeed(self, new_speed): self.speed = new_speed

    def SetHeight(self, height): self.height = height

    def SetWidth(self, width): self.width = width

    def SetLeft(self, new_left): self.corners[0] = new_left

    def SetBottom(self, new_bottom): self.corners[1] = new_bottom

    def SetRight(self, new_right): self.corners[2] = new_right

    def SetTop(self, new_top): self.corners[3] = new_top

    def ScaleCollider(self, collider_point, surface_point, line, extra=0): return collider_point + (
                (line - surface_point) / 2 + extra)

    def SetCorners(self, corners): self.corners = corners


class Unit(GameObject):
    def __init__(self, sprite, pos, speed, name, show_collider=False):
        super().__init__(sprite, pos, speed, name)
        self.show_collider = show_collider
        self.range = 0
        self.Spawn()

    def ShowInfo(self):
        print("name: {2} | position: {0} | speed: {1}".format(self.pos, self.speed, self.name))

    def GetRange(self):
        return self.range

    def Spawn(self):
        if self.show_collider: self.SetCollider()
        SCREEN.blit(self.sprite, self.pos)

    def SetCollider(self):
        collider = self.sprite.get_rect(topleft=(self.pos))
        self.SetCorners((collider.left, collider.bottom, collider.right, collider.top))
        if self.show_collider: pg.draw.rect(SCREEN, red, collider, 3)
        del collider


class Player(Unit):
    def SetPos(self, new_pos):
        self.pos[0] += new_pos[0]
        self.pos[1] += new_pos[1]

        if self.pos[0] <= player_min_x:
            self.pos[0] = player_min_x
        elif self.pos[0] >= player_max_x:
            if not is_level_finished:
                self.pos[0] = player_max_x
            else:
                self.pos[0] = player_max_x + 400

        # TODO FIX HERE
        if self.pos[1] <= player_min_y:
            self.pos[1] = player_min_y
        elif self.pos[1] >= player_max_y:
            self.pos[1] = player_max_y

        self.SetCollider()
        SCREEN.blit(self.GetSprite(), self.pos)

    def GetBulletL(self):
        return self.GetPos()[0] + 20, self.GetPos()[1] + Percentage(self.GetHeight(), 75)

    def GetBulletR(self):
        return self.GetPos()[0] + 20, self.GetPos()[1] + Percentage(self.GetHeight(), 35) - player_bullet_height

    def SetCollider(self):
        collider = self.sprite.get_rect(topleft=(self.pos))
        new_right = Percentage(collider.width, 70)
        new_bottom = Percentage(collider.height, 30)
        new_left = self.ScaleCollider(collider.left, self.sprite.get_width(), new_right, 30)
        new_top = self.ScaleCollider(collider.top, self.sprite.get_height(), new_bottom, 30)
        collider_rect = pg.Rect(new_left, new_top, new_right, new_bottom)
        self.SetCorners((collider_rect.left, collider_rect.bottom, collider_rect.right, collider_rect.top))
        if self.show_collider: pg.draw.rect(SCREEN, red, collider_rect, 3)
        del collider, collider_rect


class NonePlayer(Unit):
    def __init__(self, sprite, pos, speed, name, show_collider): super().__init__(sprite, pos, speed, name,
                                                                                  show_collider)

    def SetRange(self): pass

    def SetPos(self, new_pos):
        self.pos[0] = new_pos[0]
        self.pos[1] = new_pos[1]
        self.SetCollider()
        SCREEN.blit(self.GetSprite(), new_pos)


class Bullet(NonePlayer):
    def __init__(self, sprite, pos, speed, damage, distance, name='unit', show_collider=False):
        super().__init__(sprite, pos, speed, name, show_collider)
        self.damage = damage
        self.range = distance
        self.SetRange(self.range)

    def SetRange(self, distance): self.range = self.pos[0] + distance

    def SetDamage(self, new_damage): self.damage = new_damage

    def GetDamage(self): return self.damage

    def SetPos(self, new_pos):
        self.pos = new_pos
        self.SetCollider()
        SCREEN.blit(self.GetSprite(), new_pos)


class Enemy(NonePlayer):
    def __init__(self, sprite, pos, speed, hp_start=0, hp_end=0, shoot_interval=0, name='unit', show_collider=False, player_y=0):
        super().__init__(sprite, pos, speed, name, show_collider)
        self.hp = rnd.randrange(hp_start, hp_end, 50)
        self.score = 0
        self.SetScore(player_current_upgrades[1])
        self.SetRange()
        self.center = 0
        self.shoot_available = shoot_interval
        self.choice_y = 0 if player_y > self.GetPos()[1] else 1
        self.pivot_x = rnd.randrange(Percentage(screen_width, 50), screen_width - 100)
        if self.shoot_available > 0:
            self.shoot_interval = shoot_interval
            self.max_interval = shoot_interval
            self.can_shoot = False

    def GetChoiceY(self):
        return self.choice_y

    def GetPivotX(self):
        return self.pivot_x

    def GetHp(self):
        return self.hp

    def GetScore(self):
        return self.score

    def GetCenter(self):
        return self.center

    def SetCenter(self, new_center):
        self.center = new_center

    def SetHp(self, damage):
        self.hp -= damage

    def SetScore(self, damage):
        self.score = float(self.hp / damage)

    def SetPos(self, new_pos):
        self.pos = new_pos
        self.SetCollider()
        SCREEN.blit(self.GetSprite(), new_pos)
        if self.shoot_available > 0: self.Shoot(self.GetCenter())

    def SetCollider(self):
        collider = self.sprite.get_rect(topleft=(self.pos))
        new_right = Percentage(collider.width, 40)
        new_bottom = Percentage(collider.height, 30)
        new_left = self.ScaleCollider(collider.left, self.sprite.get_width(), new_right, 40)
        new_top = self.ScaleCollider(collider.top, self.sprite.get_height(), new_bottom, 30)
        collider_rect = pg.Rect(new_left, new_top, new_right, new_bottom)
        self.SetCenter(collider.center)
        self.SetCorners((collider_rect.left, collider_rect.bottom, collider_rect.right, collider_rect.top))
        if self.show_collider: pg.draw.rect(SCREEN, red, collider_rect, 3)
        del collider, collider_rect

    def Shoot(self, pos):
        if self.shoot_interval >= self.max_interval: self.can_shoot = True
        if self.can_shoot:
            self.can_shoot = False
            self.shoot_interval = 0
            self.max_interval = rnd.choice(enemy_shoot_interval)
            enemy_bullet = Bullet('Sprites/laser.png', pos, self.GetSpeed() + 3, 0, 0, 'Enemy_Bullet', True)
            enemy_bullets.append(enemy_bullet)
        self.shoot_interval += 0.5

class PowerUp(NonePlayer):
    def __init__(self, sprite, pos, speed, name, show_collider=False):
        super().__init__(sprite, pos, speed, name, show_collider)
        self.upgrades = []
        self.SetUpgrades(self.upgrades)

    def SetPos(self, new_pos):
        self.pos = new_pos
        self.SetCollider()
        SCREEN.blit(self.GetSprite(), new_pos)

    def SetUpgrades(self, current_upgrades: tuple or list):
        new_upgrades = [0.5, 0, 50, 0.5, 0.1, 5, 5]
        limit = len(new_upgrades) - 2
        self.upgrades = current_upgrades
        for u in range(len(self.upgrades)):
            if u < limit:
                self.upgrades[u] += new_upgrades[u]
            else:
                self.upgrades[u] -= new_upgrades[u]

    def GetUpgrades(self):
        return self.upgrades


# GLOBAL FUNCTIONS ----------------------------------------------------------------------------------------------------

def SetColor():
    global white, black, red, galaxy
    white = (255, 255, 255)
    black = (0, 0, 0)
    red = (255, 0, 0)
    galaxy = (10, 10, 40)
    SCREEN.fill(galaxy)


def DisplayScore(score):
    score_text = score_font.render("SCORE: {0}".format(int(score)), False, white)
    SCREEN.blit(score_text, score_pos)


def DisplayIntro():
    intro_text = intro_font.render('ASTRO-IMPACT', False, white)
    next_text = life_font.render("Press Enter to Play", False, white)
    SCREEN.blit(intro_text, CenterPos(intro_text))
    SCREEN.blit(next_text, (CenterX(next_text), CenterY(next_text) + 100))


def DisplayLife(life):
    level_text = level_font.render("Level 1", False, white)
    life_text = life_font.render("Life: {0}".format(life), False, white)
    life_pos = (Percentage(screen_width, 12), score_pos[1])
    SCREEN.blit(life_text, life_pos)
    SCREEN.blit(level_text, (CenterX(level_text), score_pos[1]))

end_game_delay = 0
end_game_interval = 100
def DisplayStageClear():
    global is_level_finished, next_level_delay, current_level, player_pos_x, is_bg_set, end_boost, target_score_iterator, game_ended, end_game_delay, game_start
    global game_start, game_pause, powerup_avail, current_life, current_score, score_counter
    levelcomplete_text = None
    if current_level < 3:
        levelcomplete_text = intro_font.render('LEVEL {0}  CLEARED'.format(current_level), False, white)
    else:
        levelcomplete_text = intro_font.render('CONGRATULATIONS!', False, white)
        next_text = life_font.render("You Save the Universe", False, white)
        SCREEN.blit(next_text, (CenterX(next_text), CenterY(next_text) + 100))
        if end_game_delay >= end_game_interval:
            game_ended = True
            end_game_delay = 0
            current_timelapse = 0
            game_start, game_pause, powerup_avail, current_life, current_score, score_counter = ResetValues()
        end_game_delay += 1

    border_up = pg.Rect(border_up_pos[0], border_up_pos[1], screen_width, 100)
    border_bot = pg.Rect(border_up_pos[0], border_bot_pos[1], screen_width, 100)

    if border_up.top < 0 and border_bot.bottom > screen_height:
        border_up_pos[1] += 2
        border_bot_pos[1] -= 2
    else:
        border_up_pos[1] = 0
        border_bot_pos[1] = screen_height - 100
    pg.draw.rect(SCREEN, black, border_up)
    pg.draw.rect(SCREEN, black, border_bot)
    SCREEN.blit(levelcomplete_text, CenterPos(levelcomplete_text))

    if next_level_delay >= next_level_interval:
        is_level_finished = False
        current_level += 1
        if target_score_iterator < len(target_score) - 1:
            target_score_iterator += 1
        next_level_delay = 0
        enemy_spawn_delay
        end_boost = 3
        is_bg_set = True
        player_pos_x -= player.GetPos()[0]

    next_level_delay += 0.5


def DisplayGameOver():
    gameover_text = gameover_font.render("GAME OVER!", False, white)
    next_text = life_font.render("Press Enter to Play Again", False, white)
    SCREEN.blit(gameover_text, CenterPos(gameover_text))
    SCREEN.blit(next_text, (CenterX(next_text), CenterY(next_text) + 100))


def Shoot(pos):
    can_shoot = False
    bullet_count_interval = 0
    player_bullet_SFX.play()
    bullet = Bullet('Sprites/laser.png', pos, player_current_upgrades[0], player_current_upgrades[1], player_current_upgrades[2], 'Player_Bullet')
    player_bullets.append(bullet)
    return can_shoot, bullet_count_interval


def SpawnEnemy():
    global enemy_spawn_delay
    if enemy_spawn_delay >= enemy_spawn_interval:
        if len(enemies) < enemy_count and is_player_dead is False and current_timelapse <= min_timelapse and is_level_finished is False:
            range = len(enemy_sprites)
            rand_spawn = None
            if current_level >= 2:
                rand_spawn = rnd.randrange(range)
            else:
                rand_spawn = rnd.randrange(range - 2)

            speed = rnd.choice(enemy1_speed)
            shoot_interval = rnd.choice(enemy_shoot_interval)
            name = 'Enemy'
            # choice_y = rnd.randint(0, 1)

            if rand_spawn == 0: pos = [screen_width, rnd.randrange(0, int(Percentage(screen_height, 8)))]
            elif rand_spawn == 1: pos = [screen_width, rnd.randrange(80, int(Percentage(screen_height, 20)))]
            elif rand_spawn == 2: pos = [rnd.randrange(int(Percentage(screen_width, 45)), int(Percentage(screen_width, 10))), -80]
            elif rand_spawn == 3: pos = [rnd.randrange(int(Percentage(screen_width, 45)), int(Percentage(screen_width, 10))), screen_height + 80]

            enemy = Enemy(enemy_sprites[rand_spawn], pos, speed, 10, 20, shoot_interval, name + str(rand_spawn), False, player.GetPos()[1])
            enemies.append(enemy)
            enemy_spawn_delay = 0
            print('Spawned', enemy.GetName())
    enemy_spawn_delay += 0.5
    # print(enemy_spawn_delay)


def SpawnPlayer():
    global player
    player = Player('Sprites/x-wing(small).png', player_spawn_area, player_current_upgrades[3], 'Player')


def SpawnPowerUp():
    global powerup_obj
    pos = [screen_width, rnd.randrange(20, screen_height)]
    powerup_obj = PowerUp('Sprites/bullet_upgrade.png', pos, powerup_speed, 'PU (Bullet)')


def DestroyObject(object_list, object):
    try:
        if object_list is not None: object_list.remove(object)
        object = None
        del object
    except:
        return


def DestroyPlayer(object_list, collide_target, player_object, player_life, player_dead):
    DestroyObject(object_list, collide_target)
    DestroyObject(None, player_object)
    player_life -= 1
    player_dead = True
    return player_life, player_dead


def MoveEnemies(enemy):
    x, y = enemy.GetPos()[0], enemy.GetPos()[1]
    if x < -80 or y < -80 or y > (screen_height + 80):
        DestroyObject(enemies, enemy)
    else:
        if enemy.GetName() == 'Enemy0':
            x -= enemy.GetSpeed()
        elif enemy.GetName() == 'Enemy1':
            x -= enemy.GetSpeed()
            if x <= enemy.GetPivotX():
                if enemy.GetChoiceY() >= 1:
                    y -= enemy.GetSpeed()
                else:
                    y += enemy.GetSpeed()
        elif enemy.GetName() == 'Enemy2':
            x, y = x - enemy.GetSpeed(), y + enemy.GetSpeed()
        elif enemy.GetName() == 'Enemy3':
            x, y = x - enemy.GetSpeed(), y - enemy.GetSpeed()
        enemy.SetPos((x, y))


def MoveBullet(bullet, bullet_list, max_x, sign='+', condition='>'):
    x, y = bullet.GetPos()[0], bullet.GetPos()[1]
    is_ended = 'x {0} max_x '.format(condition)
    if eval(is_ended) or x > bullet.GetRange():
        DestroyObject(bullet_list, bullet)
    else:
        x = eval('x {0} bullet.GetSpeed()'.format(sign))
        bullet.SetPos((x, y))


def IsCollided(object1, object2): return object1.GetRight() >= object2.GetLeft() and object1.GetBottom() >= object2.GetTop() and object1.GetTop() <= object2.GetBottom() and object1.GetLeft() <= object2.GetRight()


def MovePowerUp(powerup):
    x, y = powerup.GetPos()[0], powerup.GetPos()[1]
    if x < 0:
        DestroyObject(None, powerup)
        return False
    elif IsCollided(player, powerup):
        global player_current_upgrades, player_update
        # TODO New Upgrades is working but not stable
        powerup.SetUpgrades(player_current_upgrades)
        player_current_upgrades = powerup.GetUpgrades()
        player_update = True
        DestroyObject(None, powerup_obj)
        return False
    else:
        x -= powerup.GetSpeed()
        powerup.SetPos((x, y))
        return True
end_rect_scroll_speed = 5
end_rect_scroll_delay = 0
end_rect_scroll_interval = 100
end_rect = pg.Rect(screen_width, 0, screen_width, screen_height)
def Scroll():
    global bg_pos_x, is_bg_set, bg_image, end_rect, end_rect_scroll_speed
    relative_x = bg_pos_x % screen_width
    bg_pos_x -= player_current_upgrades[4]
    if is_bg_set:
        print("is_bg_set", is_bg_set)
        is_bg_set = False
        if current_level == 1:
            bg_image = pg.image.load(bg_image_name[0])
        elif current_level == 2:
            bg_image = pg.image.load(bg_image_name[1])
        else:
            bg_image = pg.image.load(bg_image_name[2])
        bg_image = pg.transform.scale(bg_image, (screen_width, screen_width))
    if relative_x < screen_width:
        SCREEN.blit(bg_image, (relative_x, 0))
    if is_level_finished and end_rect_scroll_delay >= end_rect_scroll_interval:
        pg.draw.rect(SCREEN, red, end_rect)
        end_rect.x -= end_rect_scroll_speed
        end_rect_scroll_speed += 1
    SCREEN.blit(bg_image, (relative_x - screen_width, 0))

def ResetValues():
    global player_current_upgrades, level
    level = 1
    DestroyObject(None, player)
    DestroyObject(None, powerup_obj)
    player_bullets.clear()
    enemy_bullets.clear()
    enemies.clear()
    player_current_upgrades = [player_bullet_speed, player_bullet_damage, player_bullet_range, player_speed,
                               bg_scroll_speed, player_bullet_interval_L, player_bullet_interval_R]
    return False, False, False, 3, 0, 0


def ResetBullets(): return 0, 0, False, False


def LevelFinish():
    # global can_play
    for e in enemies:
        e.SetSpeed(end_boost)
    for b in enemy_bullets:
        b.SetSpeed(end_boost)
    if player.GetPos()[0] >= screen_width:
        DisplayStageClear()
        player_bullets.clear()
        enemy_bullets.clear()
        enemies.clear()
        # can_play = False


def Start():
    global game_start, player_update, game_ended # can_play
    game_start = True
    player_update = True
    game_ended = False
    # can_play = True
    SpawnPlayer()


def Pause():
    pause_text = pause_font.render("PAUSE", True, white)
    SCREEN.blit(pause_text, (50, 50))
    return False


def FixedUpdate():
    global player_bullet_count_interval_L, l_can_shoot, player_bullet_pos_L, l_shooting
    global player_bullet_count_interval_R, r_can_shoot, player_bullet_pos_R, r_shooting
    global player, player_update, player_bullet_height, current_score, score_counter, current_life, game_start
    global player_max_x, player_pos_x, player_pos_y, bg_pos_x, game_pause, powerup_obj, powerup_avail, can_spawn_powerup, is_player_dead
    global enemy_count, enemy_update, enemy_counter, max_score_counter, enemy_counter_limit, score_counter_limit, is_level_finished, end_boost

    if game_start:

        # TODO  Fix the Next Stage Methods
        if current_life <= 0:
            DisplayGameOver()
            game_start, game_pause, powerup_avail, current_life, current_score, score_counter = ResetValues()

        if enemy_counter and score_counter != 0:
            if enemy_count <= max_enemy_count >= enemy_counter_limit:
                if enemy_counter >= enemy_counter_limit and enemy_update is False:
                    enemy_update, enemy_counter = True, 0
                if enemy_update:
                    enemy_count += 1
                    enemy_counter_limit += 1
                    enemy_update = False
            if score_counter <= max_score_counter:
                if score_counter >= score_counter_limit and can_spawn_powerup is False:
                    can_spawn_powerup, score_counter = True, 0
                if can_spawn_powerup:
                    SpawnPowerUp()
                    score_counter_limit += 1
                    can_spawn_powerup = False
                    powerup_avail = True

        SpawnEnemy()

        if powerup_avail:
            powerup_avail = MovePowerUp(powerup_obj)
        if len(enemies) <= 0:
            is_player_dead = False
            player_pos_x -= player.GetPos()[0]
            player_pos_y = 0
            player_bullet_count_interval_L, player_bullet_count_interval_R, l_shooting, r_shooting = ResetBullets()
            if current_timelapse <= min_timelapse:
                SpawnPlayer()

        DisplayScore(current_score)
        DisplayLife(current_life)

        if current_score >= target_score[target_score_iterator]:
            is_level_finished = True
            player_bullet_count_interval_L, player_bullet_count_interval_R, l_shooting, r_shooting = ResetBullets()
            if len(enemies) <= 0:
                if is_level_finished:
                    player_pos_x = end_boost
                    end_boost += 0.5
                    LevelFinish()
        else:
            for b in player_bullets:
                for e in enemies:
                    if IsCollided(b, e):
                        e.SetHp(player_current_upgrades[1])
                        DestroyObject(player_bullets, b)
                    elif e.GetHp() <= 0:
                        DestroyObject(enemies, e)
                        current_score += e.GetScore()
                        enemy_counter += 1
                        if powerup_avail is False:
                            score_counter += 1
                if player_update:
                    player_bullet_height = b.GetHeight()
                    player.SetSpeed(player_current_upgrades[3])
                    player_update = False

                MoveBullet(b, player_bullets, player_max_x)

            for en_b in enemy_bullets:
                for b in player_bullets:
                    if IsCollided(en_b, b):
                        DestroyObject(player_bullets, b)
                        DestroyObject(enemy_bullets, en_b)
                        current_score += 1
                if IsCollided(player, en_b) and not is_player_dead:
                    current_life, is_player_dead = DestroyPlayer(enemies, en_b, player, current_life, is_player_dead)
                MoveBullet(en_b, enemy_bullets, 0, '-', '<')

        for e in enemies:
            if IsCollided(player, e) and not is_player_dead and not is_level_finished:
                current_life, is_player_dead = DestroyPlayer(enemies, e, player, current_life, is_player_dead)
            MoveEnemies(e)

        if not is_player_dead and current_timelapse <= min_timelapse:
            player_bullet_count_interval_L += 1
            player_bullet_count_interval_R += 1
            if player_bullet_count_interval_L >= player_current_upgrades[-2]: l_can_shoot = True
            if player_bullet_count_interval_R >= player_current_upgrades[-1]: r_can_shoot = True
            if l_shooting and l_can_shoot:
                player_bullet_pos_L = player.GetBulletL()
                l_can_shoot, player_bullet_count_interval_L = Shoot(player_bullet_pos_L)
            if r_shooting and r_can_shoot:
                player_bullet_pos_R = player.GetBulletR()
                r_can_shoot, player_bullet_count_interval_R = Shoot(player_bullet_pos_R)

            player.SetPos((player_pos_x, player_pos_y))

    else:
        if game_pause: game_pause = Pause()


def LateUpdate():
    global current_timelapse
    if not is_player_dead:
        if current_timelapse <= min_timelapse:
            current_timelapse = min_timelapse
        else:
            current_timelapse -= 2
    elif is_player_dead:
        if current_timelapse >= max_timelapse:
            current_timelapse = max_timelapse
        else:
            current_timelapse += 3

    pg.display.update()
    clock.tick(current_timelapse)


SetColor()

while running:
    if game_pause is False:
        Scroll()
    if game_ended:
        DisplayIntro()
    else:
        FixedUpdate()
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
            pg.quit()
            sys.exit()

        if is_level_finished is False and is_player_dead is False:
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 1: l_shooting = True
                if event.button == 3: r_shooting = True

            elif event.type == pg.MOUSEBUTTONUP:
                if event.button == 1: l_shooting = False
                if event.button == 3: r_shooting = False

        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN and game_start is False and game_ended: #or can_play is False:
                Start()
            elif event.key == pg.K_ESCAPE and not is_level_finished:
                game_start = not game_start
                game_pause = True

            if game_start and not is_player_dead and not is_level_finished:
                if event.key == pg.K_w:
                    player_pos_y -= player.GetSpeed()
                elif event.key == pg.K_s:
                    player_pos_y += player.GetSpeed()
                elif event.key == pg.K_a:
                    player_pos_x -= player.GetSpeed()
                elif event.key == pg.K_d:
                    player_pos_x += player.GetSpeed()

        elif event.type == pg.KEYUP and not is_player_dead and not is_level_finished:
            if event.key == pg.K_w or pg.K_s: player_pos_y = 0
            if event.key == pg.K_a or pg.K_d: player_pos_x = 0

    LateUpdate()