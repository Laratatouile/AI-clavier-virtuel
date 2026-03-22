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

        # les instances
        self.clavier = pynput.keyboard.Controller()
        



    def boucle_quitter(self, touche):
        """ methode qui détecte si on appuie sur la touche pour quitter """
        try:
            if touche == pynput.keyboard.Key.esc:  # si on appuye sur eshap
                print("l'utilisateur a quitte")
                self.en_cours = False
        except:
            pass


    
    def touche(self, touche):
        """ appuye sur une touche """
        self.clavier.press(touche)
        self.clavier.release(touche)


    def supprimer(self):
        """ appuye sur le bouton backspace (effacer) """
        self.clavier.press(pynput.keyboard.Key.backspace)

        