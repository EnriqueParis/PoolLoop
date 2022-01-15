#=======================================================
# CODIGO DE VIDEOJUEGO DE POOL
# Nombre de juego: PoolLoop
# Hecho por: Enrique Jose Paris Cardenas - 1er Semestre
#=======================================================

from tkinter import *
import math
import random

def start():
    """
    Descripcion: Es el primer procedimiento que el programa llama automaticamente. Crea la root del Tk,
    y los botones para iniciar el juego, "Nuevo juego" y "Cargar partida".
    """
    global master,  bootButton, loadButton
    name = str(input("Escriba su nombre: ")) #Para que el usuario introduzca su nombre

    master = Tk()
    
    nameDpl = Label(master, text="USUARIO: " + name) #Widget que muestra en pantalla el nombre del usuario
    nameDpl.pack()

    bootButton = Button(master, text="Nuevo juego", command=create_variables) #Boton para empezar un nuevo juego
    bootButton.pack()
    loadButton = Button(master, text="Cargar juego", command=cargarJuego) #Boton para cargar un juego de un archivo
    loadButton.pack()

    master.mainloop()

def create_variables():
    """
    Descripcion: Procedimiento donde se crean todas las variables para el juego, que luego se referencian y manipulan en otros eventos.
    """
    global master, bolaTarget, canvas, bootButton, loadButton, STOP, cargando, pause, ballX, ballY, size, power, direction, ball, xspeed, yspeed, ballText, ballStripe, numeroGolpes, lineaTrayectoria, barraPoder, p, golpesDisplay, movingBalls, pocketedBalls, puntaje, puntajeDisplay, pocketedConsecutivas
    canvas = Canvas(master, width=947, height=564, bg="black")
    canvas.pack()

    #Pack.forget() se usa para quitar los botones de pantalla
    bootButton.pack_forget()
    loadButton.pack_forget()
    
    STOP = True #Esta variable indica cuando el juego se detiene para que el jugador golpee la bola blanca.
                #Cuando es True, el jugador puede cuadrar la direccion de la bola.
    
    cargando = False #Esta variable es True cuando la barra para cargar la potencia del tiro aparece.
    pause = False #Indica que el juego termina, ya sea por perdida y victoria antes del limite de golpe.
    
    #### Las listas ballX y ballY controlan la posicion X e Y. El index es correspondiente al numero de la bola
    #### La posicion 0 en ambas listas son los datos de la bola blanca, y la posicion 1 son los datos de la bola 1, etc.
    ballX = [260,615,767,653,691,691,767,729,729,729,729,767,767,767,653,691]
    ballY = [260,260,260,280,260,222,184,240,202,280,318,222,298,336,240,298]
    
    #### IDs para los canvas.create en el evento paint()
    ball = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #Guarda la ID de los dibujos de cada bola. Las posiciones son correspondientes.
    ballText = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0] #Guarda la ID del numero de cada bola.
    ballStripe = {'9':0, '10':0, '11':0, '12':0, '13':0, '14':0, '15':0} #Guarda la ID de los rectangulos de color de las bolas 9 en adelante.
    
    size = 16 #Radio de las bolas
    power = 0 #Poder con el que se golpea la bola blanca
    p = 1 #Es un interruptor que causa el cambio en incremento y descenso de power, cuando el jugador carga el tiro
    direction = 0 #El angulo de tiro, que el jugador controla con 'a' y 'd'.
    
    ### xspeed e yspeed manejan la velocidad horizontal y vertical. Son correspondientes al numero de la bola
    xspeed = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    yspeed = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    movingBalls = [] #Lista a la que se le agregan los numeros de las bolas que se estan moviendo
                        #Se usa para saber cuando detener los movimientos para que el jugador pueda usar el taco de nuevo.
    pocketedBalls=[] #Lista de las bolas que han sido introducidas en los bolsillos. Agregar las 15 bolas a esta lista hace ganar el juego.
    puntaje = 0 #Puntos del jugador: la suma de las bolas introducidas por el jugador
    puntajeDisplay = Label(master, text = "Puntaje: "+str(puntaje)) #Muestra el puntaje en pantalla
    puntajeDisplay.pack()
    pocketedConsecutivas = 0 #Lleva la cuenta de cuantas bolas han sido introducidas consecutivamente
                            #Al llegar a tres, se le regala un golpe adicional al jugador.
    bolaTarget = 1
    
    ### Imagen de la mesa de billar
    table = PhotoImage(file="poolTable.gif")
    field = canvas.create_image(473,262,image=table)
    labelRef = Label(image=table) #Guardar referencia de la imagen GIF en una widget aparte para que Python no la borre.
    labelRef.image = table

    numeroGolpes = 25 #Numero de golpes que el jugador tiene. Al llegar a cero, el juego termina.
    
    lineaTrayectoria = 0 #ID de la linea blanca que indica el angulo de tiro
    barraPoder = [0,0] #En [0] guarda la ID del rectangulo marco de la barra de poder. En [1] guarda la ID de la barra roja de que indica el poder

    golpesDisplay = Label(master, text = "Golpes: " + str(numeroGolpes)) #Muestra los golpes restantes en pantalla
    golpesDisplay.pack()

    saveButton = Button(master, text="Guardar partida", command = guardarJuego) #Boton para guardar el juego.
    saveButton.pack()
    
    master.bind('<Key>', accionKey) #Comando para ejecutar cuando el jugador presiona una tecla.

    paint()
    step()

