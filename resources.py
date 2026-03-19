import pygame, sys, random

class Cell:
    def __init__(self, x, y, etat=False):
        self.x = x
        self.y = y
        self.etat = etat

    def set_etat(self):
        self.etat = not self.etat # False de base, on change l'état de la cellule ici pour qu'elle devienne True si elle est vivante et vice versa

class Grille:
    def __init__(self, largeur, hauteur):
        self.largeur = largeur
        self.hauteur = hauteur
        self.cells = [[Cell(x, y) for x in range(largeur)] for y in range(hauteur)]

    def get_voisins(self, x, y):
        voisins = []
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0: # Evite la duplication de la cellule centrale dans le tab voisins
                    continue
                if 0 <= x + i < self.largeur and 0 <= y + j < self.hauteur: # Condition pour éviter que les voisins soient en dehors de la grille
                    voisins.append(self.cells[y + j][x + i])
        return voisins

    def set_voisins(self):
        new_grille = [[Cell(x, y) for x in range(self.largeur)] for y in range(self.hauteur)]
        for y, ligne in enumerate(self.cells): # enumerate renvoie un tuple avec l'indice et la valeur de la cellule
            for x, cell in enumerate(ligne):
                voisins = self.get_voisins(x, y)
                voisins_vivante = sum(1 for voisin in voisins if voisin.etat) # Calcule la somme de toutes les cellules vivantes dans le tableau voisins grace à sum
                if cell.etat:
                    if voisins_vivante < 2 or voisins_vivante > 3: # Si une cellule vivante a moins de 2 voisins vivants ou plus de 3, elle meurt
                        new_grille[y][x].etat = False
                    else:
                        new_grille[y][x].etat = True
                else:
                    if voisins_vivante == 3: # Si une cellule morte a exactement 3 voisins vivants, elle devient vivante
                        new_grille[y][x].etat = True
        self.cells = new_grille

    def randomize(self):
        for _, ligne in enumerate(self.cells):
            for _, cell in enumerate(ligne): # Pour chaque cellule dans la grille, on lui attribue un état aléatoire
                    cell.etat = random.choice([True, False, False]) 
                
