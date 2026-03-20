import cv2
import math
import time

class Main:
    """ classe qui gere le mouvement des doigts de la main """

    def __init__(self, type_main:str):
        """ initialise le clavier """

        self.type_main = type_main

        # liste des points du landmark pour les extremites des doigts
        self.doigts = [8, 12, 16, 20]

        # dictionnaire pour savoir quelle touche a ete utilisee
        if type_main == "gauche":
            self.touches = {
                "bas": {0: "b", 1: "v", 2: "c", 3: "x", 4: "w"},
                "milieu": {0: "g", 1: "f", 2: "d", 3: "s", 4: "q"},
                "haut": {0: "t", 1: "r", 2: "e", 3: "z", 4: "a"},
               "tres_haut": {0: "5", 1: "4", 2: "3", 3: "2", 4: "1"}
            }
            
        else:
            self.touches = {
                "bas": {0: "n", 1: ",", 2: ";", 3: ";", 4: ":"},
                "milieu": {0: "h", 1: "j", 2: "k", 3: "l", 4: "m"},
                "haut": {0: "y", 1: "u", 2: "i", 3: "o", 4: "p"},
                "tres_haut": {0: "6", 1: "7", 2: "8", 3: "9", 4: "0"}
            }


        # listes pour les etats des doigts
        self.est_haut = [False for _ in range(4)]
        self.est_haut_permisif = [False for _ in range(4)]
        self.est_en_bas = [False for _ in range(4)]

        # vitesse de la main pour eviter d'appuyer quand on bouge la main entiere
        self.vitesse_main = 0.0
        self.position_main = [0, 0]

        # SEUILS
        self.SEUIL_MAIN = 0.1
        self.SEUIL_BAS = 0.1
        self.SEUIL_HAUTEUR = 0.065
        self.SEUIL_HAUTEUR_PERMISIF = 0.04
        self.SEUIL_POUCE = 0.03
        self.SEUIL_DECALAGE_INDEX = 0.1
        self.SEUIL_SUPPRIMER = 0.37

        # pour le texte
        self.DELAY_TOUCHES = 0.45
        self.derniere_touches_tps = time.time()



    def update(self, img, main):
        
        self.touche = ""

        for point in main.landmark:
            h, w, c = img.shape
            cx, cy = int(point.x*w), int(point.y*h)

            cv2.circle(img, (cx, cy), 4, (255, 0, 0), cv2.FILLED)



        # calculer la vitesse de la main globale
        if self.position_main == [0, 0]:
            self.position_main = [main.landmark[0].x, main.landmark[0].y]

        self.vitesse_main = self.pythagore(self.position_main, main.landmark[0])
        self.position_main = [main.landmark[0].x, main.landmark[0].y]



        # si la vitesse de la main est elevee on ne cherche meme pas si on appuye sur une touche
        if self.vitesse_main > self.SEUIL_MAIN:
            return img
        
        # si on a appuye trop recement sur une touche (couldown)
        if time.time() - self.derniere_touches_tps < self.DELAY_TOUCHES:
            return img




        # pour chaque doigt on vas calculer si on le tend ou pas
        for id_d, doigt in enumerate(self.doigts):
            # detecter si on est tendu ou pas

            # le non permisif
            if main.landmark[doigt -2].y > main.landmark[doigt].y + self.SEUIL_HAUTEUR + (0 if doigt not in [20, 8] else 0.01):
                self.est_haut[id_d] = True
                self.est_haut_permisif[id_d] = True
            
            # le permisif pour etre large
            elif main.landmark[doigt -2].y > main.landmark[doigt].y + self.SEUIL_HAUTEUR_PERMISIF + (0 if doigt not in [20, 8] else 0.03):
                self.est_haut[id_d] = False
                self.est_haut_permisif[id_d] = True
            
            # si le doigt n'est pas vers le haut
            else:
                self.est_haut[id_d] = False
                self.est_haut_permisif[id_d] = False




        # pour chaque doigt on vas calculer si on l'a mis vers le bas ou pas
        for id_d, doigt in enumerate(self.doigts):
            if self.distance_y(main.landmark[0], main.landmark[doigt]) < self.SEUIL_BAS:
                self.est_en_bas[id_d] = True
            else:
                self.est_en_bas[id_d] = False




        # detecter si on veux supprimer une touche
        if (self.type_main == "droite" and
            self.pythagore(main.landmark[0], main.landmark[20]) > self.SEUIL_SUPPRIMER and
            self.est_en_bas.count(True) == 0 and
            self.est_haut.count(True) == 1):
            self.touche = "retour"
            self.derniere_touches_tps = time.time()
            return img


        # detecter si on appuye sur une touche (rangee bas)
        if self.est_en_bas.count(False) == 3:
            id_doigt_bas = self.est_en_bas.index(True) # detecter l'identifiant du doigt qui appuye

            # detecter si on n'est pas avec l'index si on appuye sur les touches a droite
            if not (id_doigt_bas == 0 and self.distance_x(main.landmark[8], main.landmark[12]) > self.SEUIL_DECALAGE_INDEX - 0.02):
                id_doigt_bas += 1

            self.touche = self.touches["bas"][id_doigt_bas] # ajouter la touche au texte
            self.derniere_touches_tps = time.time() # mettre le temps auquel on a appuye sur la touche (pour le couldown)


        # detecter si on appuye sur une touche (rangee milieu)
        elif self.est_haut_permisif.count(True) == 3:
            id_doigt_haut = self.est_haut.index(False) # detecter l'identifiant du doigt qui appuye

            # detecter si on n'est pas avec l'index si on appuye sur les touches a droite
            if not (id_doigt_haut == 0 and self.distance_x(main.landmark[8], main.landmark[12]) > self.SEUIL_DECALAGE_INDEX):
                id_doigt_haut += 1

            self.touche = self.touches["milieu"][id_doigt_haut] # ajouter la touche au texte
            self.derniere_touches_tps = time.time() # mettre le temps auquel on a appuye sur la touche (pour le couldown)


        # detecter si on appuye sur une touche (rangee haut)
        elif self.est_haut.count(True) == 1:
            id_doigt_haut = self.est_haut.index(True) # detecter l'identifiant du doigt qui appuye

            # detecter si on n'est pas avec l'index si on appuye sur les touches a droite
            if not (id_doigt_haut == 0 and self.distance_x(main.landmark[8], main.landmark[12]) > self.SEUIL_DECALAGE_INDEX):
                id_doigt_haut += 1
            
            self.touche = self.touches["haut"][id_doigt_haut] # ajouter la touche au texte
            self.derniere_touches_tps = time.time() # mettre le temps auquel on a appuye sur la touche (pour le couldown)

        
        # detecter si le pouce est vers le bas alors on appuye sur espace
        elif main.landmark[0].y < main.landmark[4].y + self.SEUIL_POUCE:
            self.touche = " " # ajouter espace au texte
            self.derniere_touches_tps = time.time() # mettre le temps auquel on a appuye sur la touche (pour le couldown)

        
        return img


    def distance_y(self, point_1, point_2) -> float:
        """ calcule la distance entre deux points en y """
        return abs(point_2.y - point_1.y)
    
    def distance_x(self, point_1, point_2) -> float:
        """ calcule la distance entre deux points en x """
        return abs(point_2.x - point_1.x)
    

    def pythagore(self, point_1, point_2) -> float:
        """ calcule la distance entre deux points """
        try:
            x_1 = point_1.x
            y_1 = point_1.y
        except:
            x_1 = point_1[0]
            y_1 = point_1[1]

        return math.sqrt((point_2.x - x_1) ** 2 + (point_2.y - y_1) **2)
    


    def text(self, img, text):
        """ affiche un texte """
        cv2.putText(img, text, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)