def step():
    """
    Descripcion: Procedimiento que se ejecuta en cada paso del juego. 
    """
    global ballX, ballY, bolaTarget, size, power, direction, ball, xspeed, yspeed, gspeed, master,  p, STOP, pause, cargando, movingBalls, puntaje, puntajeDisplay, pocketedBalls
    #==========================================================#
    # ACCIONES A EJECUTAR CADA PASO CUANDO LAS BOLAS SE MUEVEN #
    #==========================================================#
    if STOP == False and pause == False:                         
        for i in range(len(ballX)): #Para cada bola
            if i not in pocketedBalls: #Este 'if' se usa para no hacer calculos para bolas que estan fuera de la mesa
                ##Mover la bola en los ejes x y Y tantos pixeles como sea su velocidad
                ballX[i] = ballX[i] + xspeed[i]
                ballY[i] = ballY[i] + yspeed[i]
                ##Disminuir progresivamente la velocidad en cada eje
                xspeed[i] = xspeed[i]/1.01
                yspeed[i] = yspeed[i]/1.01

                ##Si se sigue dividiendo las velocidad, se disminiyen infinitamente sin llegar a cero.
                ##Esto fuerza que se detengan por completo.
                if abs(xspeed[i]) < 0.08:
                    xspeed[i] = 0
                if abs(yspeed[i]) < 0.08:
                    yspeed[i] = 0

                #Cuando la bola entra en los agujeros
                if (ballX[i] < 70 and ballY[i] < 75) or (ballX[i] < 70 and ballY[i] > 440) or (int(ballX[i]) in range(440,500) and (ballY[i]-size < 50 or ballY[i]+size > 465)) or (ballX[i]>870 and ballY[i]<80) or (ballX[i]>870 and ballY[i]>440):
                    pocketing(i)
                else:
                    #El rebote de la bola con los limites de la mesa
                    if (ballX[i]-size < 50 or ballX[i]+size > 895) and (ballY[i] > 80 and ballY[i]<440):
                        xspeed[i] = -xspeed[i]
                        ballX[i] = ballX[i] + xspeed[i]
                    if (ballY[i]-size < 50 or ballY[i]+size > 470) and (ballX[i] > 72 and ballX[i]<865) and (int(ballX[i]) not in range(440,500)):
                        yspeed[i] = -yspeed[i]
                        ballY[i] = ballY[i] + yspeed[i]
                #Agregar la bola a la lista de bolas moviles si se esta moviendo
                if (xspeed[i] != 0 or yspeed[i] != 0) and (i not in movingBalls):
                    movingBalls.append(i)
                #Sacar la bola de la lista si se dejo de mover
                elif (xspeed[i] == 0 and yspeed[i] == 0) and (i in movingBalls):
                    movingBalls.remove(i)
        #=======================#
        #DETECCION DE COLISIONES#
        #=======================#
        for a in range(len(ballX)):
            if a not in pocketedBalls:
                for b in range(a,len(ballX)):
                    if b not in pocketedBalls:
                        ## Las cuatro condiciones que se cumplen cuando dos bolas estan en proximidad para colisionar
                        if ballX[a] + size*2 > ballX[b] and ballX[a] < ballX[b] + size*2 and ballY[a] + size*2 > ballY[b] and ballY[a] < ballY[b] + size*2:
                            distancia = math.sqrt((ballX[a]-ballX[b])**(2) + (ballY[a]-ballY[b])**(2))
                            if distancia <= size*(2) + 3:
                                collision(a,b)

        #=============================================#
        #FIN DE LA JUGADA, LAS BOLAS DEJAN DE MOVERSE=#
        #=============================================#
        if len(movingBalls) == 0:
            STOP = True #Habilita la preparacion del golpe a la bola blanca
            if numeroGolpes == 0: #Derrota cuando al jugador se le acaban los golpes
                pause = True
                texto_final = canvas.create_text(473,262,justify=CENTER, text="HAS PERDIDO \n Numero de golpes agotado. Puntaje: "+str(puntaje))
            if verSiPocket == False: #Si en ese golpe no entro ninguna bola
                                    #se resetea el contador de bolas introducidas consecutivamente
                pocketedConsecutivas = 0
                
            if 0 in pocketedBalls: #Cuando la bola blanca entra en un hoyo
                pocketedBalls.remove(0)
                ballX[0] = 260
                ballY[0] = 260
                ##El ciclo a continuacion es para intentar posicionar la bola blanca en la linea horizontal
                ##media de la mesa, verificando en cada ocasion que no colisione con una bola que ya este ahi
                done = False 
                while (done == False):
                    for b in range(1,len(ballX)):
                        if ballX[0] + size*2 > ballX[b] and ballX[0] < ballX[b] + size*2 and ballY[0] + size*2 > ballY[b] and ballY[0] < ballY[b] + size*2:
                            ballX[0] = ballX[0] + 50
                            break
                        elif b == len(ballX)-1:
                            done = True
                ##Al entrar la bola blanca, se regresa a la mesa la ultima bola introducida (si hay una),
                ## en una posicion aleatoria.
                if len(pocketedBalls) != 0:
                    penalty = pocketedBalls.pop(len(pocketedBalls)-1)
                    puntaje = puntaje - penalty
                    ballX[penalty] = random.randint(100,850)
                    ballY[penalty] = random.randint(100,430)
                    done = False
                    while(done==False):
                        for b in range(len(ballX)):
                            if penalty != b:
                                if ballX[penalty] + size*2 > ballX[b] and ballX[penalty] < ballX[b] + size*2 and ballY[penalty] + size*2 > ballY[b] and ballY[penalty] < ballY[b] + size*2:
                                    ballX[penalty] = random.randint(100,850)
                                    ballY[penalty] = random.randint(100,430)
                                    break
                                elif b == len(ballX)-1:
                                    done = True
                    if bolaTarget > penalty:
                        bolaTarget = penalty
    #==================================#
    #CUANDO EL JUGADOR PREPARA EL TIRO #
    #==================================#
    else:
        ## Hacer subir y bajar la carga de potencia despues de que el jugador presiona J
        if cargando == True:
            if power > 920:
                p = -1
            elif power < 1:
                p = 1
            power = power + 5*p

    paint() #Redibuja todos los objetos en cada paso
    puntajeDisplay['text'] = "Puntaje: "+str(puntaje) #Actualiza el puntaje en pantalla

    master.after(15,step) #Repite el mismo evento step, con tal de que se vuelva recursivo.

