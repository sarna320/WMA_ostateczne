"---------------------------------------------------------------------------------------------------------------------"
import cv2
import numpy as np
import urllib.request
"---------------------------------------------------------------------------------------------------------------------"
#funckja zwraca obraz mozliwy do przetwarzania przez opencv, ktory zostal pobrany z githuba
#argumentem wejsciowym jest numer linku
def zwrocObrazGithub(i):
    # url zdjec z githuba
    url = ["https://github.com/sarna320/WMA_ostateczne/blob/dziala/mix.jpg?raw=true",
           "https://github.com/sarna320/WMA_ostateczne/blob/dziala/mix2.jpg?raw=true",
           "https://github.com/sarna320/WMA_ostateczne/blob/dziala/srebne.jpg?raw=true"]

    # wgranie zdjecia
    url_response = urllib.request.urlopen(url[i])

    # przekonwertowanie zdjecia do formatu odowiedniego dla opencv
    obraz = cv2.imdecode(np.array(bytearray(url_response.read()), dtype=np.uint8), -1)

    # zmniejszenie
    obraz = cv2.pyrDown(obraz)

    return obraz
"---------------------------------------------------------------------------------------------------------------------"
#funckja do drukowania obrazu
#argumentem wejsciowym jest nazwa okna i obraz do pokazania
def drukujObraz(nazwa,obraz):
    # pokazanie obrazu
    cv2.imshow(nazwa, obraz)
    cv2.waitKey()
    cv2.destroyAllWindows()
"---------------------------------------------------------------------------------------------------------------------"
#funckja zwraca obraz z wszystkimi wykrytymi nominalami na zdjeciu, gdzie tlo zamieniane jest na czarny kolor
#argumentem wejsciowym jest obraz z monetami
def wszyskieNominaly(obraz):
    # konwersja na skale szarosci
    gray = cv2.cvtColor(obraz, cv2.COLOR_BGR2GRAY)

    # pozbycie sie szumow
    blur = cv2.GaussianBlur(gray, (17, 17), 0)

    # znalezienie wszystkich nominalow param2=odleglosc
    circles = cv2.HoughCircles(blur, cv2.HOUGH_GRADIENT, 1, 50, param1=50, param2=30, minRadius=25, maxRadius=45)
    circles = np.uint16(np.around(circles))  # potrzebne bo kod nie dziala

    # Tworzenie maski
    mask = np.zeros(obraz.shape[:2], np.uint8)

    # rysowanie kołek na masce
    for i in circles[0, :]:
        mask = cv2.circle(mask, (i[0], i[1]), i[2], 255, -1)

    # przemaskowanie
    obraz[mask!=255]=0
    return obraz
"---------------------------------------------------------------------------------------------------------------------"
#funkcja zwraca 2 obrazy: 1-zlote monety, 2-srebne monety. Oba na czarnym tle
#argumentem wejsciowym jest obraz z monetami gdzie tlo czarne
def rodziel(obraz):
    # wartosci do maski dla zlotych monet, dobrane eksperymentalnie
    zloty = (0, 70, 0)
    zloty2 = (250, 250, 250)

    # przejscie na HSV
    obraz_HSV = cv2.cvtColor(obraz.copy(), cv2.COLOR_RGB2HSV)

    # stworzenie maski dla zlotych monet
    maska_zlota = cv2.inRange(obraz_HSV, zloty, zloty2)

    # obraz z samymi zlotymi monetami
    obraz_zloty = cv2.bitwise_and(wszystkie, wszystkie, mask=maska_zlota)

    # konwersja na skale szarosci
    gray_zloty = cv2.cvtColor(obraz_zloty, cv2.COLOR_BGR2GRAY)

    # znalezienie wszystkich nominalow o kolorze zlotym param2=odleglosc
    circles = cv2.HoughCircles(gray_zloty, cv2.HOUGH_GRADIENT, 1, 50, param1=50, param2=30, minRadius=20, maxRadius=45)

    #trzeba sprawdzic czy wogole znalazlo zlote monety.
    """W tym miejscu byl dosyc spory problem, mianowicie dla najnowszej wersji pythona byl blad ze wartosc ufunc w petli
    for nie moga byc typu None, chociaz ten warunek byl sprawdzany, takie rozwiazanie bylo proponowane na stronie 
    dokumentacji opencv. Problem ten zostal rozwiazany po przez uzycie starszej wersji pythona, np. na 3.6 dziala. 
    Problem ten probowalem rozwiazac innymi metodami, ale zadna z nich nie skutkowala.
    https://docs.opencv.org/3.4/d4/d70/tutorial_hough_circle.html"""
    if circles is not None:
        circles= np.uint16(np.around(circles))  # potrzebne bo kod nie dziala
        # jesli tak to nastapi rysowanie kołek czarnych kolek w miejscje znalezionych zlotych monet
        for i in circles[0, :]:
            obraz = cv2.circle(obraz, (i[0], i[1]), 46, 0, -1)

    return obraz_zloty, obraz
