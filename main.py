import game_classes
import pygame

print("Путь к файлу:", game_classes.__file__)
print("Список методов:", dir(game_classes.Game))

pygame.init()

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Cookie Clicker")
clock = pygame.time.Clock()

running = True
gamestate = "menu"
last_gamestate = None
game_difficulty = None
difficulty_screen_ready = True

# Stage flags
stage1 = True
stage2 = False
stage3 = False
final_stage = False
infinite_stage = False

# ================== ЗАГРУЗКА ТЕКСТУР И ФОНОВ ==================
try:
    cookie_image = pygame.image.load(
        "assets/images/Cookie.jpg"
    ).convert_alpha()
except (pygame.error, FileNotFoundError):
    cookie_image = pygame.Surface((300, 300))
    cookie_image.fill((210, 150, 75))

try:
    stage1_background = pygame.transform.scale(
        pygame.image.load("assets/images/stage1.jpg").convert(), (width, height)
    )
    stage2_background = pygame.transform.scale(
        pygame.image.load("assets/images/stage2.jpg").convert(), (width, height)
    )
    stage3_background = pygame.transform.scale(
        pygame.image.load("assets/images/stage3.jpg").convert(), (width, height)
    )
    final_stage_background = pygame.transform.scale(
        pygame.image.load("assets/images/final_stage.jpg").convert(), (width, height)
    )
except (pygame.error, FileNotFoundError):
    stage1_background = pygame.Surface((width, height))
    stage1_background.fill((30, 30, 30))
    stage2_background = pygame.Surface((width, height))
    stage2_background.fill((50, 30, 30))
    stage3_background = pygame.Surface((width, height))
    stage3_background.fill((30, 50, 30))
    final_stage_background = pygame.Surface((width, height))
    final_stage_background.fill((30, 30, 50))

# Create game instance
game = game_classes.Game()

# Menu buttons
play_button = game_classes.Button(300, 200, 200, 50, "Play", (32, 127, 125))
settings_button = game_classes.Button(300, 280, 200, 50, "Settings", (175, 175, 175))
quit_button = game_classes.Button(300, 360, 200, 50, "Quit", (255, 76, 76))
return_button = game_classes.Button(50, 500, 150, 50, "Menu", (255, 76, 76))

# Settings buttons
volumeup_button = game_classes.Button(300, 220, 70, 50, "+", (32, 127, 125))
volumedown_button = game_classes.Button(400, 220, 70, 50, "-", (255, 76, 76))

