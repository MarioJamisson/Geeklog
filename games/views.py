import datetime
import requests
from django.shortcuts import render, redirect
from .models import Review
from django.contrib.auth.decorators import login_required

# 🔐 Substitua pelos seus dados reais:
CLIENT_ID = 'u54eax7r0alow8vx2ks5b1ln4aet8q'
ACCESS_TOKEN = 'bf31jgo2rqbpqwjmrr0o75nyoj5w6f'  # aquele tokenzão gerado no passo anterior

def igdb_teste(request):
    query = request.GET.get('q', '')
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }

    data = f'fields name, cover.url; limit 10; sort popularity desc;'
    if query:
        data = f'search "{query}"; fields name, cover.url; limit 10;'

    response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=data)
    jogos = response.json() if response.status_code == 200 else []

    return render(request, 'igdb_teste.html', {'jogos': jogos, 'query': query})

def igdb_detalhes(request, game_id):
    headers = {
        'Client-ID': CLIENT_ID,
        'Authorization': f'Bearer {ACCESS_TOKEN}',
    }

    data = f'''
    fields name, cover.url, genres, involved_companies.company.name,
    summary, first_release_date, aggregated_rating;
    where id = {game_id};
    '''

    response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=data)
    resultado = response.json()

    if not resultado:
        return render(request, 'erro.html', {'mensagem': 'Jogo não encontrado no IGDB.'})

    jogo = resultado[0]

    # Converte data
    if 'first_release_date' in jogo:
        timestamp = jogo['first_release_date']
        jogo['first_release_date'] = datetime.datetime.fromtimestamp(timestamp).strftime('%d/%m/%Y')

    # Gêneros (segunda requisição se necessário)
    genre_ids = jogo.get('genres')
    if genre_ids and isinstance(genre_ids[0], int):  # se são apenas IDs
        genre_data = f'fields name; where id = ({",".join(str(g) for g in genre_ids)});'
        genre_resp = requests.post('https://api.igdb.com/v4/genres', headers=headers, data=genre_data)
        if genre_resp.status_code == 200:
            genres_result = genre_resp.json()
            jogo['genres'] = [g['name'] for g in genres_result]
        else:
            jogo['genres'] = []
    elif genre_ids:  # se já vierem com nome
        jogo['genres'] = [g['name'] for g in genre_ids]
    else:
        jogo['genres'] = []

    # Desenvolvedoras
    jogo['companies'] = [c['company']['name'] for c in jogo.get('involved_companies', [])]

    # Review
    if request.method == 'POST' and request.user.is_authenticated:
        texto = request.POST.get('texto')
        if texto:
            Review.objects.create(user=request.user, game_id=game_id, texto=texto)
            return redirect('igdb_detalhes', game_id=game_id)

    reviews = Review.objects.filter(game_id=game_id).order_by('-created_at')

    return render(request, 'igdb_detalhes.html', {'jogo': jogo, 'reviews': reviews})
