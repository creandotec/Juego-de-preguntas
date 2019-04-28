#!/usr/bin/env python3
import xml.dom.minidom as xmlDom
import pygame
import sys
class Preguntas:
    lista_de_preguntas = list()
    answer = list()
    answer.append("1")
    user_chosen_option = "1"

    def CheckAnswer(user_answer, numero_de_pregunta):
        correc_answer = Preguntas.lista_de_preguntas[numero_de_pregunta].getAttribute("ans")
        if correc_answer == user_answer:
            print("Ok")
            return True
        else:
            return False

class Display:
    def __init__(self):
        self.screen = pygame.display.set_mode((0,0))
        self.pregunta_background = 0
        w,h = pygame.display.get_surface().get_size()
        self.font = pygame.font.SysFont("comicsansms", 72)
        self.text = self.font.render("Hello", True, (200, 200, 200))
        self.width = w
        self.height = h

    def Load_new_image(self, numero_de_pregunta):
        nombre_de_fondo = Preguntas.lista_de_preguntas[numero_de_pregunta].getElementsByTagName("Background")[0].getAttribute("file_name")
        try:
            self.pregunta_background = pygame.image.load(nombre_de_fondo)
            self.pregunta_background = pygame.transform.scale(self.pregunta_background, (self.width, self.height))
            print(nombre_de_fondo)

        except pygame.error:
            self.pregunta_background = pygame.image.load("./default.jpg")
        self.Show_new_background()

    def Show_new_background(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.pregunta_background, (0,0))
        pygame.display.update()

    def Show_chosen_answer(self, chosen_answer,numero_de_pregunta):
        opciones = Preguntas.lista_de_preguntas[numero_de_pregunta].getElementsByTagName("Opcion")
        texto = "no existe esa opción"
        for opcion in opciones:
            if opcion.getAttribute("tecla") == chosen_answer:
                texto = opcion.getAttribute("texto")
                print(texto)
                print("Econtrado")
                break
            else:
                print(opcion.getAttribute("tecla"))
                print(chosen_answer)
        self.text = self.font.render(texto, True, (0,0,0))
        self.screen.blit(self.text, (100,100))
        pygame.display.update()

    def Show_user_input(self, user_input):
        texto = ""
        texto += user_input
        self.text = self.font.render(texto, True, (255,255,255))
        self.screen.blit(self.text, (100, 100))
        pygame.display.update()
#Aquí configuramos las preguntas que se utilizarán durante el juego
def get_questions():
    #Primero abrimos el documento XML en donde están las Preguntas
    DOMTree = xmlDom.parse("preguntas_conf.xml")
    collection = DOMTree.documentElement
    #Verificamos que la raíz tenga el tag correcto.
    if collection.tagName == "Preguntas":
        Preguntas.lista_de_preguntas = collection.getElementsByTagName("Pregunta")

        for pregunta in Preguntas.lista_de_preguntas:
            print("La pregunta es {}".format(pregunta.getAttribute("Title")))
    else:
        print("No está funcionando bien el script {}".format(collection.tagName))

def main():
    #Lleva el conteo de cuantas preguntas ya se mostraron en pantalla
    numero_de_pregunta = 0

    pygame.init()
    _display = Display()
    done = False
    clock = pygame.time.Clock()
    user_answer = ""
    _display.Load_new_image(numero_de_pregunta)
    Done = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                if event.key is not pygame.K_RETURN:
                    key = key.capitalize()
                    user_answer += key
                    _display.Show_user_input(user_answer)
                else:
                    correcto = Preguntas.CheckAnswer(user_answer, numero_de_pregunta)
                    if correcto == True:
                        numero_de_pregunta += 1
                        _display.Load_new_image(numero_de_pregunta)
                    user_answer = ""

                #En correcto se almacena si la respuesta elegida es correcta o no
                #correcto = Preguntas.CheckAnswer(key, numero_de_pregunta)
                #Aumentamos en uno el número de pregunta para pasar a la siguiente
                #numero_de_pregunta += 1
                #if correcto == True:
        if numero_de_pregunta > len(Preguntas.lista_de_preguntas):
            sys.exit()
        clock.tick(60)

if __name__ == '__main__':
    get_questions()
    main()
