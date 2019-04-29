#!/usr/bin/env python3
import xml.dom.minidom as xmlDom
import pygame
import sys
import time
import RPi.GPIO as GPIO

#Tiempo de espera antes de quitar la imagen de correcto o incorrecto
#modifica este valor para esperar más o menos tiempo, el valor es en segundos
tiempo_de_espera = 3

#Posición en la que se muestra la entrada que introduce el usuario
input_position = (100, 100)
#Ajusta este número para cambiar el tamaño de la fuente
font_size = 72

#Número de pin en que se encuentra el relevador A
relay_a_pin = 5

#Número de pin que se encuentra el relevador B
relay_b_pin = 7

#COLUMNAS
COL0 = 37
COL1 = 36
COL2 = 38
COL3 = 40

#FILAS
ROW0 = 29
ROW1 = 31
ROW2 = 33
ROW3 = 35

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
        self.screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        self.pregunta_background = 0
        w,h = pygame.display.get_surface().get_size()
        self.font = pygame.font.SysFont("comicsansms", font_size)
        self.text = self.font.render("Hello", True, (200, 200, 200))
        self.width = w
        self.height = h
        self.correct_img = pygame.image.load("./img/correcto.png")
        self.incorrect_img = pygame.image.load("./img/incorrecto.png")

    def Load_new_image(self, numero_de_pregunta):
        nombre_de_fondo = Preguntas.lista_de_preguntas[numero_de_pregunta].getElementsByTagName("Background")[0].getAttribute("file_name")

        try:
            self.pregunta_background = pygame.image.load("./img/" + nombre_de_fondo)
            self.pregunta_background = pygame.transform.scale(self.pregunta_background, (self.width, self.height))
            print(nombre_de_fondo)

        except pygame.error:
            self.pregunta_background = pygame.image.load("./img/default.jpg")
        self.Show_new_background()

    def Show_correct_image(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.correct_img,(0,0))
        pygame.display.update()

    def Show_incorrect_image(self):
        self.screen.fill((0,0,0))
        self.screen.blit(self.incorrect_img,(0,0))
        pygame.display.update()

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
        self.text = self.font.render(texto, True, (0,0,0))
        self.screen.blit(self.text, input_position)
        pygame.display.update()

