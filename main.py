"""
Spel slutprojekt av Emil
"""
import math
import random
import json
import pygame
from pygame.locals import *
import requests

class FontHandle():
    """
    Hanterar pygame fonts på ett lättare sätt
    """
    def __init__(self, game_class, size = 32) -> None:
        """
        Init method för ett lättare sätt att använda fonts på
        Args:
            game_class (Game): Aktiva game klassen
            size (int): Tecken storlek på fonten
        """
        self.game_class = game_class
        self.font = pygame.font.SysFont("comicsansms", size)
    def draw_text(self, text, color, pos_x, pos_y):
        """
        Ritar ut texten med den färg som anges samt på den position som anges
        Args:
            text (string): Strängen med text som ska skrivas ut
            color (Color): Färgen på texten
            pos_x (int/float): Position på x axeln
            pos_y (int/float): Position på y axeln
        Return:
            None
        """
        temp_render = self.font.render(text, True, color)
        self.game_class.screen.blit(temp_render, (pos_x, pos_y))
    def change_size(self, new_size):
        """
        Ändrar font storlek
        Args:
            new_size (int): nya font storleken
        """
        self.font = pygame.font.SysFont("comicsansms", new_size)

class Vector2d():
    """
    Klass för vector2d, en punkt i ett två dimonsielt system
    """
    def __init__(self, pos_x, pos_y) -> None:
        """
        Init method för en vector 2d
        Args:
            pos_x (int/float): position på x axeln
            pos_y (int/float): position på y axeln
        Return:
            None
        """
        self.pos_x = pos_x
        self.pos_y = pos_y
    def move_by(self, change_x, change_y):
        """
        Method för att flytta spelaren/globen
        
        Args:
            move_by_x (int/float): Hur mycket den ska flyttas på x axeln
            move_by_y (int/float): Hur mycket den ska flyttas på y axeln
        return:
            None
        """
        self.pos_x += change_x
        self.pos_y += change_y
    def get(self):
        """
        Få en tuple med position (pos_x, pos_y)
        """
        return (self.pos_x, self.pos_y)

class Particle(Vector2d):
    """
    En klass för att göra partiklar
    """
    def __init__(self,game_class,pos_x,pos_y,change_x,change_y,radius,color,life_span) -> None:
        """
        Init method för particel
        Args:
            pos_x (int/float): start position på x axeln
            pos_y (int/float): start position på y axeln
            change_x (int/float): Ändring på x axeln varje frame
            change_y (int/float): Ändring på y axeln varje frame
            radius (int/float): Radius på particeln
            color (Color): Färg på particeln
            life_span (int/float): Livslängden på particeln
        """
        super().__init__(pos_x, pos_y)
        self.game_class = game_class
        self.change_x = change_x
        self.change_y = change_y
        self.radius = radius
        self.color = color
        self.life_span = life_span
    def kill(self):
        """
        Tar bort partikeln ifrån partikel listan
        """
        self.game_class.particle_list.remove(self)
    def update(self):
        """
        Uppdaterar partikeln med ny position samt ändrar livs tiden
        """
        if self.life_span > 0:
            self.life_span -= 1
        else:
            self.kill()
        self.move_by(self.change_x, self.change_y)
    def draw(self):
        """
        Ritar ut partikeln på skärmen
        """
        pygame.draw.circle(self.game_class.screen, self.color,
                        (self.pos_x, self.pos_y), self.radius)

