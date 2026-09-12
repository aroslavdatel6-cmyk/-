import math
import pygame

pygame.init()

volume = 1.0

text_font = pygame.font.Font(None, 48)
title = text_font.render("Cookie clicker", True, (0, 0, 0))
ingame_title = text_font.render("Click the cookie! :D", True, (255, 255, 255))
settings_volume_text = text_font.render("Volume:", True, (0, 0, 0))


def load_sound(path):
    try:
        return pygame.mixer.Sound(path)
    except (pygame.error, FileNotFoundError):
        return None


Victori3 = load_sound("assets/sounds/Victori3.mp3")
flashbang_explode = load_sound("assets/sounds/flashbang_explode1.mp3")
background_music1 = load_sound("assets/sounds/background_music1.mp3")
background_music2 = load_sound("assets/sounds/background_music2.mp3")
lobby_muccik = load_sound("assets/sounds/lobby_muccik.mp3")
click_sound = load_sound("assets/sounds/click.mp3")


class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.current_color = color

    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_hovered(self, hover_color, normal_color):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos):
            self.current_color = hover_color
        else:
            self.current_color = normal_color

    def is_clicked(self):
        pos = pygame.mouse.get_pos()
        if self.rect.collidepoint(pos) and pygame.mouse.get_pressed()[0]:
            return True
        return False

    def volume_control(self, step):
        global volume
        volume = max(0.0, min(1.0, volume + step))


