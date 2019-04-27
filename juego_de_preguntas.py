#!/usr/bin/env python3
import xml.dom.minidom as xmlDom

class Preguntas:
    lista_de_preguntas = list()

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


get_questions()
