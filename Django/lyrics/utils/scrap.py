import time
import requests
from bs4 import BeautifulSoup
from lyrics.models import Group
import os
from django.conf import settings
import io
import re

# Cada uno de los índices corresponde a una página del tipo https://www.azlyrics.com/{index}.html, que contiene los 
# artistas que empiezan por dicho carácter
indexes = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v',
           'w', 'x', 'y', 'z', '19']
baseUrl = "https://www.azlyrics.com/"
sufix = ".html"

wait_time = 5

def scrapArtists():
    #Borramos la bd si tiene elementos
    groups = Group.objects.all()
    if groups:
        Group.objects.all().delete()

    for i in indexes:
        # Esperamos unos segundos antes de realizar la llamada
        time.sleep(wait_time)
        
        group = baseUrl + i + sufix
        
        r = requests.get(group)
        r.encoding = 'utf-8' #Codificamos el request a utf-8

        soup = BeautifulSoup(r.text, 'lxml')

        divs = soup.find_all('div', class_=['col-sm-6 text-center artist-col'])
        
        links = []

        for d in divs:
            links.extend(d.find_all('a'))
        
        for a in links:
            group_link = baseUrl + a['href']
            g = Group(name=a.text, url=group_link)
            g.save()


def scrapAlbums(groupUrl):
    albums = []

    # Hacemos la llamada para obtener la lista de álbumes
    r = requests.get(groupUrl)
    r.encoding = 'utf-8' #Codificamos el request a utf-8

    soup = BeautifulSoup(r.text, 'lxml')

    res = soup.findAll('div', class_=['album', 'listalbum-item'])

    currentAlbum = ''
    for div in res:
        if(div.get('class')[0] == 'album'):
            currentAlbum = div.find('b').contents[0].replace('"', '')
            albums.append(currentAlbum)
    
    return albums
    

def scrapAlbumsAndSongs(groupUrl):
    # Las claves serán los álbumes y los valores un array con las canciones. Las canciones a su vez serán un array de tamaño 3:
    # El primer valor es el titulo, el segundo el enlace y el tercero la letra de la canción
    albumsDict = {}

    # Hacemos la llamada para obtener la lista de álbumes
    r = requests.get(groupUrl)
    r.encoding = 'utf-8' #Codificamos el request a utf-8

    soup = BeautifulSoup(r.text, 'lxml')

    res = soup.findAll('div', class_=['album', 'listalbum-item'])

    # Recorremos la lista de álbumes y para cada uno de ellos guardamos en el diccionario
    # el título de cada canción y la ruta a la letra de dicha canción
    currentAlbum = ''
    for div in res:
        if(div.get('class')[0] == 'album'):
            # Este div corresponde a un álbum, por lo que añadimos una nueva entrada al diccionario
            currentAlbum = div.find('b').contents[0].replace('"', '')
            albumsDict[currentAlbum] = []
        else:
            # Este div corresponde a una canción por lo que la añadimos a los valores del álbum
            # Hay veces que referencia a una ruta completa, al pertenecer a otro artista, por lo que hay que tenerlo en cuenta
            if div.contents[0]['href'][2:].startswith("tps://www.azlyrics.com"):
                albumsDict[currentAlbum].append([div.contents[0].contents[0], div.contents[0]['href']])
            else:
                albumsDict[currentAlbum].append([div.contents[0].contents[0], 'https://www.azlyrics.com' + div.contents[0]['href'][2:]])
    
    #----------------- CANCIONES --------------------
    #Creamos un diccionario donde las claves serán las canciones y el valor la letra de dicha canción
    lyricsDict = {}

    print('Leyendo ' + str(len(albumsDict)) + ' álbum(es)')

    #Recorremos la lista de álbumes y para cada álbum recorremos la lista de canciones
    for album in albumsDict:
        print ('Reading album: ', album)
        for song in albumsDict[album]:
            print ('    Reading song: ', song[0])
            
            # Esperamos unos segundos antes de realizar la llamada
            time.sleep(wait_time)
            
            r = requests.get(song[1])
            r.encoding = 'utf-8' #Codificamos el request a utf-8
            
            soup = BeautifulSoup(r.text, 'lxml')
            
            # Como el div que contiene la letra no tiene ninguna clase ni identificador lo obtendremos a partir del div padre
            column = soup.find('div', class_=['col-xs-12 col-lg-8 text-center'])
            
            #El div con la letra de la canción siempre estará en 5º lugar, después de los divs del título y de las redes sociales
            raw_lyrics = column.findAll('div')[5].text
            raw_lyrics = re.sub("[\(\[].*?[\)\]]", "", raw_lyrics) #Quitamos el contenido entre paréntesis y corchetes
            lyricsDict[song[0]] = raw_lyrics

    # Recorremos los álbumes
    for album in albumsDict:
        # Recorremos las canciones de cada álbum
        for song in albumsDict[album]:
            #A cada canción le añadimos la letra correspondiente
            song.append(lyricsDict[song[0]])


    # ESCRITURA EN ARCHIVO TXT
    file = io.open(os.path.join(settings.BASE_DIR, "lyrics/data/song_lyrics.txt"), "w", encoding="utf-8") 

    n_songs = 0

    for album in albumsDict:
        for song in albumsDict[album]:
            file.write(song[2]) #El índice 2 contiene las letras
            n_songs += 1

    print("Número total de canciones almacenadas: {}.\n".format(n_songs))

    file.close()

    print("song_lyrics.txt creado satisfactoriamente.")
