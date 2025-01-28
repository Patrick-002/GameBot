from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from .models import Game, Purchase
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth.decorators import login_required
from decimal import Decimal


def main(request):
    games_list = Game.objects.all().order_by('id')
    paginator = Paginator(games_list, 10)
    page_number = request.GET.get('page')
    games = paginator.get_page(page_number)

    return render(request, 'main.html', {'games': games})


def add_to_cart(request, game_id):
    game = Game.objects.get(id=game_id)
    cart = request.session.get('cart', {})

    if game_id not in cart:
        cart[str(game.id)] = {
            'title': game.title,
            'price': float(game.price),
        }

    request.session['cart'] = cart
    return redirect('/')


def remove_from_cart(request, game_id):
    cart = request.session.get('cart', {})

    if game_id in cart:
        del cart[game_id]
        request.session['cart'] = cart
    return redirect('cart')


def cart(request):
    cart = request.session.get('cart', {})
    total_price = sum(item['price'] for item in cart.values())
    return render(request, 'cart.html', {'cart': cart, 'total_price': total_price})


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('/')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.username}!')
                return redirect('/')
            else:
                messages.error(request, 'Неправильное имя пользователя или пароль.')
        else:
            messages.error(request, 'Исправьте ошибки в форме.')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    messages.info(request, 'Вы вышли из системы.')
    return redirect('/')


@login_required(login_url='/register/')
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "Ваша корзина пуста.")
        return redirect('cart')

    total_price = sum(Decimal(item['price']) for item in cart.values())

    if request.user.balance < total_price:
        messages.error(request, "Недостаточно средств на балансе.")
        return redirect('cart')

    request.user.balance -= total_price
    request.user.save()

    for game_id in cart.keys():
        game = Game.objects.get(id=game_id)
        Purchase.objects.create(user=request.user, game=game)

    request.session['cart'] = {}
    messages.success(request, "Заказ успешно оформлен!")
    return redirect('my_games')


@login_required(login_url='/register/')
def my_games(request):
    purchases = request.user.purchases.select_related('game')
    return render(request, 'my_games.html', {'purchases': purchases})
