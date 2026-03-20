import pynput



class Clavier:
    """ classe qui gere la detection et l'appui sur les touches """

    def __init__(self):
        """ initialise la classe """
        # variables pas modifiables
        self.en_cours = True
        detecteur_touches = pynput.keyboard.Listener(
            on_press=self.boucle_quitter)
        detecteur_touches.start()
        



    def boucle_quitter(self, key):
        """ methode qui détecte si on appuie sur la touche pour quitter """
        try:
            if key == pynput.keyboard.Key.esc:  # si on appuye sur eshap
                print("l'utilisateur a quitte")
                self.en_cours = False
        except:
            pass