def paint():
    """
    Descripcion: Dibuja en el canvas todos los objetos necesarios para visualizar el juego
    """
    global canvas,ball,ballX,ballY,size,ballText, power, direction, barraPoder, lineaTrayectoria, STOP, cargando, pause, pocketedBalls
#====================================================#
# ELIMINA LOS DIBUJOS ANTERIORES DE TODOS LOS OBJETOS#
#====================================================#
    canvas.delete(lineaTrayectoria)
    canvas.delete(barraPoder[0])
    canvas.delete(barraPoder[1])
    for i in (range(len(ballX))):
        if i not in pocketedBalls:
            canvas.delete(ball[i])
            canvas.delete(ballText[i])
            #========================================================================#
            #Para cada bola, dibuja su circulo, numero, y raya de color(si la tiene);#
            #de acuerdo al numero de la bola. Los 'ifs' estan para darle a cada bola#
            #su color y numero correspondiente                              #
            #===============================================================#
            if i > 8:
                canvas.delete(ballStripe[str(i)])
            if i == 0:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
            elif i == 1:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="yellow")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="1", fill="black", justify=CENTER)
            elif i == 2:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="blue")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="2", fill="white", justify=CENTER)
            elif i == 3:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="red")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="3", fill="white", justify=CENTER)
            elif i == 4:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="purple")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="4", fill="white", justify=CENTER)
            elif i == 5:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="orange")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="5", fill="black", justify=CENTER)
            elif i == 6:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="green")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="6", fill="white", justify=CENTER)
            elif i == 7:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="brown")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="7", fill="white", justify=CENTER)
            elif i == 8:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="black")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="8", fill="white", justify=CENTER)
            elif i == 9:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
                ballStripe[str(i)] = canvas.create_rectangle(ballX[i]-size/1.5,ballY[i]-size/2,ballX[i]+size/1.5,ballY[i]+size/2, outline="white", fill="yellow")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="9", fill="black", justify=CENTER)
            elif i == 10:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
                ballStripe[str(i)] = canvas.create_rectangle(ballX[i]-size/1.5,ballY[i]-size/2,ballX[i]+size/1.5,ballY[i]+size/2, outline="white", fill="blue")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="10", fill="white", justify=CENTER)
            elif i == 11:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
                ballStripe[str(i)] = canvas.create_rectangle(ballX[i]-size/1.5,ballY[i]-size/2,ballX[i]+size/1.5,ballY[i]+size/2, outline="white", fill="red")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="11", fill="white", justify=CENTER)
            elif i == 12:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
                ballStripe[str(i)] = canvas.create_rectangle(ballX[i]-size/1.5,ballY[i]-size/2,ballX[i]+size/1.5,ballY[i]+size/2, outline="white", fill="purple")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="12", fill="white", justify=CENTER)
            elif i == 13:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
                ballStripe[str(i)] = canvas.create_rectangle(ballX[i]-size/1.5,ballY[i]-size/2,ballX[i]+size/1.5,ballY[i]+size/2, outline="white", fill="orange")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="13", fill="black", justify=CENTER)
            elif i == 14:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
                ballStripe[str(i)] = canvas.create_rectangle(ballX[i]-size/1.5,ballY[i]-size/2,ballX[i]+size/1.5,ballY[i]+size/2, outline="white", fill="green")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="14", fill="white", justify=CENTER)
            elif i == 15:
                ball[i]=canvas.create_oval(ballX[i]-size,ballY[i]-size, ballX[i]+size,ballY[i]+size, fill="white")
                ballStripe[str(i)] = canvas.create_rectangle(ballX[i]-size/1.5,ballY[i]-size/2,ballX[i]+size/1.5,ballY[i]+size/2, outline="white", fill="brown")
                ballText[i]=canvas.create_text(ballX[i],ballY[i],text="15", fill="white", justify=CENTER)

    if STOP == True and pause == False: #Los dibujos de la linea de direccion del tiro, y la barra de poder.
        lineaTrayectoria = canvas.create_line(ballX[0],ballY[0], 900*math.cos(math.radians(direction))+ballX[0], 900*math.sin(math.radians(direction))+ballY[0], width=4, fill="white")
        if cargando == True:
            barraPoder[0] = canvas.create_rectangle(10,530,937,560,fill="white")
            barraPoder[1] = canvas.create_rectangle(11,531,11+power,559,fill="red",outline="white")