class Meteorit(Vector2d):
    """
    En klass som hanterar meteoriter
    """
    def __init__(self, game_class, size, speed) -> None:
        """
        Init method för meteorit
        Args:
            game_class (Game): En game klass så man har tillgång till att rita på skärmen
            size (int/float): Storleken på met
            speed (int/float):
        Return:
            None
        """
        super().__init__(0,0)
        self.game_class = game_class
        meteorit = pygame.image.load("./assets/metriorit.png")
        self.meteorit = pygame.transform.scale(meteorit, (size, size))
        self.set_start_pos()
        self.vinkel = math.atan2(self.pos_y - self.game_class.player.pos_y,
                        self.pos_x - self.game_class.player.pos_x) - math.pi
        self.collision_box = self.meteorit.get_rect()
        self.collision_box.x = self.pos_x
        self.collision_box.y = self.pos_y
        self.speed = speed
    def set_start_pos(self):
        """
        Sätter start positionen utanför skärmen
        """
        # funkar ganska bra
        sides = ["top", "left", "right", "bottom"]
        chosen = random.choice(sides)
        if chosen == "top": # random på x och -100 på y
            self.pos_x = random.randint(-100, self.game_class.screen_size+100)
            self.pos_y = -100
        if chosen == "bottom": # random på x och 100 mer än skärmstorlek på y
            self.pos_x = random.randint(-100, self.game_class.screen_size+100)
            self.pos_y = self.game_class.screen_size + 100
        if chosen == "left": # -100 på x och random på y
            self.pos_x = -100
            self.pos_y = random.randint(-100, self.game_class.screen_size+100)
        if chosen == "right": # 100 mer än skärmstorlek på x och random på y
            self.pos_x = self.game_class.screen_size + 100
            self.pos_y = random.randint(-100, self.game_class.screen_size+100)
    def kill(self):
        """
        Tar bort meteoriten ifrån meteorit listan
        """
        self.game_class.meteorit_list.remove(self) # faktiskt bra funktion
    def draw(self):
        """
        Ritar meteoriten på skärmen
        """
        self.game_class.screen.blit(self.meteorit, (self.pos_x, self.pos_y))
    def update(self):
        """
        Updaterar meteoritens position samt collision box positionen
        """
        # så att den flyttar sig med en vinkel
        self.move_by(self.speed*math.cos(self.vinkel), self.speed*math.sin(self.vinkel))
        self.collision_box.x = self.pos_x
        self.collision_box.y = self.pos_y
        big_screen_size = self.game_class.screen_size+300
        small_screen_size = -300
        if (self.pos_x>big_screen_size or self.pos_y>big_screen_size):
            self.kill()
        if (self.pos_x<small_screen_size or self.pos_y<small_screen_size):
            self.kill()

class Satelit():
    """
    En klass som hanterar sateliter
    """
    def __init__(self, owner, start_vinkel, game_class, speed, max_radius) -> None:
        """
        Init method för satelit
        Args:
            owner (Player): En globe klass som är ägare av sateliten
            start_vinkel (int/float): Start vinkeln som sateliten först har
            game_class (Game): En Game klass så man kan få tillgång till att rita m.m
            speed (int/float): Hastigheten den snurrar med
            max_radius (int/float): En max radius ifrån mitten av owner
        Return:
            None
        """
        satelit = pygame.image.load("./assets/satelit.png")
        self.satelit = pygame.transform.scale(satelit, (20,20))
        self.owner = owner
        self.game_class = game_class
        self.collision_box = self.satelit.get_rect()
        self.pos_x = self.owner.pos_x + self.owner.globe.get_size()[0]/2
        self.pos_y = self.owner.pos_y + self.owner.globe.get_size()[1]/2
        self.vinkel = math.pi/180*start_vinkel
        self.radius = 0
        self.speed = speed
        if speed == 0:
            self.speed = 5
        self.max_radius = max_radius
    def kill(self):
        """
        Method för att döda sateliten
        """
        self.owner.satelit_list.remove(self)
    def draw(self):
        """
        Method för att rita ut satelit
        """
        self.game_class.screen.blit(self.satelit, (self.pos_x, self.pos_y))
    def update(self):
        """
        Method för att uppdatera satelit ska köras varje frame
        """
        # kollision
        for meteorit in self.game_class.meteorit_list:
            if self.collision_box.colliderect(meteorit.collision_box):
                self.kill()
                meteorit.kill()
                for _ in range(5): # 5 partiklar ser mycket ut men är mest slumptal
                    self.game_class.particle_list.append(Particle(self.game_class,
                    self.pos_x, self.pos_y, random.randint(-15, 15)/10,
                    random.randint(-15, 15)/10, 5, (random.randint(230, 255),
                            random.randint(50, 200), 3), random.randint(20, 50)))
                self.game_class.score += 1
        # uppdatera
        if self.radius < self.max_radius:
            self.radius += 0.8
        # cos och sin för att få ny punkt med en vinkel ifrån en punkt
        self.vinkel += math.pi/180*self.speed
        self.pos_x = (self.radius*math.cos(self.vinkel)
                    + self.owner.pos_x + self.owner.globe.get_size()[0]/2
                    - self.satelit.get_size()[0]/2)
        self.pos_y = (self.radius*math.sin(self.vinkel)
                    + self.owner.pos_y + self.owner.globe.get_size()[1]/2
                    - self.satelit.get_size()[1]/2)
        self.collision_box.x = self.pos_x
        self.collision_box.y = self.pos_y

