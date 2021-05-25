from django.shortcuts import render
from lyrics.utils import scrap, train_model, generate_from_model
from django.http import JsonResponse
from lyrics.models import Group
from django.shortcuts import redirect

# Create your views here.
def index(request):
    if request.GET:
        empty = False
        consulta = request.GET.get('q')
        res = Group.objects.filter(name__icontains=consulta)
        if not res:
            empty = True
        return render(request, 'index.html', {"groups":res, "empty":empty})
    else:
        groups = Group.objects.all()
        isLoaded = True
        if not groups:
            isLoaded = False
        return render(request, 'index.html', {"isLoaded":isLoaded})


def loadArtists(request):
    return render(request, 'loadGroups.html', {})


def loadingArtists(request):
    data = {"error": False, "numArtists": 0}
    try:
        scrap.scrapArtists()
    except Exception as e:
        data = {"error":True}
        return JsonResponse(data)

    numArtists = Group.objects.all().count()
    data["numArtists"] = numArtists

    return JsonResponse(data)

def artist(request, id):
    if request.POST:
        artistId = id
        artist = Group.objects.get(id=artistId)
        scrap.scrapAlbumsAndSongs(artist.url) 

        return redirect('training')

    else:
        artistId = id
        artist = Group.objects.get(id=artistId)
        albums = scrap.scrapAlbums(artist.url) 

        return render(request, 'displayArtist.html', {"artist":artist, "albums":albums})


def training(request):
    if request.POST:
        train_model.train()
        trained = True
        return redirect('generate')
    else:
        return render(request, 'training.html', {})


def generate(request):
    if request.POST:
        firstWords = request.POST.get('firstWords')
        temperature = float(request.POST.get('temperature_val'))
        max_length = int(request.POST.get('max_length_val'))
        verses = int(request.POST.get('verses_val'))

        generated_song_list = generate_from_model.generate(verses, firstWords, max_length, temperature)
        
        [x.encode('utf-8') for x in generated_song_list] #TODO seguramente no haga falta esto tras haber corregido los scrappings

        print("....................")
        print(generated_song_list)

        return render(request, 'generate.html', {"res":generated_song_list})

    return render(request, 'generate.html', {})