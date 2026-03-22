import cv2
import mediapipe as mp
import tkinter
import claviers.clavier as clavier
import claviers.main as main_clavier



class App:
    """ classe principale """

    def __init__(self):
        """ classe qui initialise l'application """
        self.camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)    # la camera
        self.mains = mp.solutions.hands                     # les mains de l'IA
        self.detecteur_mains = self.mains.Hands(            # les parameters de la detection de l'IA
            max_num_hands = 2,
            min_detection_confidence = 0.8,         # l'indice de confiance minimal pour savoir si c'est une main
            min_tracking_confidence = 0.5           # l'indice de confiance minimal pour savoir le type de main
        )

        # variables
        self.en_cours = True
        self.texte = ""
        

        # les instances
        self.clavier = clavier.Clavier()
        self.main_droite = main_clavier.Main("droite")
        self.main_gauche = main_clavier.Main("gauche")


        self.boucle()   # la boucle
        
        self.arreter()  # un arret propre
            




    def boucle(self):
        """ fonction de la boucle principale """
        while self.clavier.en_cours:
            self.texte = ""         # on vide le texte

            reussi, image = self.camera.read()          # on lit l'image de la camera
            image = cv2.flip(image, 1)                  # retourner l'image parce que sinon c chiant


            if not reussi:
                print("une erreur est survenue avec la camera")
                return


            imageRGB = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)   # convertion de l'image du BGR au RGB
            resultat = self.detecteur_mains.process(imageRGB)   # Recuperer les mains


            if not resultat.multi_hand_landmarks: # si on n'a pas de mains
                continue

            for id_main in range(len(resultat.multi_hand_landmarks)):      # on itere les mains

                main = resultat.multi_hand_landmarks[id_main]

                # on detecte le type de main
                if resultat.multi_handedness[id_main].classification[0].label == "Left":
                    # si c'est la main gauche
                    image = self.main_gauche.update(image, main)
                    self.texte += self.main_gauche.touche


                else:
                    # si c'est la droite
                    image = self.main_droite.update(image, main)

                    # la touche
                    self.texte += self.main_droite.touche


            # transmetre les touches
            # si c'est une touche speciale
            if self.texte == "retour":
                self.clavier.supprimer()
            
            # si c'est un texte
            else:
                for lettre in self.texte:
                    self.clavier.touche(lettre)




    
    def arreter(self):
        """ arrete le programme """
        self.camera.release()
        cv2.destroyAllWindows()




App()