while running:

    # Music switching
    if gamestate != last_gamestate:
        game.stop_all_music()

        if gamestate == "menu":
            game.music_player(1)
        elif gamestate == "settings":
            game.music_player(1)
        elif gamestate == "playing":
            game.music_player(2)
        elif gamestate in ["victory", "secret_victory"]:
            game_classes.Victori.play()
            game_classes.flashbang_explode.play()

        last_gamestate = gamestate

        if gamestate == "select_difficulty":
            difficulty_screen_ready = False

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == game.PLAYLIST_END_EVENT:
            if gamestate == "playing":
                game.next_gaming_song()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if gamestate == "playing":
                game.handle_click(event.pos)

    game.volume_update(game_classes.volume)

    # ================== MENU ==================
    if gamestate == "menu":
        screen.fill((245, 227, 255))

        screen.blit(
            game_classes.title,
            (width // 2 - game_classes.title.get_width() // 2, 50),
        )

        play_button.draw(screen)
        play_button.is_hovered((153, 175, 213), (32, 127, 125))
        if play_button.is_clicked():
            if game_difficulty is None:
                gamestate = "select_difficulty"
            else:
                gamestate = "playing"
                stage1 = True

        settings_button.draw(screen)
        settings_button.is_hovered((221, 221, 221), (175, 175, 175))
        if settings_button.is_clicked():
            gamestate = "settings"

        quit_button.draw(screen)
        quit_button.is_hovered((255, 172, 172), (255, 76, 76))
        if quit_button.is_clicked():
            running = False

    # ================== PLAYING ==================
    elif gamestate == "playing":

        if stage1:
            screen.blit(stage1_background, (0, 0))
        elif stage2:
            screen.blit(stage2_background, (0, 0))
        elif stage3:
            screen.blit(stage3_background, (0, 0))
        elif final_stage:
            screen.blit(final_stage_background, (0, 0))
        elif infinite_stage:
            screen.fill((255, 255, 255))

        # Stage progression
        if game.cookies >= 1_000_000 and stage1:
            stage1 = False
            stage2 = True
        elif game.cookies >= 50_000_000 and stage2:
            stage2 = False
            stage3 = True
        elif game.cookies >= 5_000_000_000 and stage3:
            stage3 = False
            final_stage = True
        elif (
            game.cookies >= 100_000_000_000
            and final_stage
            and game_difficulty == "infinite"
        ):
            final_stage = False
            infinite_stage = True

        # Victory conditions
        if game_difficulty == "quick":
            if game.victory(1_000_000):
                gamestate = "victory"
        elif game_difficulty == "normal":
            if game.victory(1_000_000_000):
                gamestate = "victory"
        elif game_difficulty == "hard":
            if game.victory(1_000_000_000_000):
                gamestate = "victory"
        elif game_difficulty == "infinite":
            if game.victory(100_000_000_000_000_000_000_000_000):
                gamestate = "secret_victory"

        game.cookie_spinning()

        return_button.draw(screen)
        return_button.is_hovered((255, 172, 172), (255, 76, 76))
        if return_button.is_clicked():
            gamestate = "menu"

        screen.blit(game_classes.ingame_title, (250, 15))
        game.render(screen, cookie_image)

    # ================== VICTORY ==================
    elif gamestate == "victory":
        screen.fill((73, 159, 149))
        victory_text = game_classes.text_font.render(
            "You Win! You can close the game now :)",
            True,
            (255, 255, 255),
        )
        screen.blit(
            victory_text,
            (
                screen.get_width() // 2 - victory_text.get_width() // 2,
                screen.get_height() // 2 - victory_text.get_height() // 2,
            ),
        )

    elif gamestate == "secret_victory":
        screen.fill((89, 0, 255))
        text = game_classes.text_font.render(
            "You found the secret ending! Congrats!",
            True,
            (0, 0, 0),
        )
        screen.blit(
            text,
            (
                screen.get_width() // 2 - text.get_width() // 2,
                screen.get_height() // 2 - text.get_height() // 2,
            ),
        )

    # ================== SELECT DIFFICULTY ==================
    elif gamestate == "select_difficulty":
        screen.fill((255, 187, 71))

        quick_button = game_classes.Button(325, 150, 150, 50, "Quick", (32, 127, 125))
        normal_button = game_classes.Button(325, 250, 150, 50, "Normal", (175, 175, 175))
        hard_button = game_classes.Button(325, 350, 150, 50, "Hard", (255, 76, 76))
        infinite_button = game_classes.Button(
            325, 450, 150, 50, "Infinite", (255, 255, 255)
        )

        quick_button.draw(screen)
        normal_button.draw(screen)
        hard_button.draw(screen)
        infinite_button.draw(screen)

        if not difficulty_screen_ready:
            if not pygame.mouse.get_pressed()[0]:
                difficulty_screen_ready = True
        else:
            if quick_button.is_clicked():
                game_difficulty = "quick"
                stage1 = True
                gamestate = "playing"
            elif normal_button.is_clicked():
                game_difficulty = "normal"
                stage1 = True
                gamestate = "playing"
            elif hard_button.is_clicked():
                game_difficulty = "hard"
                stage1 = True
                gamestate = "playing"
            elif infinite_button.is_clicked():
                game_difficulty = "infinite"
                stage1 = True
                gamestate = "playing"

    # ================== SETTINGS ==================
    elif gamestate == "settings":
        screen.fill((211, 64, 255))

        screen.blit(game_classes.settings_volume_text, (200, 150))
        current_volume_text = game_classes.text_font.render(
            f"{game_classes.volume:.1f}", True, (0, 0, 0)
        )
        screen.blit(current_volume_text, (470, 150))

        return_button.draw(screen)
        return_button.is_hovered((255, 172, 172), (255, 76, 76))
        if return_button.is_clicked():
            gamestate = "menu"

        volumeup_button.draw(screen)
        volumeup_button.is_hovered((153, 175, 213), (32, 127, 125))
        if volumeup_button.is_clicked():
            volumeup_button.volume_control(0.1)

        volumedown_button.draw(screen)
        volumedown_button.is_hovered((255, 172, 172), (255, 76, 76))
        if volumedown_button.is_clicked():
            volumedown_button.volume_control(-0.1)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()