def collision(A , B):
    """
    Descripcion: Procedimiento que calcula las velocidades resultantes de dos bolas que colisionan.
    Entrada: Dos numeros enteros, que son los indices de las bolas que colisionan.
    Salida: Las velocidades de las bolas cambian de acuerdo a los calculos hechos.
    """
    global ballX, ballY, xspeed, yspeed
    distancia_enx = ballX[A] - ballX[B]
    distancia_eny = ballY[A] - ballY[B]
    collisionAngle = math.atan2(distancia_eny,distancia_enx) #Angulo de colision
    speed0 = math.sqrt(xspeed[A]**2 + yspeed[A]**2) #Vector general de la velocidad para cada bola
    speed1 = math.sqrt(xspeed[B]**2 + yspeed[B]**2)

    ang = [0,0]
    ang[0] = math.atan2(yspeed[A],xspeed[A]) #Los angulos de direccion de la bolas
    ang[1] = math.atan2(yspeed[B],xspeed[B])

    #Para los calculos, la velocidad en los ejes de cada bola deben ajustarse a un nuevo eje x y Y,
    #que se obtiene restandole el angulo que se forma entre las dos bolas.
    xspeed0_neweje = speed0* math.cos(ang[0]-collisionAngle)
    yspeed0_neweje = speed0* math.sin(ang[0]-collisionAngle)
    xspeed1_neweje = speed1* math.cos(ang[1]-collisionAngle)
    yspeed1_neweje = speed1* math.sin(ang[1]-collisionAngle)

    #Evidencia el intercambio de velocidades
    newXspeed0 = xspeed1_neweje
    newXspeed1 = xspeed0_neweje
    newYspeed0 = yspeed0_neweje
    newYspeed1 = yspeed1_neweje

    #Formula de fisica/mecanica para determinar la nueva velocidad en los distintos ejes para cada bola
    xspeed[A] = (math.cos(collisionAngle)*newXspeed0)+(math.cos(collisionAngle+math.pi/2)*newYspeed0)
    yspeed[A] = (math.sin(collisionAngle)*newXspeed0)+(math.sin(collisionAngle+math.pi/2)*newYspeed0)
    xspeed[B] = (math.cos(collisionAngle)*newXspeed1)+(math.cos(collisionAngle+math.pi/2)*newYspeed1)
    yspeed[B] = (math.sin(collisionAngle)*newXspeed1)+(math.sin(collisionAngle+math.pi/2)*newYspeed1)