class JeuDelaVie:
    def __init__(self, taille_cellule):
        info = pygame.display.Info()
        self.largeur = info.current_w-320
        self.hauteur = info.current_h
        self.taille_cellule = taille_cellule
        self.grille = Grille(self.largeur // self.taille_cellule, self.hauteur // self.taille_cellule)
        self.screen = pygame.display.set_mode((info.current_w, info.current_h))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Jeu de la vie")
        pygame.surface.Surface.fill(self.screen, (20, 20, 20))
        self.FPS = 5
        self.patterns = []
        self.cont = False # variable pour créer un toggle sur une touche
        self.hold = None
        
    def draw_grille(self):
         for y, ligne in enumerate(self.grille.cells):
            for x, cell in enumerate(ligne):
                couleur = (255, 255, 255) if cell.etat else (0, 0, 0)
                pygame.draw.rect(self.screen, couleur, ((x * self.taille_cellule)+1, (y * self.taille_cellule)+1, self.taille_cellule-2, self.taille_cellule-2)) 
    
    def enregistrer_pattern(self):
        pattern = []
        for y, ligne in enumerate(self.grille.cells):
            for x, cell in enumerate(ligne):
                if cell.etat:
                    pattern.append((x, y))
        self.patterns.append(pattern)
        print(f"Pattern enregistré: {pattern}")

    def sauvegarder_patterns(self, nom_fichier):
        with open(nom_fichier, 'w') as fichier:
            for pattern in self.patterns:
                fichier.write(','.join(f'{x}:{y}' for x, y in pattern) + '\n')
        self.patterns = []
        
    def charger_patterns(self, nom_fichier):
        self.patterns = []
        with open(nom_fichier, 'r') as fichier:
            for ligne in fichier:
                pattern = []
                for cell in ligne.strip().split(','): # strip sert à enlever les espaces et split à séparer les coordonnées x et y
                    x, y = cell.split(':')
                    pattern.append((int(x), int(y)))
                self.patterns.append(pattern)
        self.grille = Grille(self.largeur // self.taille_cellule, self.hauteur // self.taille_cellule)
        for pattern in self.patterns:
            for x, y in pattern:
                self.grille.cells[y][x].etat = True
        self.patterns = []

    def menu(self):
        font = pygame.font.SysFont("Courier New", 24)

        pygame.draw.rect(self.screen, (0, 0, 0), (self.largeur, 0, 320, self.hauteur))

        def print_text(text, pos):
            text = font.render(text, True, (255, 255, 255))
            textRect = text.get_rect()
            textRect.center = pos
            self.screen.blit(text, textRect)

        print_text("ESPACE : Start/Stop", (self.largeur+160, 50))
        print_text("A : Grille aléatoire", (self.largeur+160, 100))
        print_text("R : RÉinitialisation", (self.largeur+160, 150))
        print_text("Z : Augmente les FPS", (self.largeur+160, 200))
        print_text("S : Diminue les FPS", (self.largeur+160, 250))
        print_text("D : Prochaine génération", (self.largeur+160, 300))
        print_text(f'FPS: {self.FPS}', (self.largeur+160, 350))
        
        vivante = 0
        for ligne in (self.grille.cells):
            for cell in (ligne):
                if cell.etat:
                    vivante += 1
        print_text(f"Cellules vivantes: {vivante}", (self.largeur+160, 400))

        if self.cont:
            pygame.display.set_caption("Jeu de la vie - Simulation en cours")
        else:
            pygame.display.set_caption("Jeu de la vie - Simulation arrêté")
    
    def jouer(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    keep_fps = self.FPS
                    self.FPS = 0
                    self.cont = False
                    pos_x, pos_y = pygame.mouse.get_pos()
                    if pos_x > self.largeur or pos_y > self.hauteur:
                        continue
                    cell_x = pos_x // self.taille_cellule
                    cell_y = pos_y // self.taille_cellule
                    cell = self.grille.cells[cell_y][cell_x]
                    self.hold = 1 if cell.etat else 0

                elif event.type == pygame.MOUSEBUTTONUP:
                    self.FPS = keep_fps
                    self.hold = None
    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.cont = not self.cont

                    if event.key == pygame.K_r: # Reset
                        self.grille = Grille(self.largeur // self.taille_cellule, self.hauteur // self.taille_cellule)

                    if event.key == pygame.K_z: # Fps
                        if self.FPS < 60:
                            self.FPS = self.FPS+2
                        else:
                            self.FPS = 60
                    if event.key == pygame.K_s:
                        if self.FPS > 1:
                            self.FPS = self.FPS-2
                        else:
                            self.FPS = 1

                    if event.key == pygame.K_d:
                        self.grille.set_voisins()
                        self.draw_grille()

                    if event.key == pygame.K_a:
                        self.grille.randomize()
                        self.draw_grille()

                    if event.key == pygame.K_i:  # Touche pour enregistrer le pattern
                        self.enregistrer_pattern()

                    if event.key == pygame.K_o:  # Touche pour sauvegarder les patterns
                        self.sauvegarder_patterns(input("Nom du fichier en .txt: \n"))

                    if event.key == pygame.K_p:  # Touche pour charger les patterns
                        self.charger_patterns(input("Nom du fichier en .txt: \n"))


            if self.cont: # Lance la simulation lorsque espace est pressé et l'arrête lorsqu'il est pressé à nouveau
                self.grille.set_voisins()

            if self.hold != None:
                self.cont = False
                pos_x, pos_y = pygame.mouse.get_pos()
                if pos_x > self.largeur or pos_y > self.hauteur:
                    continue
                cell_x = pos_x // self.taille_cellule
                cell_y = pos_y // self.taille_cellule
                cell = self.grille.cells[cell_y][cell_x]
                cell.etat = True if self.hold == 0 else False
                print(f"Cellule cliquée: {cell.x}, {cell.y}, {'vivante' if cell.etat else 'morte'}")
            self.draw_grille()

            self.menu()
            pygame.display.update()
            self.clock.tick(self.FPS)

        pygame.quit()
        sys.exit()