class Game:
    PLAYLIST_END_EVENT = pygame.USEREVENT + 1

    def handle_click(self, pos):
        """Обработка кликов мышью."""
        if self.cookie.collidepoint(pos):
            if click_sound:
                click_sound.play()
            self.cookies += self.cookies_per_click
            self.target_cookie_scale = 0.8

        
        elif self.upgradeBtn.collidepoint(pos):
            if self.cookies >= self.upgrade1_cost:
                self.cookies -= self.upgrade1_cost
                self.upgrade1_cost *= 2
                self.cookies_per_click += 1

        
        elif self.lika_btn.collidepoint(pos):
            if not self.has_lika:
                if self.cookies >= self.lika_buy_cost:
                    self.cookies -= self.lika_buy_cost
                    self.has_lika = True
                    self.lika_level = 1
                    self.lika_cps = 1
            else:
                if self.cookies >= self.lika_upgrade_cost:
                    self.cookies -= self.lika_upgrade_cost
                    self.lika_level += 1
                    self.lika_cps += 1
                    self.lika_upgrade_cost = max(10, int(self.lika_upgrade_cost * 1.6))

        
        elif self.autoclick_btn.collidepoint(pos):
            if not self.has_autoclick:
                if self.cookies >= self.autoclick_buy_cost:
                    self.cookies -= self.autoclick_buy_cost
                    self.has_autoclick = True
                    self.autoclick_level = 1
                    self.autoclick_cpc = 1
            else:
                if self.cookies >= self.autoclick_upgrade_cost:
                    self.cookies -= self.autoclick_upgrade_cost
                    self.autoclick_level += 1
                    self.autoclick_cpc += 1
                    self.autoclick_upgrade_cost = max(
                        10, int(self.autoclick_upgrade_cost * 1.6)
                    )

    def __init__(self):
        self.cookies = 0
        self.cookies_per_click = 1
        self.cookie_center = (400, 350)
        self.cookie_base_size = 300
        self.cookie_scale = 1.0
        self.target_cookie_scale = 1.0
        self.cookie_anim_speed = 0.15

        self.cookie = pygame.Rect(0, 0, self.cookie_base_size, self.cookie_base_size)
        self.cookie.center = self.cookie_center
        self.cookie_angle = 0

        
        self.upgradeBtn = pygame.Rect(30, 60, 230, 60)
        self.upgrade1_cost = 10

        
        self.lika_btn = pygame.Rect(280, 60, 230, 60)
        self.has_lika = False
        self.lika_level = 0
        self.lika_buy_cost = 20
        self.lika_upgrade_cost = 35
        self.lika_cps = 1
        self.last_lika_time = pygame.time.get_ticks()

        
        self.autoclick_btn = pygame.Rect(530, 60, 240, 60)
        self.has_autoclick = False
        self.autoclick_level = 0
        self.autoclick_buy_cost = 50
        self.autoclick_upgrade_cost = 80
        self.autoclick_cpc = 1
        self.last_autoclick_time = pygame.time.get_ticks()

        
        self.lika_pos = (640, 350)
        self.lika_bounce = 0

        
        try:
            self.lika_image = pygame.image.load(
                "assets/images/lika.png"
            ).convert_alpha()
            self.lika_image = pygame.transform.smoothscale(
                self.lika_image, (100, 100)
            )
        except (pygame.error, FileNotFoundError):
            self.lika_image = None

        self.game_font = pygame.font.Font(None, 20)

        self.gaming_playlist = [s for s in [background_music1, background_music2] if s]
        self.current_song_index = 0
        pygame.mixer.set_reserved(1)
        self.playlist_channel = pygame.mixer.Channel(0)


    def update_autoclicker(self):
        """Автоматический клик каждую секунду от Авто-кликера."""
        if self.has_autoclick:
            now = pygame.time.get_ticks()
            if now - self.last_autoclick_time >= 1000:
                self.cookies += self.autoclick_cpc
                self.target_cookie_scale = 0.85
                self.last_autoclick_time = now

    def update_lika(self):
        """Автоматическое начисление от Лики."""
        if self.has_lika:
            now = pygame.time.get_ticks()
            if now - self.last_lika_time >= 1000:
                self.cookies += self.lika_cps
                self.last_lika_time = now
                self.lika_bounce = 15

        if self.lika_bounce > 0:
            self.lika_bounce -= 1

    def draw_lika(self, surface):
        """Отрисовка Лики."""
        if self.has_lika:
            y_offset = -abs(math.sin(self.lika_bounce * 0.2) * 20)
            render_pos = (self.lika_pos[0], self.lika_pos[1] + y_offset)

            if self.lika_image:
                rect = self.lika_image.get_rect(center=render_pos)
                surface.blit(self.lika_image, rect)
            else:
                pygame.draw.circle(surface, (255, 105, 180), render_pos, 40)
                pygame.draw.circle(
                    surface, (255, 255, 255), (render_pos[0] - 12, render_pos[1] - 10), 8
                )
                pygame.draw.circle(
                    surface, (255, 255, 255), (render_pos[0] + 12, render_pos[1] - 10), 8
                )
                pygame.draw.circle(
                    surface, (0, 0, 0), (render_pos[0] - 12, render_pos[1] - 10), 4
                )
                pygame.draw.circle(
                    surface, (0, 0, 0), (render_pos[0] + 12, render_pos[1] - 10), 4
                )

            lvl_text = self.game_font.render(
                f"Lika Lvl {self.lika_level}", True, (255, 255, 255)
            )
            surface.blit(
                lvl_text, (render_pos[0] - lvl_text.get_width() // 2, render_pos[1] + 45)
            )

    def upgrade(self, surface):
        desc1 = self.game_font.render(
            f"+1 Click (Current: {self.cookies_per_click})", True, (255, 255, 255)
        )
        cost1 = self.game_font.render(
            f"Cost: {self.upgrade1_cost}", True, (255, 255, 255)
        )
        pygame.draw.rect(surface, (0, 170, 255), self.upgradeBtn, border_radius=15)
        surface.blit(desc1, (self.upgradeBtn.x + 10, 70))
        surface.blit(cost1, (self.upgradeBtn.x + 10, 90))

        if not self.has_lika:
            desc2 = self.game_font.render("Buy Lika (+1/s)", True, (255, 255, 255))
            cost2 = self.game_font.render(f"Cost: {self.lika_buy_cost}", True, (255, 255, 255))
            btn_color2 = (255, 105, 180)
        else:
            desc2 = self.game_font.render(
                f"Upgrade Lika (+{self.lika_cps}/s)", True, (255, 255, 255)
            )
            cost2 = self.game_font.render(f"Cost: {self.lika_upgrade_cost}", True, (255, 255, 255))
            btn_color2 = (180, 80, 200)

        pygame.draw.rect(surface, btn_color2, self.lika_btn, border_radius=15)
        surface.blit(desc2, (self.lika_btn.x + 10, 70))
        surface.blit(cost2, (self.lika_btn.x + 10, 90))

        
        if not self.has_autoclick:
            desc3 = self.game_font.render("Buy Auto Clicker", True, (255, 255, 255))
            cost3 = self.game_font.render(f"Cost: {self.autoclick_buy_cost}", True, (255, 255, 255))
            btn_color3 = (50, 205, 50)
        else:
            desc3 = self.game_font.render(
                f"Upgrade Auto Clicker (Lvl {self.autoclick_level})", True, (255, 255, 255)
            )
            cost3 = self.game_font.render(f"Cost: {self.autoclick_upgrade_cost}", True, (255, 255, 255))
            btn_color3 = (34, 139, 34)

        pygame.draw.rect(surface, btn_color3, self.autoclick_btn, border_radius=15)
        surface.blit(desc3, (self.autoclick_btn.x + 10, 70))
        surface.blit(cost3, (self.autoclick_btn.x + 10, 90))

    def draw_score(self, surface):
        display_cookies = text_font.render(
            f"Cookies: {self.cookies}", True, (0, 170, 255)
        )
        surface.blit(display_cookies, (25, 550))

    def victory(self, victory_score):
        return self.cookies >= victory_score

    def music_player(self, song_number):
        songs = [lobby_muccik, background_music1, background_music2]
        if song_number == 1 and songs[0]:
            self.playlist_channel.play(songs[0], loops=-1)
        elif song_number == 2:
            self.start_gaming_playlist()
        elif song_number == 3 and songs[2]:
            self.playlist_channel.play(songs[2], loops=-1)

    def stop_all_music(self):
        for snd in [lobby_muccik, background_music1, background_music2]:
            if snd:
                snd.stop()
        self.playlist_channel.stop()

    def start_gaming_playlist(self):
        if self.gaming_playlist:
            song = self.gaming_playlist[self.current_song_index]
            self.playlist_channel.play(song)
            self.playlist_channel.set_endevent(self.PLAYLIST_END_EVENT)

    def next_gaming_song(self):
        if self.gaming_playlist:
            self.current_song_index = (self.current_song_index + 1) % len(
                self.gaming_playlist
            )
            self.start_gaming_playlist()

    def volume_update(self, new_volume):
        global volume
        volume = max(0.0, min(1.0, new_volume))
        sounds = [
            click_sound,
            background_music1,
            background_music2,
            lobby_muccik,
            Victori3,
            flashbang_explode,
        ]
        for snd in sounds:
            if snd:
                snd.set_volume(volume)

    def update_cookie_anim(self):
        if self.cookie_scale != self.target_cookie_scale:
            diff = self.target_cookie_scale - self.cookie_scale
            if abs(diff) < 0.01:
                self.cookie_scale = self.target_cookie_scale
            else:
                self.cookie_scale += diff * self.cookie_anim_speed

        if self.cookie_scale < 1.0 and self.target_cookie_scale == 0.8:
            self.target_cookie_scale = 1.0

    def cookie_spinning(self):
        self.cookie_angle = (self.cookie_angle + 0.5) % 360

    def render(self, surface, cookie_image=None):
        self.update_lika()
        self.update_autoclicker()
        self.update_cookie_anim()
        self.cookie_spinning()

        scaled_size = max(1, int(self.cookie_base_size * self.cookie_scale))
        self.cookie.size = (scaled_size, scaled_size)
        self.cookie.center = self.cookie_center

        if cookie_image is not None:
            scaled_img = pygame.transform.smoothscale(
                cookie_image, (scaled_size, scaled_size)
            )
            rotated_img = pygame.transform.rotate(scaled_img, self.cookie_angle)
            rotated_rect = rotated_img.get_rect(center=self.cookie.center)
            surface.blit(rotated_img, rotated_rect.topleft)

        self.draw_lika(surface)
        self.draw_score(surface)
        self.upgrade(surface)