def accionKey(event):
    """
    Descripcion: Evento que se ejecuta cada vez que el jugador presiona una tecla.
    Entrada: Tecla presionado.
    """
    global STOP, cargando, direction, power, numeroGolpes, golpesDisplay, verSiPocket
    #==================================#
    #COMANDOS CUANDO SE PREPARA EL TIRO#
    #==================================#
    if STOP == True:
        if cargando == False:
            #Cuando se esta moviendo la direccion del tiro
            if event.char == "d":
                direction = direction + 2
            elif event.char == "a":
                direction = direction - 2
            if event.char == 'j': #Comenzar a cargar el tiro
                cargando = True
        else: #El presionar 'j' de nuevo para que la barra de poder se detenga, y golpear la bola.
            if event.char == 'j':
                xspeed[0] = (power/80)*math.cos(math.radians(direction))
                yspeed[0] = (power/80)*math.sin(math.radians(direction))

                numeroGolpes = numeroGolpes - 1
                golpesDisplay['text'] = numeroGolpes
                verSiPocket = False
                STOP = False
                cargando = False
                power = 0

def pocketing(B):
    global pocketedBalls, bolaTarget, puntaje, pocketedConsecutivas, ball, ballText, ballStripe, xspeed, yspeed, verSiPocket, numeroGolpes
    """
    Descripcion: Procedimiento que ocurre cuando una bola es introducida en un hoyo.
    Entrada: Numero entero que es el indice de la bola introducida.
    """
    if B != 0:
        pocketedBalls.append(B)
        if bolaTarget == B:
            puntaje = puntaje + B
            while (bolaTarget in pocketedBalls):
                bolaTarget = bolaTarget + 1
        pocketedConsecutivas = pocketedConsecutivas + 1
        verSiPocket = True
        xspeed[B] = 0
        yspeed[B] = 0

        canvas.delete(ball[B])
        canvas.delete(ballText[B])
        if B > 8:
            canvas.delete(ballStripe[str(B)])

        if pocketedConsecutivas == 3:
            pocketedConsecutivas = 0
            numeroGolpes = numeroGolpes + 1

        if len(pocketedBalls) == 15:
            STOP = True
            pause = True

            texto_final = canvas.create_text(473,262,justify=CENTER, text="HAS GANADO \n Golpes restantes: "+str(numeroGolpes))

    else:
        pocketedBalls.append(B)
        xspeed[B] = 0
        yspeed[B] = 0
        canvas.delete(ball[B])
        canvas.delete(ballText[B])