class Player(Vector2d):
    """
    Håller spelarens information
    """
    def __init__(self, game_class) -> None:
        """
        Method för att sätta alla start värden
        Args:
            game_class (Game): Används för att få information från spel klassen
        return:
            None
        """
        super().__init__(game_class.screen_size/2, game_class.screen_size/2)
        self.game_class = game_class
        globe = pygame.image.load("./assets/globe.png")
        self.globe = pygame.transform.scale(globe, (60, 60))
        self.satelit_cool_down = 0
        self.health = 3
        self.satelit_list = []
        self.collision_box = self.globe.get_rect()
        self.round_timer = 0
    def update(self):
        """
        Method för att uppdatera collision box position med mera
        """
        self.collision_box.x = self.pos_x
        self.collision_box.y = self.pos_y
        # kollision
        for meteorit in self.game_class.meteorit_list:
            if self.collision_box.colliderect(meteorit.collision_box):
                meteorit.kill()
                for _ in range(7): # skapa 7 partiklar
                    self.game_class.particle_list.append(Particle(self.game_class,
                        meteorit.pos_x, meteorit.pos_y, random.randint(-15, 15)/10,
                        random.randint(-15, 15)/10, 5, (random.randint(230, 255),
                            random.randint(50, 200), 3), random.randint(20, 50)))
                if self.health > 0: # ändra livet
                    self.health -= 1
                    if self.health <= 0: # spelaren är död
                        self.game_class.send_score(f"Spelare{random.randint(0,1000)}",
                                            self.game_class.score, int(self.round_timer))
                        self.game_class.reset_game()
    def draw(self):
        """
        Method för att rita ut spelaren på skärmen
        """
        self.game_class.screen.blit(self.globe, (self.pos_x, self.pos_y))

