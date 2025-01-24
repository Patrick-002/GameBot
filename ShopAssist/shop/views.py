from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Game


def index(request):
    return render(request, 'shop/index.html')


def index(request):
    games_list = Game.objects.all().order_by('id')
    paginator = Paginator(games_list, 10)
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)

    return render(request, 'index.html', {'games': games})


def add_to_cart(request, game_title):
    game = get_object_or_404(Game, title=game_title)

    cart = request.session.get('cart', {})

    if game_title not in cart:
        cart[game_title] = {
            'title': game.title,
            'price': float(game.price),
        }

    request.session['cart'] = cart

    return redirect('/')


def remove_from_cart(request, game_title):
    cart = request.session.get('cart', {})

    if game_title in cart:
        del cart[game_title]

    request.session['cart'] = cart

    return redirect('cart')


def cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] for item in cart.values())  # Суммируем только цену
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})