def guardarJuego():
    global STOP, cargando, bolaTarget, pause, ballX, ballY, pocketedBalls, puntaje, numeroGolpes, pocketedConsecutivas
    """
    Descripcion: Procedimiento que guarda el estado actual del juego en un archivo. txt, para ser cargado al reejecutar el juego.
    """
    if STOP == True and cargando == False and pause == False:
        save = open("poolloop_save.txt", mode='w')
        for i in range(len(ballX)):
            save.write(str(ballX[i]))
            save.write(',')
        save.write('\n')
        for i in range(len(ballY)):
            save.write(str(ballY[i]))
            save.write(',')
        save.write('\n')

        for i in range(len(pocketedBalls)):
            save.write(str(pocketedBalls[i]))
            save.write(',')
        save.write('\n')

        save.write(str(puntaje))
        save.write('\n')

        save.write(str(numeroGolpes))
        save.write('\n')

        save.write(str(pocketedConsecutivas))
        save.write('\n')
        save.write(str(bolaTarget))
        save.close()

def cargarJuego():
    global master, canvas, bolaTarget, bootButton, loadButton, STOP, cargando, pause, ballX, ballY, size, power, direction, ball, xspeed, yspeed, ballText, ballStripe, numeroGolpes, lineaTrayectoria, barraPoder, p, golpesDisplay, movingBalls, pocketedBalls, puntaje, puntajeDisplay, pocketedConsecutivas
    """
    Descripcion: Procedimiento para cargar un juego anterior.
    """
    save = open("poolloop_save.txt",mode='r')
    ballX = []
    ballY = []
    pocketedBalls = []

    lines = save.readlines()
    tmp = ""

    for i in lines[0]:
        if i != '\n':
            if i == ',':
                tmp = float(tmp)
                ballX.append(tmp)
                tmp = ""
            else:
                tmp = tmp + i
    tmp = ""
    for i in lines[1]:
        if i != '\n':
            if i == ',':
                tmp = float(tmp)
                ballY.append(tmp)
                tmp = ""
            else:
                tmp = tmp + i
    tmp = ""
    for i in lines[2]:
        if i != '\n':
            if i == ',':
                tmp = float(tmp)
                pocketedBalls.append(tmp)
                tmp = ""
            else:
                tmp = tmp + i

    puntaje = ""
    for i in lines[3]:
        if i != '\n':
            puntaje = puntaje + i
    puntaje = int(puntaje)
    
    numeroGolpes = ""
    for i in lines[4]:
        if i != '\n':
            numeroGolpes = numeroGolpes + i
    numeroGolpes = int(numeroGolpes)
    
    pocketedConsecutivas = int(lines[5][0])
    bolaTarget = ""
    for i in lines[6]:
        if i != '\n':
            bolaTarget = bolaTarget + i
    bolaTarget = int(bolaTarget)
    
    save.close()

    canvas = Canvas(master, width=947, height=564, bg="black")
    canvas.pack()

    bootButton.pack_forget()
    loadButton.pack_forget()
    
    STOP = True
    cargando = False
    pause = False
    
    ball = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ballText = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    ballStripe = {'9':0, '10':0, '11':0, '12':0, '13':0, '14':0, '15':0}
    size = 16
    power = 0
    p = 1
    direction = 0
    xspeed = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    yspeed = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]

    movingBalls = []
    
    puntajeDisplay = Label(master, text = "Puntaje: "+str(puntaje))
    puntajeDisplay.pack()
    
    table = PhotoImage(file="poolTable.gif")
    field = canvas.create_image(473,262,image=table)
    labelRef = Label(image=table)
    labelRef.image = table
    
    lineaTrayectoria = 0
    barraPoder = [0,0]

    golpesDisplay = Label(master, text = "Golpes: " + str(numeroGolpes))
    golpesDisplay.pack()

    saveButton = Button(master, text="Guardar partida", command = guardarJuego)
    saveButton.pack()
    
    master.bind('<Key>', accionKey)

    paint()
    step()
    
start()

    