"---------------------------------------------------------------------------------------------------------------------"
#funkcja zwraca obraz z wykrytymi nominalami i sume nominalow wszystkich monet
#argumentem wejsciowym jest obraz z oryginalny, obraz z zlotymi monetami i obraz z srebnymi monetami na czarnym tle
def licz(obraz,obraz_zloty,obraz_srebny):
    #zliczona wartosc monet na zdjeciu
    suma=0

    # konwersja na skale szarosci
    gray_srebny = cv2.cvtColor(obraz_srebny, cv2.COLOR_BGR2GRAY)
    gray_zloty = cv2.cvtColor(obraz_zloty, cv2.COLOR_BGR2GRAY)

    """dodatkowo zastosowalem adaptive thresh poniewaz wystepowal problem z znalezieniem promieni nominalow, ktorych
    zakres wartosic nie nachodzi na siebie """
    thresh_srebny= cv2.adaptiveThreshold(gray_srebny, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 101,-10)

    #znalezienie zlotych monet
    circles = cv2.HoughCircles(gray_zloty, cv2.HOUGH_GRADIENT, 1, 50, param1=50, param2=30, minRadius=20, maxRadius=45)

    #tutaj rowniez wystupuje ten sam problem opisany juz wczesniej
    #zliczanie sumy zlotych monet i detekcja na obrazie
    if circles is not None:
        circles = np.uint16(np.around(circles))
        for i in circles[0, :]:
            #rysowanie kolek dla wszystkich
            cv2.circle(obraz, (i[0], i[1]), i[2], (0, 255, 0), 2)

            #dla 1 gr
            if i[2]==27:
                cv2.putText(img=obraz, text="1 gr", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                            fontScale=0.5,
                            color=(0, 255, 0), thickness=1)
                suma=suma+0.01

            #dla 2 gr
            if i[2]==30:
                cv2.putText(img=obraz, text="2 gr", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                            fontScale=0.5,
                            color=(0, 255, 0), thickness=1)
                suma=suma+0.02

            #dla 5 gr
            if i[2]==34:
                cv2.putText(img=obraz, text="5 gr", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                            fontScale=0.5,
                            color=(0, 255, 0), thickness=1)
                suma=suma+0.05

            #dla 2 zl
            if i[2]==37:
                cv2.putText(img=obraz, text="2 zl", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                            fontScale=0.5,
                            color=(0, 255, 0), thickness=1)
                suma=suma+2.0

            #dla 5 zl
            if i[2]==28:
                cv2.putText(img=obraz, text="5 zl", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                            fontScale=0.5,
                            color=(0, 255, 0), thickness=1)
                suma=suma+5.0


    #znalezienie srebnych monet
    circles1 = cv2.HoughCircles(thresh_srebny, cv2.HOUGH_GRADIENT, 1, 100, param1=300, param2=10, minRadius=25, maxRadius=45)

    #tutaj ten problem nie wystepuje, poniewaz na kazdym zdjeciu sa srebne monety
    #zliczanie sumy srebnych monet i detekcja na obrazie
    if circles1 is not None:
        circles1 = np.uint16(np.around(circles1))
        for i in circles1[0, :]:
            cv2.circle(obraz, (i[0], i[1]), i[2], (0, 255, 0), 2)

            #dla 10 gr
            if i[2]==31 or i[2]==30:
                cv2.putText(img=obraz, text="10 gr", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0), thickness=1)
                suma=suma+0.10

            #dla 20 gr
            if i[2]==35 or i[2]==34 or i[2]==33 or i[2]==32:
                cv2.putText(img=obraz, text="20 gr", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0), thickness=1)
                suma=suma+0.20

            #dla 50 gr
            if i[2]==38 or i[2]==37:
                cv2.putText(img=obraz, text="50 gr", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0), thickness=1)
                suma=suma+0.50

            #dla 1 zl
            if i[2]==40 or i[2]==41 or i[2]==42:
                cv2.putText(img=obraz, text="1 zl", org=(i[0], i[1]), fontFace=cv2.FONT_HERSHEY_TRIPLEX,
                        fontScale=0.5,
                        color=(0, 255, 0), thickness=1)
                suma=suma+1.0

    return obraz,suma
"---------------------------------------------------------------------------------------------------------------------"
#glowna petla programu
for i in range(3):
    obraz=zwrocObrazGithub(i)
    drukujObraz("oryginalny",obraz)

    wszystkie=wszyskieNominaly(obraz.copy())
    drukujObraz("wszystkie nomianly",wszystkie)

    obraz_zloty,obraz_srebny=rodziel(wszystkie.copy())
    drukujObraz("tylko zlote",obraz_zloty)
    drukujObraz("tylko srebne",obraz_srebny)

    obraz_wykryty,suma=licz(obraz.copy(),obraz_zloty.copy(),obraz_srebny.copy())
    drukujObraz("wykryte nominaly",obraz_wykryty)
    print(suma,"zł")
"---------------------------------------------------------------------------------------------------------------------"