class Game():
    """
    En klass som håller spel logik
    """
    def __init__(self) -> None:
        """
        Init method som sätter alla startvärden
        """
        pygame.init()
        pygame.display.set_caption("Satelit spelet")
        self.game_clock = pygame.time.Clock()
        self.is_running = 1
        self.screen_size = 720
        self.screen = pygame.display.set_mode((self.screen_size, self.screen_size))
        self.game_state = 0 # 0 är för leaderboard/start skärm 1 är för själva spelet
        self.meteorit_list = []
        self.meteorit_cool_down = 0
        self.particle_list = []
        self.score = 0
        self.player = Player(self)
        self.leader_board_list = self.get_scores()
    def reset_game(self):
        """
        Method för att starta om spelet
        """
        self.game_state = 0
        self.meteorit_list.clear()
        self.particle_list.clear()
        self.score = 0
        self.player = Player(self)
        self.leader_board_list = self.get_scores()
    def keyboard_input(self):
        """
        Method för att hantera input från tangentbord
        """
        keys = pygame.key.get_pressed()
        if keys[K_SPACE] and self.game_state == 0:
            self.game_state = 1
            return
        if keys[K_w]:
            self.player.move_by(0, -5)
        if keys[K_s]:
            self.player.move_by(0, 5)
        if keys[K_d]:
            self.player.move_by(5, 0)
        if keys[K_a]:
            self.player.move_by(-5, 0)
        if keys[K_SPACE] and self.player.satelit_cool_down <= 0:
            self.player.satelit_list.append(Satelit(self.player,random.randint(0, 360),
                                self, random.randint(-10, 10),random.randint(60, 200)))
            self.player.satelit_cool_down = 60
    def meteorit_spawn_handle(self):
        """
        Method som hanterar när meteoriter ska spawna
        """
        if self.meteorit_cool_down <= 0:
            self.meteorit_list.append(Meteorit(self, random.randint(15, 35), random.randint(2, 10)))
            self.meteorit_cool_down = 60
    def send_score(self, name, score, time):
        """
        Method för att ladda upp ett nytt score
        Args:
            name (string): namnet på spelaren
            score (int): spelarens scrore
            time (int): tiden i sekunder
        """
        # request till dreamlo för leaderboard
        link = "http://dreamlo.com/lb/2zJTVyMJDEulP1XyGMv6XQSaqIMYimQUS2Eh18WIGtag/add/"
        requests.get(f"{link}{name}/{score}/{time}", timeout=10)
        return 0
    def get_scores(self):
        """
        Method för att få hämta informationen ifrån dreamlo leaderboarden
        och sedan formatera den till en lista med json objekt
        Args:
            None
        Return:
            List med json objekt
        """
        req = requests.get("http://dreamlo.com/lb/6447de408f40bb6dec7238e2/json", timeout=10)
        json_form = json.loads(req.text)
        leader_board_list = []
        if json_form["dreamlo"]["leaderboard"] is None:
            return leader_board_list
        count = 0
        # lägger till alla 'entries' i en lista
        for i in json_form["dreamlo"]["leaderboard"]["entry"]:
            leader_board_list.append(i)
            count += 1
        if count == 1:
            leader_board_list = [json_form["dreamlo"]["leaderboard"]]
        return leader_board_list
    def game_loop(self):
        """
        Method för loopen i spelet som sköter allt
        """
        deafult_font = FontHandle(self, 32)
        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = 0
            self.keyboard_input()
            if self.game_state == 0: # om leaderboard
                self.screen.fill((255, 255, 255))
                count = 0
                for leader_board_score in self.leader_board_list:
                    deafult_font.draw_text( # jag vet pylint klagar men kan inte fixa
                        f"{count+1}. {leader_board_score['name']} score: {leader_board_score['score']} time: {leader_board_score['seconds']}",
                        (0,0,0), 50, 35*count+50)
                    count += 1
                deafult_font.draw_text("Press space to start", (50,50,50), 100, 600)
            if self.game_state == 1: # om spelet körs
                self.meteorit_spawn_handle()
                #updates
                for satelit in self.player.satelit_list:
                    satelit.update()
                for meteorit in self.meteorit_list:
                    meteorit.update()
                for particle in self.particle_list:
                    particle.update()
                self.player.update()
                #draw
                self.screen.fill((255, 255, 255))
                self.player.draw()
                for satelit in self.player.satelit_list:
                    satelit.draw()
                for meteorit in self.meteorit_list:
                    meteorit.draw()
                for particle in self.particle_list:
                    particle.draw()
                # gui/text
                deafult_font.draw_text(f"Score: {self.score}", (0,0,0), 10, 10)
                deafult_font.draw_text(f"Time: {int(self.player.round_timer)}", (0,0,0), 200, 10)
                pygame.draw.rect(self.screen, (200, 200, 200), # yttre liv bar
                                pygame.Rect(self.screen_size-3*75-15, 5, 3*75+10, 40))
                pygame.draw.rect(self.screen, (0, 200, 0), # liv bar
                            pygame.Rect(self.screen_size-3*75-10, 10, self.player.health*75, 30))

                # cooldowns
                if self.meteorit_cool_down > 0:
                    self.meteorit_cool_down -= 1
                if self.player.satelit_cool_down > 0:
                    self.player.satelit_cool_down -= 1
                self.player.round_timer += (1000/60)/1000 # 1000/fps = ms => ms/1000 = sekund |timer
            pygame.display.flip()
            self.game_clock.tick(60)

if __name__ == "__main__": # kolla så duktig
    GAME = Game()
    GAME.game_loop()
