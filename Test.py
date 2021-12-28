import sys
import pygame as pg


pg.init()
player_pos_y = 0
player_pos_x = 0
player_speed = 50
running = True
clock = pg.time.Clock()
SCREEN = pg.display.set_mode((500, 500))
lerp_font = pg.font.Font("Font/azonix.otf", 50)

def Lerp(startFloat: float, endFloat: float, time: float = 0.33, debug=True):
    # if startFloat >= endFloat:
    #     startFloat = endFloat
    # if debug:
    #     print(startFloat)
    return float("{:.2f}".format(startFloat + time * (endFloat - startFloat)))

def DisplayLerp(current_x, current_y: tuple or list):
    lerp_text = lerp_font.render("{0}, {1}".format(current_x, current_y), False, (255, 255, 255))
    SCREEN.blit(lerp_text, (50, 40))


keys = [False, False, False, False]
while running:
    SCREEN.fill((0, 0, 0))
    # if keys[0]:
    #     player_pos_y -= Lerp(player_pos_y, player_speed)
    # elif keys[1]:
    #     player_pos_y += Lerp(player_pos_y, player_speed)
    # elif keys[2]:
    #     player_pos_x -= Lerp(player_pos_x, player_speed)
    # elif keys[3]:
    #     player_pos_x += Lerp(player_pos_x, player_speed)
    # elif keys[0] is False or keys[1]:
    #     player_pos_y -= Lerp(player_speed, 0)
    for event in pg.event.get():
        # print("EVENT")
        if event.type == pg.QUIT:
            running = False
            pg.quit()
            sys.exit()
        if event.type == pg.KEYDOWN:
            print("Pressed")
            if event.key == pg.K_w:
                player_pos_y -= Lerp(player_pos_y, player_speed)
                # keys[0] = True
            if event.key == pg.K_s:
                player_pos_y += Lerp(player_pos_y, player_speed)
                # keys[1] = True
            if event.key == pg.K_a:
                player_pos_x -= Lerp(player_pos_x, player_speed)
            if event.key == pg.K_d:
                player_pos_x += Lerp(player_pos_x, player_speed)
        elif event.type == pg.KEYUP:
            print("Released")
            # if event.key == pg.K_w:
            #     keys[0] = False
            # elif event.key == pg.K_s:
            #     keys[1] = False
            # elif event.key == pg.K_a:
            #     keys[2] = False
            # elif event.key == pg.K_d:
            #     keys[3] = False
            if event.key == pg.K_a or pg.K_d: player_pos_x = 0
            if event.key == pg.K_w or pg.K_s: player_pos_x = 0



    DisplayLerp(player_pos_x, player_pos_y)
    pg.display.update()
    clock.tick(10)