class Keypad_matrix:
    def __init__(self):
        self.MATRIX = [	['1','2','3','A'],
    				['4','5','6','B'],
    				['7','8','9','C'],
    				['*','0','#','D']]

        self.rows = [ROW0,ROW1,ROW2,ROW3]
        self.cols = [COL0,COL1,COL2,COL3]

        self.contador_de_columnas = 0
        self.contador_de_filas = 0

        self.last_key_pushed = 0
        self.new_key_pushed = 0

        self.last_column = 10
        self.last_row = 10
        self.keypad_is_free = True

        for columna in range(0, len(self.cols)):
            GPIO.setup(self.cols[columna], GPIO.OUT)
            GPIO.output(self.cols[columna], GPIO.HIGH)
        for fila in range(0, len(self.rows)):
            GPIO.setup(self.rows[fila], GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def scan_keyboard(self):
        send_info = False
        for columna in range(0, len(self.cols)):
            GPIO.output(self.cols[columna], GPIO.LOW)
            for fila in range(0, len(self.rows)):
                key_pushed = GPIO.input(self.rows[fila])

                #Cuando presionan una tecla del teclado, el resultaod es falso
                if key_pushed == False:
                    if self.keypad_is_free == True:
                        self.new_key_pushed = self.MATRIX[fila][columna]

                        if self.new_key_pushed is not self.last_key_pushed:
                            self.keypad_is_free = False
                            #print(self.MATRIX[fila][columna])
                            send_info = True

                        self.last_key_pushed = self.new_key_pushed
                        self.last_column = columna
                        self.last_row = fila

                else:
                    if self.last_row == fila and self.last_column == columna:
                        self.last_key_pushed = 0
                        self.new_key_pushed = 0
                        self.keypad_is_free = True

                time.sleep(0.01)
            GPIO.output(self.cols[columna], GPIO.HIGH)
        if send_info == True:
            send_info = False
            return self.new_key_pushed
        else:
            return 0

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

def init_gpio():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(relay_a_pin, GPIO.OUT)
    GPIO.setup(relay_b_pin, GPIO.OUT)
    GPIO.output(relay_a_pin, GPIO.LOW)
    GPIO.output(relay_b_pin, GPIO.LOW)


def main():
    #Lleva el conteo de cuantas preguntas ya se mostraron en pantalla
    numero_de_pregunta = 0

    pygame.init()
    _display = Display()
    done = False
    clock = pygame.time.Clock()
    user_answer = ""
    _display.Load_new_image(numero_de_pregunta)

    init_gpio()

    _keypad = Keypad_matrix()

    Done = False
    while True:
        key_pressed = _keypad.scan_keyboard()

        if key_pressed is not 0:
            #print("nueva tecla presionada")
            #print(ord(key_pressed))
            if key_pressed == '*':
                #print("Tecla de aceptar")
                correcto = Preguntas.CheckAnswer(user_answer, numero_de_pregunta)

                if correcto == True:
                    #Mostramos la imagen que corresponde a correcto
                    _display.Show_correct_image()

                    #Se aumenta la pregunta en 1, para permitir que se muestre el nuevo background y que
                    #se evalue la respuesta del usuario con la siguiente pregunta
                    numero_de_pregunta += 1
                    if numero_de_pregunta == len(Preguntas.lista_de_preguntas) - 2:
                        GPIO.output(relay_a_pin, GPIO.HIGH)
                    elif numero_de_pregunta == len(Preguntas.lista_de_preguntas) - 1:
                        GPIO.output(relay_b_pin, GPIO.HIGH)
                    #mostramos la nueva imagen en la pantalla

                else:
                    _display.Show_incorrect_image()

                time.sleep(tiempo_de_espera)

                if numero_de_pregunta == len(Preguntas.lista_de_preguntas):
                    GPIO.output(relay_a_pin, GPIO.LOW)
                    GPIO.output(relay_b_pin, GPIO.LOW)
                    numero_de_pregunta = 0
                    user_answer = ""

                _display.Load_new_image(numero_de_pregunta)
                user_answer = ""

            else:
                user_answer += key_pressed
                _display.Show_user_input(user_answer)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            if event.type == pygame.K_ESCAPE:
                sys.exit()
            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                #Cuando la tecla presionada no es igual a "Enter", se actualiza la pantalla
                if event.key is not pygame.K_RETURN:
                    key = key.capitalize()
                    user_answer += key
                    _display.Show_user_input(user_answer)
                #En caso contrario, analizamos la respuesta con la que está guardada en el archivo xml
                else:
                    #La función CheckAnswer devuelve verdadero cuando la respuesta es correcta
                    #devuelve falso cuando la respuesta es incorrecta
                    correcto = Preguntas.CheckAnswer(user_answer, numero_de_pregunta)

                    if correcto == True:
                        #Mostramos la imagen que corresponde a correcto
                        _display.Show_correct_image()

                        #Se aumenta la pregunta en 1, para permitir que se muestre el nuevo background y que
                        #se evalue la respuesta del usuario con la siguiente pregunta
                        numero_de_pregunta += 1
                        if numero_de_pregunta == len(Preguntas.lista_de_preguntas) - 1:
                            GPIO.output(relay_a_pin, GPIO.HIGH)
                        elif numero_de_pregunta == len(Preguntas.lista_de_preguntas):
                            GPIO.output(relay_b_pin, GPIO.HIGH)
                        #mostramos la nueva imagen en la pantalla

                    else:
                        _display.Show_incorrect_image()

                    time.sleep(tiempo_de_espera)
                    _display.Load_new_image(numero_de_pregunta)
                    user_answer = ""

        if numero_de_pregunta == len(Preguntas.lista_de_preguntas):
            GPIO.output(relay_a_pin, GPIO.LOW)
            GPIO.output(relay_b_pin, GPIO.LOW)
            numero_de_pregunta = 0
            user_answer = ""
        clock.tick(60)

if __name__ == '__main__':
    get_questions()
    try:
        main()
    finally:
        GPIO.cleanup()
