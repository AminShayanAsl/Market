import json
import re

from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models import Q, F
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from . import forms
from . import models


def home(request):
    discount_list = models.Good.objects.order_by('-discount').filter(~Q(discount=0))
    score_list = models.Good.objects.order_by('-score').filter(score__gte=3)
    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'
    codes = models.Discount_code.objects.all()
    dis_code = ''
    for item in codes:
        dis_code = item.code
    context = {'discount_list': discount_list, 'score_list': score_list, 'btn_text': btn_text, 'dis_code': dis_code}
    return render(request, 'app/home.html', context)


def discount(request):
    goods = models.Good.objects.order_by('-discount').filter(~Q(discount=0))
    title = 'discount'
    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'
    return render(request, 'app/discount.html', {'goods': goods, 'title': title, 'btn_text': btn_text})


def score(request):
    goods = models.Good.objects.order_by('-score').filter(score__gte=3)
    title = 'score'
    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'
    return render(request, 'app/discount.html', {'goods': goods, 'title': title, 'btn_text': btn_text})


def acount(request):
    if request.user.is_authenticated and request.user.username != 'amin':
        user = User.objects.get(username=request.user.username)
        return render(request, 'app/profile.html', {'user': user})
    else:
        return render(request, 'app/acount.html', {'btn_text': 'ورود به حساب کاربری'})


def logIn(request):
    users = User.objects.all()
    userName = request.POST['username']
    password = request.POST['password']
    error_message = []
    has_error = False
    flag = False
    if userName == '' or password == '':
        error_message.append('لطفا نام کاربری یا رمز را خالی نگذارید.')
        has_error = True
    else:
        for user in users:
            if user.username == userName:
                if user.check_password(password):
                    flag = True
                    break
        if not flag:
            error_message.append('نام کاربری یا رمز اشتباه میباشد.')
            has_error = True

    if has_error:
        return render(request, 'app/acount.html', {'error_message': error_message})

    else:
        user = authenticate(username=userName, password=password)
        login(request, user)
        return render(request, 'app/profile.html', {'user': user})


def create_acount(request):
    if request.method == 'POST':
        pass
    else:
        form = forms.ImageForm()
    return render(request, 'app/create_acount.html', {'btn_text': 'ورود به حساب کاربری', 'form': form})


def created_acount(request):
    users = User.objects.all()
    userName = request.POST['user_name']
    fname = request.POST['fname']
    lname = request.POST['lname']
    password = request.POST['password']
    error_messages = []
    has_error = False

    if len(userName) < 6 or len(userName) > 256:
        error_messages.append('نام کاربری باید حداقل ۶ حرف باشد.')
        has_error = True
    else:
        for user in users:
            if user.username == userName:
                error_messages.append('این نام کاربری از قبل موجود می‌باشد.')
                has_error = True
                break
    if len(fname) == 0 or len(lname) == 0:
        error_messages.append('نام و نام خانوادگی نباید خالی باشد.')
        has_error = True
    if len(password) < 6 or len(password) > 24:
        error_messages.append('تعداد حروف رمز باید بین ۶ تا ۲۴ باشد.')
        has_error = True
    elif re.search('\W', password) is not None:
        error_messages.append('برای رمز باید فقط از حروف انگلیسی و اعداد استفاده کنید.')
        has_error = True

    if has_error:
        form = forms.ImageForm()
        return render(request, 'app/create_acount.html',
                      {'error_messages': error_messages, 'btn_text': 'ورود به حساب کاربری', 'form': form})

    else:
        form = forms.ImageForm(request.POST, request.FILES)
        user = User.objects.create_user(username=userName, first_name=fname, last_name=lname, password=password)
        if request.FILES:
            models.User_img(user=user, image=request.FILES['image']).save()
        return render(request, 'app/create_acount_address.html', {'btn_text': 'ورود به حساب کاربری', 'user': user})


def create_acount_address(request, user_ID):
    state = request.POST['state']
    city = request.POST['city']
    address = request.POST['address']
    postalCode = request.POST['postalcode']
    error_messages = []
    has_error = False

    if state == '0':
        error_messages.append('لطفا استان را انتخاب نمایید.')
        has_error = True

    elif city == '0':
        error_messages.append('لطفا شهر را انتخاب نمایید.')
        has_error = True

    elif address == '':
        error_messages.append('لطفا آدرس خود را وارد نمایید.')
        has_error = True

    if len(address) > 256:
        error_messages.append('لطفا آدرس کوتاه‌تری وارد نمایید.')
        has_error = True

    if len(postalCode) != 10 or re.search('[^0-9]', postalCode) is not None:
        error_messages.append('لطفا کدپستی ۱۰ رقمی خود را بدون استفاده از خط تیره و فقظ با استفاده از اعداد پر کنید.')
        has_error = True

    if has_error:
        user = User.objects.get(id=user_ID)
        return render(request, 'app/create_acount_address.html',
                      {'btn_text': 'ورود به حساب کاربری', 'user': user, 'error_messages': error_messages})

    else:
        city_code = find_city(state, city)
        state_code = find_state(state)
        user = User.objects.get(id=user_ID)
        location = models.Location(state=state_code, city=city_code, address=address, postal_code=postalCode, user=user)
        location.save()
        return render(request, 'app/created_acount.html')


def add_address(request, user_id):
    user = User.objects.get(id=user_id)
    return render(request, 'app/add_address.html', {'user': user})


def del_address(request, user_ID, address_id):
    models.Location.objects.filter(id=address_id).delete()
    user = User.objects.get(id=user_ID)
    return render(request, 'app/profile.html', {'user': user})


def check_address(request, user_id):
    user = User.objects.get(id=user_id)
    state = request.POST['state']
    city = request.POST['city']
    address = request.POST['address']
    postalCode = request.POST['postalcode']
    error_messages = []
    has_error = False

    if state == '0':
        error_messages.append('لطفا استان را انتخاب نمایید.')
        has_error = True

    elif city == '0':
        error_messages.append('لطفا شهر را انتخاب نمایید.')
        has_error = True

    elif address == '':
        error_messages.append('لطفا آدرس خود را وارد نمایید.')
        has_error = True

    if len(address) > 256:
        error_messages.append('لطفا آدرس کوتاه‌تری وارد نمایید.')
        has_error = True

    if len(postalCode) != 10 or re.search('[^0-9]', postalCode) is not None:
        error_messages.append('لطفا کدپستی ۱۰ رقمی خود را بدون استفاده از خط تیره و فقظ با استفاده از اعداد پر کنید.')
        has_error = True

    if has_error:
        return render(request, 'app/add_address.html', {'error_messages': error_messages, 'user': user})

    else:
        city_code = find_city(state, city)
        state_code = find_state(state)
        location = models.Location(state=state_code, city=city_code, address=address, postal_code=postalCode, user=user)
        location.save()
        return render(request, 'app/created_acount.html')


def good_info(request, good_id):
    good = models.Good.objects.get(pk=good_id)
    comments = models.Comment.objects.order_by('-date').filter(good=good)
    related_goods = []

    if good.category == 'Electronic':
        related_goods = models.Good.objects.all().filter(category='Electronic',
                                                         electronic__category_elec=good.electronic.category_elec)
    elif good.category == 'Clothes':
        related_goods = models.Good.objects.all().filter(category='Clothes',
                                                         clothes__category_clothes=good.clothes.category_clothes,
                                                         clothes__gender=good.clothes.gender)
    elif good.category == 'HomeAppliances':
        related_goods = models.Good.objects.all().filter(category='HomeAppliances',
                                                         homeappliances__category_happ=good.homeappliances.category_happ)
    elif good.category == 'Sport':
        related_goods = models.Good.objects.all().filter(category='Sport',
                                                         sport__category_sport=good.sport.category_sport)
    elif good.category == 'Stationery':
        related_goods = models.Good.objects.all().filter(category='Stationery',
                                                         stationery__category_st=good.stationery.category_st)

    related_goods = related_goods.filter(~Q(id=good.id))

    interesting = request.POST.get('interesting', 'all')
    blue = request.POST.get('blue', 'false')
    black = request.POST.get('black', 'false')
    brown = request.POST.get('brown', 'false')
    gray = request.POST.get('gray', 'false')
    navy = request.POST.get('navy', 'false')
    add_cart = request.POST.get('add_cart', 'false')
    size = request.POST.get('size', 'all')
    star = request.POST.get('star', 0)
    comment = request.POST.get('comment_text', '')

    error_messages = []
    messages = []
    colors = []
    sizes = []
    heart = 'off'
    this_color = ''
    star = int(star)

    if good.category == 'Electronic':
        if blue == 'true':
            if good.electronic.category_elec == 'LapTop':
                good.electronic.laptop.color_choose = 'blue'
                good.electronic.laptop.save()
            elif good.electronic.category_elec == 'Mobile':
                good.electronic.mobile.color_choose = 'blue'
                good.electronic.mobile.save()
        elif black == 'true':
            if good.electronic.category_elec == 'LapTop':
                good.electronic.laptop.color_choose = 'black'
                good.electronic.laptop.save()
            elif good.electronic.category_elec == 'Mobile':
                good.electronic.mobile.color_choose = 'black'
                good.electronic.mobile.save()
        elif brown == 'true':
            if good.electronic.category_elec == 'LapTop':
                good.electronic.laptop.color_choose = 'brown'
                good.electronic.laptop.save()
            elif good.electronic.category_elec == 'Mobile':
                good.electronic.mobile.color_choose = 'brown'
                good.electronic.mobile.save()
        elif gray == 'true':
            if good.electronic.category_elec == 'LapTop':
                good.electronic.laptop.color_choose = 'gray'
                good.electronic.laptop.save()
            elif good.electronic.category_elec == 'Mobile':
                good.electronic.mobile.color_choose = 'gray'
                good.electronic.mobile.save()
        elif navy == 'true':
            if good.electronic.category_elec == 'LapTop':
                good.electronic.laptop.color_choose = 'navy'
                good.electronic.laptop.save()
            elif good.electronic.category_elec == 'Mobile':
                good.electronic.mobile.color_choose = 'navy'
                good.electronic.mobile.save()

    elif good.category == 'Clothes':
        if good.clothes.category_clothes == 'Shirt' and size != 'all':
            good.clothes.shirt.size_this = size
            good.clothes.shirt.save()
        elif good.clothes.category_clothes == 'Tshirt' and size != 'all':
            good.clothes.tshirt.size_this = size
            good.clothes.tshirt.save()

    if interesting == 'true':
        heart = 'off'
    elif interesting == 'false':
        heart = 'on'

    if good.category == 'Electronic':
        if good.electronic.category_elec == 'LapTop' or good.electronic.category_elec == 'Mobile':
            colors = good.electronic.color_set.all()
            if good.electronic.category_elec == 'LapTop':
                this_color = good.electronic.laptop.color_this
            elif good.electronic.category_elec == 'Mobile':
                this_color = good.electronic.mobile.color_this

    elif good.category == 'Clothes':
        if good.clothes.category_clothes == 'Shirt' or good.clothes.category_clothes == 'Tshirt':
            sizes = good.clothes.size_set.all()

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
        user = User.objects.get(username=request.user.username)
        if interesting == 'true':
            Interesting = models.Interesting(good=good, user=user)
            Interesting.save()
            heart = 'on'
        elif interesting == 'all':
            for product in user.interesting_set.all():
                if product.good == good:
                    heart = 'on'

        elif interesting == 'false':
            for product in user.interesting_set.all():
                if product.good == good:
                    pk = product.id
                    models.Interesting.objects.get(id=pk).delete()
                    heart = 'off'
                    break

        if add_cart == 'true':
            carts = models.Cart.objects.all().filter(user=user)
            exsist = False
            for elem in carts:
                if elem.good == good:
                    exsist = True
            if exsist == False:
                cart = models.Cart(user=request.user, good=good, number=1)
                cart.save()
                messages.append('این کالا به سبد خرید شما افزوده شد.')
            else:
                error_messages.append('این کالا در سبد خرید شما موجود است.')

        if star > 0:
            score = good.score
            score_num = good.score_num + 1
            score = (score * (score_num - 1) + star) / score_num
            good.score = score
            good.score_num = score_num
            good.save()

        if comment != '':
            name = user.first_name + ' ' + user.last_name
            new_comment = models.Comment(good=good, text=comment, name=name)
            new_comment.save()

    else:
        btn_text = 'ورود به حساب کاربری'
        if interesting == 'true' or add_cart == 'true' or star > 0 or comment != '':
            error_messages.append('ابتدا وارد حساب کاربری خود شوید.')

    context = {'good': good, 'btn_text': btn_text, 'heart': heart, 'error_messages': error_messages,
               'colors': colors, 'this_color': this_color, 'sizes': sizes, 'related_goods': related_goods,
               'comments': comments, 'messages': messages}

    return render(request, 'app/good_info.html', context=context)


def interesting(request, user_id):
    user = User.objects.get(id=user_id)
    btn_text = user.username

    interesting_goods = user.interesting_set.all()
    page = request.GET.get('page', 1)
    paginator = Paginator(interesting_goods, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'goods': goods}

    return render(request, 'app/interesting.html', context=context)


def logOut(request):
    logout(request)
    return redirect('app:home')


def elect_menu(request):
    name = 'electronic'
    return render(request, 'app/menu.html', {'name': name})


def clothes_menu(request):
    name = 'clothes'
    return render(request, 'app/menu.html', {'name': name})


def homeApp_menu(request):
    name = 'homeApp'
    return render(request, 'app/menu.html', {'name': name})


def sport_menu(request):
    name = 'sport'
    return render(request, 'app/menu.html', {'name': name})


def stationery_menu(request):
    name = 'stationery'
    return render(request, 'app/menu.html', {'name': name})


# grouping
def electronic(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Electronic')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'all_elec'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def lap_top(request):
    list = models.Good.objects.order_by('-release_date').filter(electronic__category_elec='LapTop')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    brand_asus = request.POST.get('brand_asus', 'false')
    brand_huawei = request.POST.get('brand_huawei', 'false')
    brand_apple = request.POST.get('brand_apple', 'false')
    storage = request.POST.get('storage', 'all')
    ram = request.POST.get('RAM', 'all')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    if storage == 'all':
        min_storage = 0
        max_storage = 2000
    else:
        if storage == '16_500':
            min_storage = 16
            max_storage = 499
        elif storage == '500_1000':
            min_storage = 500
            max_storage = 999
        elif storage == '1000_1500':
            min_storage = 1000
            max_storage = 1499
        elif storage == '1500_2000':
            min_storage = 1500
            max_storage = 2000

    if ram == 'all':
        min_ram = 0
        max_ram = 64
    else:
        if ram == '1_4':
            min_ram = 1
            max_ram = 3.9
        elif ram == '4_8':
            min_ram = 4
            max_ram = 7.9
        elif ram == '8_16':
            min_ram = 8
            max_ram = 15.9
        elif ram == '16_32':
            min_ram = 16
            max_ram = 31.9
        elif ram == '32_64':
            min_ram = 32
            max_ram = 64

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val, electronic__laptop__storage__gte=min_storage,
                       electronic__laptop__storage__lte=max_storage, electronic__laptop__ram__gte=min_ram,
                       electronic__laptop__ram__lte=max_ram)
    list1 = models.Good.objects.order_by('-release_date').filter(electronic__category_elec='LapTop',
                                                                 real_price__gte=min_val, real_price__lte=max_val,
                                                                 electronic__laptop__storage__gte=min_storage,
                                                                 electronic__laptop__storage__lte=max_storage,
                                                                 electronic__laptop__ram__gte=min_ram,
                                                                 electronic__laptop__ram__lte=max_ram)
    list2 = models.Good.objects.order_by('-release_date').filter(electronic__category_elec='LapTop',
                                                                 real_price__gte=min_val, real_price__lte=max_val,
                                                                 electronic__laptop__storage__gte=min_storage,
                                                                 electronic__laptop__storage__lte=max_storage,
                                                                 electronic__laptop__ram__gte=min_ram,
                                                                 electronic__laptop__ram__lte=max_ram)

    if brand_asus == 'true':
        list = list.filter(electronic__brand='ASUS')
    if brand_huawei == 'true':
        if brand_asus == 'true':
            list1 = list1.filter(electronic__brand='Huawei')
            list |= list1
        else:
            list = list.filter(electronic__brand='Huawei')
    if brand_apple == 'true':
        if brand_asus == 'true' and brand_huawei != 'true':
            list2 = list2.filter(electronic__brand='Apple')
            list |= list2
        elif brand_asus != 'true' and brand_huawei == 'true':
            list1 = list1.filter(electronic__brand='Huawei')
            list2 = list2.filter(electronic__brand='Apple')
            list = list1 | list2
        elif brand_asus == 'true' and brand_huawei == 'true':
            list1 = list1.filter(electronic__brand='Huawei')
            list2 = list2.filter(electronic__brand='Apple')
            list |= (list1 | list2)
        else:
            list = list.filter(electronic__brand='Apple')

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'lap_top'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'brand_asus': brand_asus, 'brand_huawei': brand_huawei,
               'brand_apple': brand_apple, 'storage': storage, 'ram': ram, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def mobile(request):
    list = models.Good.objects.order_by('-release_date').filter(electronic__category_elec='Mobile')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    brand_asus = request.POST.get('brand_asus', 'false')
    brand_huawei = request.POST.get('brand_huawei', 'false')
    brand_apple = request.POST.get('brand_apple', 'false')
    storage = request.POST.get('storage', 'all')
    ram = request.POST.get('RAM', 'all')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    if storage == 'all':
        min_storage = 0
        max_storage = 1000
    else:
        if storage == '0_16':
            min_storage = 0
            max_storage = 15
        elif storage == '16_200':
            min_storage = 16
            max_storage = 199
        elif storage == '200_500':
            min_storage = 200
            max_storage = 499
        elif storage == '500_1000':
            min_storage = 500
            max_storage = 1000

    if ram == 'all':
        min_ram = 0
        max_ram = 16
    else:
        if ram == '0_4':
            min_ram = 0
            max_ram = 3.9
        elif ram == '4_6':
            min_ram = 4
            max_ram = 5.9
        elif ram == '6_8':
            min_ram = 6
            max_ram = 7.9
        elif ram == '8_12':
            min_ram = 8
            max_ram = 11.9
        elif ram == '12_16':
            min_ram = 12
            max_ram = 16

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val, electronic__mobile__memory__gte=min_storage,
                       electronic__mobile__memory__lte=max_storage, electronic__mobile__ram__gte=min_ram,
                       electronic__mobile__ram__lte=max_ram)
    list1 = models.Good.objects.order_by('-release_date').filter(electronic__category_elec='Mobile',
                                                                 real_price__gte=min_val, real_price__lte=max_val,
                                                                 electronic__mobile__memory__gte=min_storage,
                                                                 electronic__mobile__memory__lte=max_storage,
                                                                 electronic__mobile__ram__gte=min_ram,
                                                                 electronic__mobile__ram__lte=max_ram)
    list2 = models.Good.objects.order_by('-release_date').filter(electronic__category_elec='Mobile',
                                                                 real_price__gte=min_val, real_price__lte=max_val,
                                                                 electronic__mobile__memory__gte=min_storage,
                                                                 electronic__mobile__memory__lte=max_storage,
                                                                 electronic__mobile__ram__gte=min_ram,
                                                                 electronic__mobile__ram__lte=max_ram)

    if brand_asus == 'true':
        list = list.filter(electronic__brand='Samsung')
    if brand_huawei == 'true':
        if brand_asus == 'true':
            list1 = list1.filter(electronic__brand='Huawei')
            list |= list1
        else:
            list = list.filter(electronic__brand='Huawei')
    if brand_apple == 'true':
        if brand_asus == 'true' and brand_huawei != 'true':
            list2 = list2.filter(electronic__brand='Apple')
            list |= list2
        elif brand_asus != 'true' and brand_huawei == 'true':
            list1 = list1.filter(electronic__brand='Huawei')
            list2 = list2.filter(electronic__brand='Apple')
            list = list1 | list2
        elif brand_asus == 'true' and brand_huawei == 'true':
            list1 = list1.filter(electronic__brand='Huawei')
            list2 = list2.filter(electronic__brand='Apple')
            list |= (list1 | list2)
        else:
            list = list.filter(electronic__brand='Apple')

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'mobile'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'brand_asus': brand_asus, 'brand_huawei': brand_huawei,
               'brand_apple': brand_apple, 'storage': storage, 'ram': ram, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def headset(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Electronic',
                                                                electronic__category_elec='Headset')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    led = request.POST.get('led', 'false')
    connection = request.POST.get('connection', 'all')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)
    if led == 'true':
        list = list.filter(electronic__headset__led_indicator=True, electronic__headset__connectionType='wireless')
    if connection == 'wire':
        list = list.filter(~Q(electronic__headset__connectionType='wireless'))
    elif connection == 'wireless':
        list = list.filter(electronic__headset__connectionType='wireless')

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'headset'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'led': led, 'connection': connection,
               'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def charger(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Electronic',
                                                                electronic__category_elec='Charger')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    cable_type = request.POST.get('cable_type', 'all')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)
    if cable_type == 'C':
        list = list.filter(~Q(electronic__charger__cable_type='Micro'))
    elif cable_type == 'Micro':
        list = list.filter(electronic__charger__cable_type='Micro')

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'charger'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'cable_type': cable_type, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def male_clothes(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='male')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'all_male_clothes'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def female_clothes(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='female')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'all_female_clothes'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def shirt(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='male',
                                                                clothes__category_clothes='Shirt')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    sleeve_height = request.POST.get('sleeve_height', 'all')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)
    if sleeve_height == 'Short':
        list = list.filter(~Q(clothes__shirt__sleeve_height='Long'))
    elif sleeve_height == 'Long':
        list = list.filter(clothes__shirt__sleeve_height='Long')

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'shirt'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number,
               'sleeve_height': sleeve_height}
    return render(request, 'app/goods.html', context=context)


def tshirt(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='male',
                                                                clothes__category_clothes='Tshirt')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'tshirt'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def male_pants(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='male',
                                                                clothes__category_clothes='Pants')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'male_pants'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def female_pants(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='female',
                                                                clothes__category_clothes='Pants')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'female_pants'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def manto(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='female',
                                                                clothes__category_clothes='Manto')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'manto'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def blouse(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Clothes', clothes__gender='female',
                                                                clothes__category_clothes='Blouse')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'blouse'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def home_app(request):
    list = models.Good.objects.order_by('-release_date').filter(category='HomeAppliances')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'all_home_app'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def refrigerator(request):
    list = models.Good.objects.order_by('-release_date').filter(category='HomeAppliances',
                                                                homeappliances__category_happ='Refrigerator')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    brand = request.POST.get('brand', 'all')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)
    if brand == 'Emersun':
        list = list.filter(homeappliances__refrigerator__brand='Emersun')
    elif brand == 'Snowa':
        list = list.filter(homeappliances__refrigerator__brand='Snowa')

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'refrigerator'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number,
               'brand': brand}
    return render(request, 'app/goods.html', context=context)


def TV(request):
    list = models.Good.objects.order_by('-release_date').filter(category='HomeAppliances',
                                                                homeappliances__category_happ='TV')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    brand = request.POST.get('brand', 'all')
    bluetooth = request.POST.get('bluetooth', 'false')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)
    if brand == 'LG':
        list = list.filter(homeappliances__tv__brand='LG')
    elif brand == 'Samsung':
        list = list.filter(homeappliances__tv__brand='Samsung')
    if bluetooth == 'true':
        list = list.filter(homeappliances__tv__bluetooth=True)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'tv'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number,
               'brand': brand, 'bluetooth': bluetooth}
    return render(request, 'app/goods.html', context=context)


def washing_machine(request):
    list = models.Good.objects.order_by('-release_date').filter(category='HomeAppliances',
                                                                homeappliances__category_happ='Washing_machine')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    brand = request.POST.get('brand', 'all')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)
    if brand == 'Bosch':
        list = list.filter(homeappliances__washing_machine__brand='Bosch')
    elif brand == 'Gplus':
        list = list.filter(homeappliances__washing_machine__brand='Gplus')

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'washing_machine'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number,
               'brand': brand}
    return render(request, 'app/goods.html', context=context)


def sofa(request):
    list = models.Good.objects.order_by('-release_date').filter(category='HomeAppliances',
                                                                homeappliances__category_happ='Sofa')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'sofa'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def sport(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Sport')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'all_sport'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def bicycle(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Sport', sport__category_sport='Bicycle')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'bicycle'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def treadmill(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Sport', sport__category_sport='Treadmill')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'treadmill'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def ball(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Sport', sport__category_sport='Ball')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'ball'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def stationery(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Stationery')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'stationery'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def notebook(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Stationery',
                                                                stationery__category_st='NoteBook')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'notebook'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def pen(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Stationery', stationery__category_st='Pen')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'pen'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def crayons(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Stationery',
                                                                stationery__category_st='Crayons')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'crayons'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def eraser(request):
    list = models.Good.objects.order_by('-release_date').filter(category='Stationery', stationery__category_st='Eraser')

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')

    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'eraser'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def cart(request):
    carts = []
    sum = 0

    discount_code = request.POST.get('discount_code', '')

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
        user = request.user
        carts = models.Cart.objects.all().filter(user=user)

    else:
        btn_text = 'ورود به حساب کاربری'

    for cart in carts:
        sum += cart.good.real_price

    if discount_code != '':
        codes = models.Discount_code.objects.all()
        dis_code = ''
        for item in codes:
            dis_code = item.code
        if discount_code == dis_code:
            sum = int(sum * 0.9)

    context = {'btn_text': btn_text, 'carts': carts, 'sum': sum}
    return render(request, 'app/cart.html', context=context)


def del_cart(request, cart_id):
    models.Cart.objects.get(id=cart_id).delete()

    carts = []
    sum = 0

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
        user = request.user
        carts = models.Cart.objects.all().filter(user=user)

    else:
        btn_text = 'ورود به حساب کاربری'

    for cart in carts:
        sum += cart.good.real_price

    context = {'btn_text': btn_text, 'carts': carts, 'sum': sum}
    return render(request, 'app/cart.html', context=context)


def choose_address(request):
    user = request.user
    return render(request, 'app/choose_address.html', {'user': user})


def message(request):
    return render(request, 'app/message.html')


def cart_plus(request, cart_id):
    cart = models.Cart.objects.get(id=cart_id)
    if cart.good.num > cart.number:
        cart.number = cart.number + 1
        cart.save()

    carts = []
    sum = 0

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
        user = request.user
        carts = models.Cart.objects.all().filter(user=user)

    else:
        btn_text = 'ورود به حساب کاربری'

    for cart in carts:
        sum += cart.good.real_price

    context = {'btn_text': btn_text, 'carts': carts, 'sum': sum}
    return render(request, 'app/cart.html', context=context)


def cart_minus(request, cart_id):
    cart = models.Cart.objects.get(id=cart_id)
    if cart.number > 1:
        cart.number = cart.number - 1
        cart.save()

    carts = []
    sum = 0

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
        user = request.user
        carts = models.Cart.objects.all().filter(user=user)

    else:
        btn_text = 'ورود به حساب کاربری'

    for cart in carts:
        sum += cart.good.real_price

    context = {'btn_text': btn_text, 'carts': carts, 'sum': sum}
    return render(request, 'app/cart.html', context=context)


def all(request):
    word = request.POST.get('search_box', '')

    list = models.Good.objects.order_by('-release_date').filter(Q(name__icontains=word))

    discount = request.POST.get('discount', 'false')
    exsist = request.POST.get('exsist', 'false')
    min_price = request.POST.get('Min_val', '0')
    max_price = request.POST.get('Max_val', '75,000,000')
    min = ''.join([i for i in min_price if i.isdigit()])
    max = ''.join([i for i in max_price if i.isdigit()])
    min_val = int(min)
    max_val = int(max)

    list = list.filter(real_price__gte=min_val, real_price__lte=max_val)

    if discount == 'true':
        list = list.filter(~Q(discount=0), num__gte=1)
    if exsist == 'true':
        list = list.filter(num__gte=1)

    if request.user.is_authenticated and request.user.username != 'amin':
        btn_text = request.user.username
    else:
        btn_text = 'ورود به حساب کاربری'

    group = 'all'

    page_number = request.POST.get('page_number', 1)

    page = request.GET.get('page', page_number)
    paginator = Paginator(list, 12)
    try:
        goods = paginator.page(page)
    except PageNotAnInteger:
        goods = paginator.page(1)
    except EmptyPage:
        goods = paginator.page(paginator.num_pages)

    context = {'btn_text': btn_text, 'group': group, 'goods': goods, 'discount': discount, 'exsist': exsist,
               'min_price': min_price, 'max_price': max_price, 'page_number': page_number}
    return render(request, 'app/goods.html', context=context)


def search(request):
    if 'term' in request.GET:
        goods = models.Good.objects.order_by('-release_date').filter(Q(name__icontains=request.GET.get('term')))
        names = list()
        for good in goods:
            names.append(good.name)
        names = names[:10]
        return JsonResponse(names, safe=False)


# find location
def find_state(state_code):
    code = ''
    if state_code == '1':
        code = 'تهران'
    elif state_code == '2':
        code = 'گیلان'
    elif state_code == '3':
        code = 'آذربایجان شرقی'
    elif state_code == '4':
        code = 'خوزستان'
    elif state_code == '5':
        code = 'فارس'
    elif state_code == '6':
        code = 'اصفهان'
    elif state_code == '7':
        code = 'خراسان رضوی'
    elif state_code == '8':
        code = 'قزوین'
    elif state_code == '9':
        code = 'سمنان'
    elif state_code == '10':
        code = 'قم'
    elif state_code == '11':
        code = 'مرکزی'
    elif state_code == '12':
        code = 'زنجان'
    elif state_code == '13':
        code = 'مازندران'
    elif state_code == '14':
        code = 'گلستان'
    elif state_code == '15':
        code = 'اردبیل'
    elif state_code == '16':
        code = 'آذربایجان غربی'
    elif state_code == '17':
        code = 'همدان'
    elif state_code == '18':
        code = 'کردستان'
    elif state_code == '19':
        code = 'کرمانشاه'
    elif state_code == '20':
        code = 'لرستان'
    elif state_code == '21':
        code = 'بوشهر'
    elif state_code == '22':
        code = 'کرمان'
    elif state_code == '23':
        code = 'هرمزگان'
    elif state_code == '24':
        code = 'چهارمحال و بختیاری'
    elif state_code == '25':
        code = 'یزد'
    elif state_code == '26':
        code = 'سیستان و بلوچستان'
    elif state_code == '27':
        code = 'ایلام'
    elif state_code == '28':
        code = 'کهگلویه و بویراحمد'
    elif state_code == '29':
        code = 'خراسان شمالی'
    elif state_code == '30':
        code = 'خراسان جنوبی'
    elif state_code == '31':
        code = 'البرز'
    return code


def find_city(state_code, city_code):
    code = ''
    if state_code == '1':
        if city_code == '33131':
            code = 'احمدآبادمستوفي'
        elif city_code == '31541':
            code = 'ادران'
        elif city_code == '18641':
            code = 'اسلام آباد'
        elif city_code == '331':
            code = 'اسلام شهر'
        elif city_code == '37671':
            code = 'اكبرآباد'
        elif city_code == '39861':
            code = 'اميريه'
        elif city_code == '31686':
            code = 'انديشه'
        elif city_code == '33431':
            code = 'اوشان'
        elif city_code == '39761':
            code = 'آبسرد'
        elif city_code == '39741':
            code = 'آبعلي'
        elif city_code == '33541':
            code = 'باغستان'
        elif city_code == '18131':
            code = 'باقر شهر'
        elif city_code == '33631':
            code = 'برغان'
        elif city_code == '16551':
            code = 'بومهن'
        elif city_code == '33971':
            code = 'پارچين'
        elif city_code == '3391':
            code = 'پاكدشت'
        elif city_code == '16581':
            code = 'پرديس'
        elif city_code == '37611':
            code = 'پرند'
        elif city_code == '19731':
            code = 'پس قلعه'
        elif city_code == '3381':
            code = 'پيشوا'
        elif city_code == '1012':
            code = 'تجزيه مبادلات لشكر'
        elif city_code == '1':
            code = 'تهران'
        elif city_code == '16531':
            code = 'جاجرود'
        elif city_code == '18361':
            code = 'چرمسازي سالاريه'
        elif city_code == '33191':
            code = 'چهاردانگه'
        elif city_code == '18331':
            code = 'حسن آباد'
        elif city_code == '33411':
            code = 'حومه گلندوك'
        elif city_code == '33991':
            code = 'خاتون آباد'
        elif city_code == '33841':
            code = 'خاوه'
        elif city_code == '16571':
            code = 'خرمدشت'
        elif city_code == '19841':
            code = 'دركه'
        elif city_code == '3971':
            code = 'دماوند'
        elif city_code == '3761':
            code = 'رباط كريم'
        elif city_code == '37561':
            code = 'رزگان'
        elif city_code == '39731':
            code = 'رودهن'
        elif city_code == '1813':
            code = 'ري'
        elif city_code == '33361':
            code = 'سعيدآباد'
        elif city_code == '37631':
            code = 'سلطان آباد'
        elif city_code == '19561':
            code = 'سوهانك'
        elif city_code == '33561':
            code = 'شاهدشهر'
        elif city_code == '33941':
            code = 'شريف آباد'
        elif city_code == '18341':
            code = 'شمس آباد'
        elif city_code == '3751':
            code = 'شهر قدس'
        elif city_code == '33551':
            code = 'شهرآباد'
        elif city_code == '16561':
            code = 'شهرجديدپرديس'
        elif city_code == '37511':
            code = 'شهرقدس(مويز)'
        elif city_code == '3351':
            code = 'شهريار'
        elif city_code == '33511':
            code = 'شهرياربردآباد'
        elif city_code == '33171':
            code = 'صالح آباد'
        elif city_code == '31641':
            code = 'صفادشت'
        elif city_code == '18381':
            code = 'فرودگاه امام خميني'
        elif city_code == '18471':
            code = 'فرون آباد'
        elif city_code == '33451':
            code = 'فشم'
        elif city_code == '3981':
            code = 'فيروزكوه'
        elif city_code == '18686':
            code = 'قرچك'
        elif city_code == '18661':
            code = 'قيام دشت'
        elif city_code == '18161':
            code = 'كهريزك'
        elif city_code == '39751':
            code = 'كيلان'
        elif city_code == '33151':
            code = 'گلدسته'
        elif city_code == '37571':
            code = 'گلستان (بهارستان)'
        elif city_code == '39711':
            code = 'گيلاوند'
        elif city_code == '3341':
            code = 'لواسان'
        elif city_code == '33461':
            code = 'لوسان بزرگ'
        elif city_code == '37541':
            code = 'مارليك'
        elif city_code == '33141':
            code = 'مروزبهرام'
        elif city_code == '31691':
            code = 'ملارد'
        elif city_code == '1011':
            code = 'منطقه 11 پستي تهران'
        elif city_code == '1013':
            code = 'منطقه 13 پستي تهران'
        elif city_code == '1014':
            code = 'منطقه 14 پستي تهران'
        elif city_code == '1015':
            code = 'منطقه 15 پستي تهران'
        elif city_code == '1016':
            code = 'منطقه 16 پستي تهران'
        elif city_code == '1017':
            code = 'منطقه 17 پستي تهران'
        elif city_code == '1018':
            code = 'منطقه 18 پستي تهران'
        elif city_code == '1019':
            code = 'منطقه 19 پستي تهران'
        elif city_code == '37651':
            code = 'نسيم شهر (بهارستان)'
        elif city_code == '37551':
            code = 'نصيرآباد'
        elif city_code == '33176':
            code = 'واوان'
        elif city_code == '33581':
            code = 'وحيديه'
        elif city_code == '3371':
            code = 'ورامين'
        elif city_code == '18391':
            code = 'وهن آباد'

    elif state_code == '2':
        if city_code == '43591':
            code = 'احمد سرگوراب'
        elif city_code == '43891':
            code = 'اسالم'
        elif city_code == '44681':
            code = 'اسكلك'
        elif city_code == '43371':
            code = 'اسلام آباد'
        elif city_code == '44791':
            code = 'اطاقور'
        elif city_code == '44951':
            code = 'املش'
        elif city_code == '4331':
            code = 'آبكنار'
        elif city_code == '4391':
            code = 'آستارا'
        elif city_code == '4441':
            code = 'آستانه اشرفيه'
        elif city_code == '43731':
            code = 'بازاراسالم'
        elif city_code == '43811':
            code = 'بازارجمعه شاندرمن'
        elif city_code == '44561':
            code = 'برهسر'
        elif city_code == '44941':
            code = 'بلترك'
        elif city_code == '43471':
            code = 'بلسبنه'
        elif city_code == '431':
            code = 'بندرانزلي'
        elif city_code == '44331':
            code = 'پاشاكي'
        elif city_code == '43861':
            code = 'پرهسر'
        elif city_code == '43791':
            code = 'پلاسي'
        elif city_code == '44992':
            code = 'پونل'
        elif city_code == '43441':
            code = 'پيربست لولمان'
        elif city_code == '44651':
            code = 'توتكابن'
        elif city_code == '43751':
            code = 'جوكندان'
        elif city_code == '44551':
            code = 'جيرنده'
        elif city_code == '44871':
            code = 'چابكسر'
        elif city_code == '43481':
            code = 'چاپارخانه'
        elif city_code == '43561':
            code = 'چوبر'
        elif city_code == '43451':
            code = 'خاچكين'
        elif city_code == '43391':
            code = 'خشك بيجار'
        elif city_code == '43771':
            code = 'خطبه سرا'
        elif city_code == '4341':
            code = 'خمام'
        elif city_code == '44391':
            code = 'ديلمان'
        elif city_code == '44861':
            code = 'رانكوه'
        elif city_code == '44931':
            code = 'رحيم آباد'
        elif city_code == '44641':
            code = 'رستم آباد'
        elif city_code == '41':
            code = 'رشت'
        elif city_code == '43841':
            code = 'رضوان شهر'
        elif city_code == '4461':
            code = 'رودبار'
        elif city_code == '4481':
            code = 'رودسر'
        elif city_code == '43381':
            code = 'سراوان'
        elif city_code == '43361':
            code = 'سنگر'
        elif city_code == '4431':
            code = 'سياهكل'
        elif city_code == '43851':
            code = 'شاندرمن'
        elif city_code == '43541':
            code = 'شفت'
        elif city_code == '4361':
            code = 'صومعه سرا'
        elif city_code == '43651':
            code = 'طاهر گوداب'
        elif city_code == '44851':
            code = 'طوللات'
        elif city_code == '4351':
            code = 'فومن'
        elif city_code == '44831':
            code = 'قاسم آبادسفلي'
        elif city_code == '43331':
            code = 'كپورچال'
        elif city_code == '4491':
            code = 'كلاچاي'
        elif city_code == '43461':
            code = 'كوچصفهان'
        elif city_code == '44761':
            code = 'كومله'
        elif city_code == '44471':
            code = 'كياشهر'
        elif city_code == '43581':
            code = 'گشت'
        elif city_code == '441':
            code = 'لاهيجان'
        elif city_code == '43431':
            code = 'لشت نشا'
        elif city_code == '4471':
            code = 'لنگرود'
        elif city_code == '44531':
            code = 'لوشان'
        elif city_code == '43531':
            code = 'لولمان'
        elif city_code == '43531':
            code = 'لوندويل'
        elif city_code == '43761':
            code = 'ليسار'
        elif city_code == '4381':
            code = 'ماسال'
        elif city_code == '43571':
            code = 'ماسوله'
        elif city_code == '4451':
            code = 'منجيل'
        elif city_code == '4371':
            code = 'هشتپر ـ طوالش'
        elif city_code == '44891':
            code = 'واجارگاه'

    elif state_code == '3':
        if city_code == '54671':
            code = 'ابشاحمد'
        elif city_code == '54561':
            code = 'اذغان'
        elif city_code == '54731':
            code = 'اسب فروشان'
        elif city_code == '5351':
            code = 'اسكو'
        elif city_code == '5586':
            code = 'اغچه ريش'
        elif city_code == '55661':
            code = 'اقمنار'
        elif city_code == '55541':
            code = 'القو'
        elif city_code == '5451':
            code = 'اهر'
        elif city_code == '53581':
            code = 'ايلخچي'
        elif city_code == '5371':
            code = 'آذرشهر'
        elif city_code == '53661':
            code = 'باسمنج'
        elif city_code == '53951':
            code = 'بخشايش ـ كلوانق'
        elif city_code == '5491':
            code = 'بستان آباد'
        elif city_code == '5551':
            code = 'بناب'
        elif city_code == '54351':
            code = 'بناب جديد ـ مرند'
        elif city_code == '51':
            code = 'تبريز'
        elif city_code == '53331':
            code = 'ترك'
        elif city_code == '53881':
            code = 'تسوج'
        elif city_code == '5441':
            code = 'جلفا'
        elif city_code == '53841':
            code = 'خامنه'
        elif city_code == '54683':
            code = 'خداآفرين'
        elif city_code == '53551':
            code = 'خسروشهر'
        elif city_code == '55441':
            code = 'خضرلو'
        elif city_code == '53641':
            code = 'خلجان'
        elif city_code == '5321':
            code = 'سبلان'
        elif city_code == '5471':
            code = 'سراب'
        elif city_code == '5361':
            code = 'سردرود'
        elif city_code == '53851':
            code = 'سيس'
        elif city_code == '53671':
            code = 'شادبادمشايخ'
        elif city_code == '5381':
            code = 'شبستر'
        elif city_code == '54751':
            code = 'شربيان'
        elif city_code == '53891':
            code = 'شرفخانه'
        elif city_code == '5331':
            code = 'شهر جديد سهند'
        elif city_code == '53861':
            code = 'صوفيان'
        elif city_code == '5541':
            code = 'عجب شير'
        elif city_code == '5581':
            code = 'قره اغاج ـ چاراويماق'
        elif city_code == '54941':
            code = 'قره بابا'
        elif city_code == '54971':
            code = 'كردكندي'
        elif city_code == '5461':
            code = 'كليبر'
        elif city_code == '53681':
            code = 'كندرود'
        elif city_code == '54685':
            code = 'كندوان'
        elif city_code == '53761':
            code = 'گوگان'
        elif city_code == '551':
            code = 'مراغه'
        elif city_code == '541':
            code = 'مرند'
        elif city_code == '5561':
            code = 'ملكان'
        elif city_code == '53751':
            code = 'ممقان'
        elif city_code == '531':
            code = 'ميانه'
        elif city_code == '5431':
            code = 'هاديشهر'
        elif city_code == '5391':
            code = 'هريس'
        elif city_code == '5571':
            code = 'هشترود'
        elif city_code == '54491':
            code = 'هوراند'
        elif city_code == '54581':
            code = 'ورزقان'

    elif state_code == '4':
        if city_code == '6331':
            code = 'اروندكنار'
        elif city_code == '63731':
            code = 'اميديه'
        elif city_code == '6481':
            code = 'انديمشك'
        elif city_code == '61':
            code = 'اهواز'
        elif city_code == '6391':
            code = 'ايذه'
        elif city_code == '631':
            code = 'آبادان'
        elif city_code == '6371':
            code = 'آغاجاري'
        elif city_code == '63951':
            code = 'باغ ملك'
        elif city_code == '63561':
            code = 'بندرامام خميني'
        elif city_code == '6361':
            code = 'بهبهان'
        elif city_code == '63881':
            code = 'جايزان'
        elif city_code == '64541':
            code = 'جنت مكان'
        elif city_code == '63541':
            code = 'چمران ـ شهرك طالقاني'
        elif city_code == '63441':
            code = 'حميديه'
        elif city_code == '641':
            code = 'خرمشهر'
        elif city_code == '64651':
            code = 'دزآب'
        elif city_code == '6461':
            code = 'دزفول'
        elif city_code == '63991':
            code = 'دهدز'
        elif city_code == '63871':
            code = 'رامشير'
        elif city_code == '6381':
            code = 'رامهرمز'
        elif city_code == '63551':
            code = 'سربندر'
        elif city_code == '63681':
            code = 'سردشت'
        elif city_code == '64561':
            code = 'سماله'
        elif city_code == '6441':
            code = 'سوسنگرد ـ دشت آزادگان'
        elif city_code == '6431':
            code = 'شادگان'
        elif city_code == '64511':
            code = 'شرافت'
        elif city_code == '6471':
            code = 'شوش'
        elif city_code == '6451':
            code = 'شوشتر'
        elif city_code == '61481':
            code = 'شيبان'
        elif city_code == '64791':
            code = 'صالح مشطت'
        elif city_code == '63661':
            code = 'كردستان بزرگ'
        elif city_code == '64551':
            code = 'گتوند'
        elif city_code == '64941':
            code = 'لالي'
        elif city_code == '6351':
            code = 'ماهشهر'
        elif city_code == '6491':
            code = 'مسجد سليمان'
        elif city_code == '6341':
            code = 'ملاثاني'
        elif city_code == '63751':
            code = 'ميانكوه'
        elif city_code == '64961':
            code = 'هفتگل'
        elif city_code == '63591':
            code = 'هنديجان'
        elif city_code == '64451':
            code = 'هويزه'
        elif city_code == '61491':
            code = 'ويس'

    elif state_code == '5':
        if city_code == '73631':
            code = 'بيضا'
        elif city_code == '7361':
            code = 'اردكان ـ سپيدان'
        elif city_code == '73761':
            code = 'ارسنجان'
        elif city_code == '7451':
            code = 'استهبان'
        elif city_code == '74391':
            code = 'اشكنان ـ اهل'
        elif city_code == '7381':
            code = 'اقليد'
        elif city_code == '71651':
            code = 'اكبرآبادكوار'
        elif city_code == '74331':
            code = 'اوز'
        elif city_code == '73991':
            code = 'ايزدخواست'
        elif city_code == '7391':
            code = 'آباده'
        elif city_code == '74931':
            code = 'آباده طشك'
        elif city_code == '73391':
            code = 'بالاده'
        elif city_code == '73681':
            code = 'بانش'
        elif city_code == '74361':
            code = 'بنارويه'
        elif city_code == '73911':
            code = 'بهمن'
        elif city_code == '73941':
            code = 'بوانات'
        elif city_code == '73971':
            code = 'بوانات(سوريان)'
        elif city_code == '74381':
            code = 'بيرم'
        elif city_code == '74891':
            code = 'جنت شهر(دهخير)'
        elif city_code == '741':
            code = 'جهرم'
        elif city_code == '74351':
            code = 'جويم'
        elif city_code == '74861':
            code = 'حاجي آباد ـ زرين دشت'
        elif city_code == '73841':
            code = 'حسن آباد'
        elif city_code == '73441':
            code = 'خرامه'
        elif city_code == '74998':
            code = 'خرمی'
        elif city_code == '73341':
            code = 'خشت'
        elif city_code == '74431':
            code = 'خنج'
        elif city_code == '71451':
            code = 'خيرآبادتوللي'
        elif city_code == '7481':
            code = 'داراب'
        elif city_code == '71461':
            code = 'داريان'
        elif city_code == '74781':
            code = 'دهرم'
        elif city_code == '74461':
            code = 'رونيز'
        elif city_code == '74671':
            code = 'زاهدشهر'
        elif city_code == '7341':
            code = 'زرقان'
        elif city_code == '73451':
            code = 'سروستان'
        elif city_code == '73741':
            code = 'سعادت شهر ـ پاسارگاد'
        elif city_code == '73771':
            code = 'سيدان'
        elif city_code == '74651':
            code = 'ششده'
        elif city_code == '71991':
            code = 'شهر جديد صدرا'
        elif city_code == '71':
            code = 'شيراز'
        elif city_code == '73931':
            code = 'صغاد'
        elif city_code == '73951':
            code = 'صفاشهر ـ خرم بيد'
        elif city_code == '71641':
            code = 'طسوج'
        elif city_code == '74441':
            code = 'علاءمرودشت'
        elif city_code == '74871':
            code = 'فدامي'
        elif city_code == '74771':
            code = 'فراشبند'
        elif city_code == '7461':
            code = 'فسا'
        elif city_code == '7471':
            code = 'فيروزآباد'
        elif city_code == '74311':
            code = 'فيشور'
        elif city_code == '73751':
            code = 'قادرآباد'
        elif city_code == '73751':
            code = 'قائميه'
        elif city_code == '74551':
            code = 'قطب آباد'
        elif city_code == '74981':
            code = 'قطرويه'
        elif city_code == '74761':
            code = 'قير و كارزين'
        elif city_code == '731':
            code = 'كازرون'
        elif city_code == '73431':
            code = 'كام فيروز'
        elif city_code == '73141':
            code = 'كلاني'
        elif city_code == '73331':
            code = 'كنارتخته'
        elif city_code == '73461':
            code = 'كوار'
        elif city_code == '7441':
            code = 'گراش'
        elif city_code == '73491':
            code = 'گويم'
        elif city_code == '7431':
            code = 'لار ـ لارستان'
        elif city_code == '74341':
            code = 'لامرد'
        elif city_code == '74731':
            code = 'مبارك آباد'
        elif city_code == '7371':
            code = 'مرودشت'
        elif city_code == '74971':
            code = 'مشكان'
        elif city_code == '73571':
            code = 'مصيري ـ رستم'
        elif city_code == '71661':
            code = 'مظفري'
        elif city_code == '74451':
            code = 'مهر'
        elif city_code == '74741':
            code = 'ميمند'
        elif city_code == '7351':
            code = 'نورآباد ـ ممسني'
        elif city_code == '7491':
            code = 'ني ريز'
        elif city_code == '73171':
            code = 'وراوي'

    elif state_code == '6':
        if city_code == '81789':
            code = 'ابريشم'
        elif city_code == '87481':
            code = 'ابوزيدآباد'
        elif city_code == '8381':
            code = 'اردستان'
        elif city_code == '87641':
            code = 'اريسمان'
        elif city_code == '83781':
            code = 'اژيه'
        elif city_code == '8651':
            code = 'اسفرجان'
        elif city_code == '86481':
            code = 'اسلام آباد'
        elif city_code == '85451':
            code = 'اشن'
        elif city_code == '84351':
            code = 'اصغرآباد'
        elif city_code == '81':
            code = 'اصفهان'
        elif city_code == '86531':
            code = 'امين آباد'
        elif city_code == '84651':
            code = 'ايمان شهر'
        elif city_code == '8741':
            code = 'آران وبيدگل'
        elif city_code == '87661':
            code = 'بادرود'
        elif city_code == '84761':
            code = 'باغ بهادران'
        elif city_code == '81431':
            code = 'بهارستان'
        elif city_code == '85651':
            code = 'بوئين ومياندشت'
        elif city_code == '84541':
            code = 'پيربكران'
        elif city_code == '81351':
            code = 'تودشك'
        elif city_code == '8531':
            code = 'تيران'
        elif city_code == '84381':
            code = 'جعفرآباد'
        elif city_code == '83631':
            code = 'جندق'
        elif city_code == '84691':
            code = 'جوجيل'
        elif city_code == '8571':
            code = 'چادگان'
        elif city_code == '84751':
            code = 'چرمهين'
        elif city_code == '84781':
            code = 'چمگردان'
        elif city_code == '83791':
            code = 'حسن اباد'
        elif city_code == '87671':
            code = 'خالدآباد'
        elif city_code == '841':
            code = 'خميني شهر'
        elif city_code == '8791':
            code = 'خوانسار'
        elif city_code == '84531':
            code = 'خوانسارك'
        elif city_code == '8361':
            code = 'خور'
        elif city_code == '81561':
            code = 'خوراسگان'
        elif city_code == '83451':
            code = 'خورزوق'
        elif city_code == '8561':
            code = 'داران ـ فريدن'
        elif city_code == '8431':
            code = 'درچه پياز'
        elif city_code == '83431':
            code = 'دستگردوبرخوار'
        elif city_code == '8641':
            code = 'دهاقان'
        elif city_code == '8541':
            code = 'دهق'
        elif city_code == '8341':
            code = 'دولت آباد'
        elif city_code == '84831':
            code = 'ديزيچه'
        elif city_code == '85761':
            code = 'رزوه'
        elif city_code == '85331':
            code = 'رضوان شهر'
        elif city_code == '81879':
            code = 'رهنان'
        elif city_code == '84931':
            code = 'زاينده رود'
        elif city_code == '8471':
            code = 'زرين شهر ـ لنجان'
        elif city_code == '8441':
            code = 'زواره'
        elif city_code == '81681':
            code = 'زيار'
        elif city_code == '84841':
            code = 'زيبا شهر'
        elif city_code == '87992':
            code = 'سپاهان شهر'
        elif city_code == '84741':
            code = 'سده لنجان'
        elif city_code == '8661':
            code = 'سميرم'
        elif city_code == '831':
            code = 'شاهين شهر'
        elif city_code == '861':
            code = 'شهرضا'
        elif city_code == '83331':
            code = 'شهرك صنعتي مورچ'
        elif city_code == '8631':
            code = 'شهرك مجلسي'
        elif city_code == '8161':
            code = 'شهرک صنعتي محمودآباد'
        elif city_code == '84981':
            code = 'طالخونچه'
        elif city_code == '85351':
            code = 'عسگران'
        elif city_code == '8551':
            code = 'علويچه'
        elif city_code == '85631':
            code = 'غرغن'
        elif city_code == '83641':
            code = 'فرخي'
        elif city_code == '8591':
            code = 'فريدون شهر'
        elif city_code == '8451':
            code = 'فلاورجان'
        elif city_code == '8491':
            code = 'فولادشهر'
        elif city_code == '84881':
            code = 'فولادمباركه'
        elif city_code == '8461':
            code = 'قهد ريجان'
        elif city_code == '871':
            code = 'كاشان'
        elif city_code == '84561':
            code = 'كليشادوسودرجان'
        elif city_code == '83591':
            code = 'كمشچه'
        elif city_code == '8371':
            code = 'كوهپايه'
        elif city_code == '83441':
            code = 'گز'
        elif city_code == '8771':
            code = 'گلپايگان'
        elif city_code == '85831':
            code = 'گلدشت'
        elif city_code == '87841':
            code = 'گلشهر'
        elif city_code == '8781':
            code = 'گوگد'
        elif city_code == '8481':
            code = 'مباركه'
        elif city_code == '84431':
            code = 'مهاباد'
        elif city_code == '8331':
            code = 'مورچه خورت'
        elif city_code == '8351':
            code = 'ميمه'
        elif city_code == '8391':
            code = 'نائين'
        elif city_code == '851':
            code = 'نجف آباد'
        elif city_code == '81751':
            code = 'نصر آباد'
        elif city_code == '8761':
            code = 'نطنز'
        elif city_code == '83771':
            code = 'نيك آباد'
        elif city_code == '81431':
            code = 'بهارستان'
        elif city_code == '83741':
            code = 'هرند'
        elif city_code == '83751':
            code = 'ورزنه'
        elif city_code == '84731':
            code = 'ورنامخواست'
        elif city_code == '8581':
            code = 'ویلاشهر'

    elif state_code == '7':
        if city_code == '95781':
            code = 'ابدال آباد'
        elif city_code == '96441':
            code = 'ازادوار'
        elif city_code == '94861':
            code = 'باجگيران'
        elif city_code == '95971':
            code = 'باخرز'
        elif city_code == '95481':
            code = 'باسفر'
        elif city_code == '96981':
            code = 'بجستان'
        elif city_code == '9681':
            code = 'بردسكن'
        elif city_code == '97741':
            code = 'برون'
        elif city_code == '93871':
            code = 'بزنگان'
        elif city_code == '96791':
            code = 'بند قرائ'
        elif city_code == '96941':
            code = 'بيدخت'
        elif city_code == '9591':
            code = 'تايباد'
        elif city_code == '9571':
            code = 'تربت جام'
        elif city_code == '951':
            code = 'تربت حيدريه'
        elif city_code == '9641':
            code = 'جغتاي'
        elif city_code == '95471':
            code = 'جنگل'
        elif city_code == '95671':
            code = 'چمن آباد'
        elif city_code == '9361':
            code = 'چناران'
        elif city_code == '96771':
            code = 'خليل آباد'
        elif city_code == '9561':
            code = 'خواف'
        elif city_code == '9631':
            code = 'داورزن'
        elif city_code == '9491':
            code = 'درگز'
        elif city_code == '95491':
            code = 'دولت آباد ـ زاوه'
        elif city_code == '93631':
            code = 'رادكان'
        elif city_code == '9541':
            code = 'رشتخوار'
        elif city_code == '91671':
            code = 'رضويه'
        elif city_code == '96741':
            code = 'ريوش(كوهسرخ)'
        elif city_code == '961':
            code = 'سبزوار'
        elif city_code == '9381':
            code = 'سرخس'
        elif city_code == '96561':
            code = 'سلطان آباد'
        elif city_code == '95641':
            code = 'سنگان'
        elif city_code == '93561':
            code = 'شانديز'
        elif city_code == '9581':
            code = 'صالح آباد'
        elif city_code == '9351':
            code = 'طرقبه ـ بينالود'
        elif city_code == '93571':
            code = 'طوس سفلي'
        elif city_code == '9391':
            code = 'فريمان'
        elif city_code == '9331':
            code = 'فيروزه ـ تخت جلگه'
        elif city_code == '9531':
            code = 'فيض آباد ـ مه ولات'
        elif city_code == '95661':
            code = 'قاسم آباد'
        elif city_code == '93461':
            code = 'قدمگاه'
        elif city_code == '9471':
            code = 'قوچان'
        elif city_code == '96961':
            code = 'كاخك'
        elif city_code == '9671':
            code = 'كاشمر'
        elif city_code == '9371':
            code = 'كلات'
        elif city_code == '93651':
            code = 'گلبهار'
        elif city_code == '9691':
            code = 'گناباد'
        elif city_code == '94941':
            code = 'لطف آباد'
        elif city_code == '91':
            code = 'مشهد'
        elif city_code == '95961':
            code = 'مشهدريزه'
        elif city_code == '97761':
            code = 'مصعبي'
        elif city_code == '95631':
            code = 'نشتيفان'
        elif city_code == '96471':
            code = 'نقاب ـ جوين'
        elif city_code == '931':
            code = 'نيشابور'
        elif city_code == '95751':
            code = 'نيل شهر'

    elif state_code == '8':
        if city_code == '3461':
            code = 'آوج'
        elif city_code == '34671':
            code = 'ارداق'
        elif city_code == '34561':
            code = 'اسفرورين'
        elif city_code == '34171':
            code = 'اقباليه'
        elif city_code == '3431':
            code = 'الوند ـ البرز'
        elif city_code == '34641':
            code = 'آبگرم'
        elif city_code == '3441':
            code = 'آبيك'
        elif city_code == '34791':
            code = 'آقابابا'
        elif city_code == '3451':
            code = 'بوئين زهرا'
        elif city_code == '34151':
            code = 'بیدستان'
        elif city_code == '3481':
            code = 'تاكستان'
        elif city_code == '34691':
            code = 'حصاروليعصر'
        elif city_code == '34481':
            code = 'خاكعلي'
        elif city_code == '34831':
            code = 'خرم دشت'
        elif city_code == '34581':
            code = 'دانسفهان'
        elif city_code == '34741':
            code = 'سيردان'
        elif city_code == '34571':
            code = 'شال'
        elif city_code == '3410':
            code = 'شهر صنعتي البرز'
        elif city_code == '34851':
            code = 'ضياآباد'
        elif city_code == '341':
            code = 'قزوين'
        elif city_code == '34491':
            code = 'ليا'
        elif city_code == '3491':
            code = 'محمديه'
        elif city_code == '34131':
            code = 'محمود آباد نمونه'
        elif city_code == '34931':
            code = 'معلم كلايه'
        elif city_code == '34811':
            code = 'نرجه'

    elif state_code == '9':
        if city_code == '35861':
            code = 'ارادان'
        elif city_code == '3681':
            code = 'اميريه'
        elif city_code == '3591':
            code = 'ايوانكي'
        elif city_code == '3641':
            code = 'بسطام'
        elif city_code == '3661':
            code = 'بيارجمند'
        elif city_code == '35331':
            code = 'خيرآباد'
        elif city_code == '3671':
            code = 'دامغان'
        elif city_code == '35631':
            code = 'درجزين'
        elif city_code == '3551':
            code = 'سرخه'
        elif city_code == '351':
            code = 'سمنان'
        elif city_code == '361':
            code = 'شاهرود'
        elif city_code == '3571':
            code = 'شهميرزاد'
        elif city_code == '3581':
            code = 'گرمسار'
        elif city_code == '3651':
            code = 'مجن'
        elif city_code == '3561':
            code = 'مهدي شهر'
        elif city_code == '3631':
            code = 'ميامي'
        elif city_code == '36441':
            code = 'ميغان'

    elif state_code == '10':
        if city_code == '3741':
            code = 'دستجرد'
        elif city_code == '37461':
            code = 'سلفچگان'
        elif city_code == '37441':
            code = 'شهر جعفریه'
        elif city_code == '371':
            code = 'قم'
        elif city_code == '3731':
            code = 'قنوات'
        elif city_code == '37351':
            code = 'كهك'

    elif state_code == '11':
        if city_code == '381':
            code = 'اراك'
        elif city_code == '3871':
            code = 'آستانه'
        elif city_code == '3961':
            code = 'آشتيان'
        elif city_code == '3951':
            code = 'تفرش'
        elif city_code == '38661':
            code = 'توره'
        elif city_code == '38451':
            code = 'جاورسيان'
        elif city_code == '38541':
            code = 'خسروبيك'
        elif city_code == '37761':
            code = 'خشك رود'
        elif city_code == '3881':
            code = 'خمين'
        elif city_code == '3841':
            code = 'خنداب'
        elif city_code == '3791':
            code = 'دليجان'
        elif city_code == '38941':
            code = 'ريحان عليا'
        elif city_code == '39441':
            code = 'زاويه'
        elif city_code == '391':
            code = 'ساوه'
        elif city_code == '3861':
            code = 'شازند'
        elif city_code == '39541':
            code = 'شهراب'
        elif city_code == '3991':
            code = 'شهرك مهاجران'
        elif city_code == '39531':
            code = 'فرمهين'
        elif city_code == '3851':
            code = 'كميجان'
        elif city_code == '3941':
            code = 'مامونيه ـ زرنديه'
        elif city_code == '3781':
            code = 'محلات'
        elif city_code == '38551':
            code = 'ميلاجرد'
        elif city_code == '38761':
            code = 'هندودر'

    elif state_code == '12':
        if city_code == '4591':
            code = 'آب بر ـ طارم'
        elif city_code == '4561':
            code = 'ابهر'
        elif city_code == '45371':
            code = 'اسفجين'
        elif city_code == '45431':
            code = 'پري'
        elif city_code == '45971':
            code = 'حلب'
        elif city_code == '4571':
            code = 'خرمدره'
        elif city_code == '45941':
            code = 'دستجرده'
        elif city_code == '45471':
            code = 'دندي'
        elif city_code == '4531':
            code = 'زرين آباد ـ ايجرود'
        elif city_code == '45881':
            code = 'زرين رود'
        elif city_code == '451':
            code = 'زنجان'
        elif city_code == '4551':
            code = 'سلطانيه'
        elif city_code == '45741':
            code = 'صائين قلعه'
        elif city_code == '4581':
            code = 'قيدار'
        elif city_code == '45871':
            code = 'گرماب'
        elif city_code == '45931':
            code = 'گيلوان'
        elif city_code == '4541':
            code = 'ماهنشان'
        elif city_code == '45331':
            code = 'همايون'
        elif city_code == '45731':
            code = 'هيدج'

    elif state_code == '13':
        if city_code == '48451':
            code = 'اسلام آباد'
        elif city_code == '4731':
            code = 'اميركلا'
        elif city_code == '46411':
            code = 'ايزدشهر'
        elif city_code == '461':
            code = 'آمل'
        elif city_code == '47341':
            code = 'آهنگركلا'
        elif city_code == '471':
            code = 'بابل'
        elif city_code == '4741':
            code = 'بابلسر'
        elif city_code == '46471':
            code = 'بلده'
        elif city_code == '4851':
            code = 'بهشهر'
        elif city_code == '47441':
            code = 'بهنمير'
        elif city_code == '4791':
            code = 'پل سفيد ـ سوادكوه'
        elif city_code == '4681':
            code = 'تنكابن'
        elif city_code == '4771':
            code = 'جويبار'
        elif city_code == '4661':
            code = 'چالوس'
        elif city_code == '46431':
            code = 'چمستان'
        elif city_code == '46851':
            code = 'خرم آباد'
        elif city_code == '47331':
            code = 'خوشرودپی'
        elif city_code == '4691':
            code = 'رامسر'
        elif city_code == '48561':
            code = 'رستم كلا'
        elif city_code == '46561':
            code = 'رويانشهر'
        elif city_code == '48541':
            code = 'زاغمرز'
        elif city_code == '47581':
            code = 'زرگر محله'
        elif city_code == '4781':
            code = 'زيرآب'
        elif city_code == '46931':
            code = 'سادات محله'
        elif city_code == '481':
            code = 'ساري'
        elif city_code == '46341':
            code = 'سرخرود'
        elif city_code == '4671':
            code = 'سلمانشهر'
        elif city_code == '48351':
            code = 'سنگده'
        elif city_code == '46371':
            code = 'سوا'
        elif city_code == '48441':
            code = 'سورك'
        elif city_code == '47871':
            code = 'شيرگاه'
        elif city_code == '46861':
            code = 'شيرود'
        elif city_code == '46741':
            code = 'عباس آباد'
        elif city_code == '4751':
            code = 'فريدون كنار'
        elif city_code == '4761':
            code = 'قائم شهر'
        elif city_code == '46731':
            code = 'كلارآباد'
        elif city_code == '46661':
            code = 'كلاردشت'
        elif city_code == '47731':
            code = 'كيا كلا'
        elif city_code == '4831':
            code = 'كياسر'
        elif city_code == '46391':
            code = 'گزنك'
        elif city_code == '4861':
            code = 'گلوگاه'
        elif city_code == '48461':
            code = 'گهرباران'
        elif city_code == '4631':
            code = 'محمودآباد'
        elif city_code == '46641':
            code = 'مرزن آباد'
        elif city_code == '47561':
            code = 'مرزي كلا'
        elif city_code == '46831':
            code = 'نشتارود'
        elif city_code == '4841':
            code = 'نكاء'
        elif city_code == '4641':
            code = 'نور'
        elif city_code == '4651':
            code = 'نوشهر'

    elif state_code == '14':
        if city_code == '49391':
            code = 'انبار آلوم'
        elif city_code == '49751':
            code = 'اينچه برون'
        elif city_code == '4961':
            code = 'آزادشهر'
        elif city_code == '4931':
            code = 'آق قلا'
        elif city_code == '4871':
            code = 'بندر گز'
        elif city_code == '4891':
            code = 'بندرتركمن'
        elif city_code == '49351':
            code = 'جلين'
        elif city_code == '49531':
            code = 'خان ببين'
        elif city_code == '4951':
            code = 'راميان'
        elif city_code == '48971':
            code = 'سيمين شهر'
        elif city_code == '4941':
            code = 'علي آباد'
        elif city_code == '49431':
            code = 'فاضل آباد'
        elif city_code == '4881':
            code = 'كردكوي'
        elif city_code == '4991':
            code = 'كلاله'
        elif city_code == '49831':
            code = 'گاليكش'
        elif city_code == '491':
            code = 'گرگان'
        elif city_code == '48961':
            code = 'گميش تپه'
        elif city_code == '4971':
            code = 'گنبدكاوس'
        elif city_code == '48733':
            code = 'مراوه تپه'
        elif city_code == '4981':
            code = 'مينودشت'

    elif state_code == '15':
        if city_code == '56331':
            code = 'ابي بيگلو'
        elif city_code == '561':
            code = 'اردبيل'
        elif city_code == '56981':
            code = 'اصلاندوز'
        elif city_code == '5671':
            code = 'بيله سوار'
        elif city_code == '5691':
            code = 'پارس آباد'
        elif city_code == '56581':
            code = 'تازه كند انگوت'
        elif city_code == '56751':
            code = 'جعفرآباد'
        elif city_code == '5681':
            code = 'خلخال'
        elif city_code == '56391':
            code = 'سرعين'
        elif city_code == '56971':
            code = 'شهرك شهيد غفاري'
        elif city_code == '56891':
            code = 'كلور'
        elif city_code == '56431':
            code = 'كوارئيم'
        elif city_code == '5651':
            code = 'گرمي'
        elif city_code == '56851':
            code = 'گيوي ـ كوثر'
        elif city_code == '56653':
            code = 'لاهرود'
        elif city_code == '5661':
            code = 'مشگين شهر'
        elif city_code == '5631':
            code = 'نمين'
        elif city_code == '5641':
            code = 'نير'
        elif city_code == '56871':
            code = 'هشتجين'

    elif state_code == '16':
        if city_code == '571':
            code = 'اروميه'
        elif city_code == '5771':
            code = 'اشنويه'
        elif city_code == '5831':
            code = 'ايواوغلي'
        elif city_code == '58671':
            code = 'بازرگان'
        elif city_code == '5951':
            code = 'بوكان'
        elif city_code == '57951':
            code = 'پسوه'
        elif city_code == '58771':
            code = 'پلدشت'
        elif city_code == '5781':
            code = 'پيرانشهر'
        elif city_code == '5891':
            code = 'تازه شهر'
        elif city_code == '5991':
            code = 'تكاب'
        elif city_code == '59771':
            code = 'چهاربرج قديم'
        elif city_code == '581':
            code = 'خوي'
        elif city_code == '57451':
            code = 'ديزج'
        elif city_code == '5837':
            code = 'ديزجديز'
        elif city_code == '59691':
            code = 'ربط'
        elif city_code == '57461':
            code = 'زيوه'
        elif city_code == '5961':
            code = 'سردشت'
        elif city_code == '5881':
            code = 'سلماس'
        elif city_code == '57411':
            code = 'سيلوانا'
        elif city_code == '573':
            code = 'سيلوه'
        elif city_code == '5871':
            code = 'سيه چشمه ـ چالدران'
        elif city_code == '5981':
            code = 'شاهين دژ'
        elif city_code == '58751':
            code = 'شوط'
        elif city_code == '5851':
            code = 'قره ضياء الدين ـ چايپاره'
        elif city_code == '5751':
            code = 'قوشچي'
        elif city_code == '59731':
            code = 'كشاورز (اقبال)'
        elif city_code == '5861':
            code = 'ماكو'
        elif city_code == '57661':
            code = 'محمد يار'
        elif city_code == '59861':
            code = 'محمودآباد'
        elif city_code == '591':
            code = 'مهاباد'
        elif city_code == '5971':
            code = 'مياندوآب'
        elif city_code == '57351':
            code = 'مياوق'
        elif city_code == '59671':
            code = 'ميرآباد'
        elif city_code == '5761':
            code = 'نقده'
        elif city_code == '57381':
            code = 'نوشين شهر'

    elif state_code == '17':
        if city_code == '65995':
            code = 'ازندريان'
        elif city_code == '6541':
            code = 'اسدآباد'
        elif city_code == '65791':
            code = 'اسلام آباد'
        elif city_code == '6531':
            code = 'بهار'
        elif city_code == '65992':
            code = 'پايگاه نوژه'
        elif city_code == '6581':
            code = 'تويسركان'
        elif city_code == '65671':
            code = 'دمق'
        elif city_code == '65681':
            code = 'رزن'
        elif city_code == '65761':
            code = 'سامن'
        elif city_code == '65841':
            code = 'سركان'
        elif city_code == '65571':
            code = 'شيرين سو'
        elif city_code == '65361':
            code = 'صالح آباد'
        elif city_code == '6561':
            code = 'فامنين'
        elif city_code == '65691':
            code = 'قروه درجزين'
        elif city_code == '65631':
            code = 'قهاوند'
        elif city_code == '6551':
            code = 'كبودرآهنگ'
        elif city_code == '65961':
            code = 'گيان'
        elif city_code == '65331':
            code = 'لالجين'
        elif city_code == '6571':
            code = 'ملاير'
        elif city_code == '6591':
            code = 'نهاوند'
        elif city_code == '651':
            code = 'همدان'

    elif state_code == '18':
        if city_code == '66791':
            code = 'اورامانتخت'
        elif city_code == '6691':
            code = 'بانه'
        elif city_code == '66661':
            code = 'بلبان آباد'
        elif city_code == '6651':
            code = 'بيجار'
        elif city_code == '66631':
            code = 'دلبران'
        elif city_code == '66671':
            code = 'دهگلان'
        elif city_code == '6641':
            code = 'ديواندره'
        elif city_code == '66781':
            code = 'سروآباد'
        elif city_code == '66691':
            code = 'سريش آباد'
        elif city_code == '6681':
            code = 'سقز'
        elif city_code == '661':
            code = 'سنندج'
        elif city_code == '6661':
            code = 'قروه'
        elif city_code == '6631':
            code = 'كامياران'
        elif city_code == '6671':
            code = 'مريوان'
        elif city_code == '66391':
            code = 'موچش'

    elif state_code == '19':
        if city_code == '6761':
            code = 'اسلام آباد غرب'
        elif city_code == '67931':
            code = 'باينگان'
        elif city_code == '67371':
            code = 'بيستون'
        elif city_code == '6791':
            code = 'پاوه'
        elif city_code == '67771':
            code = 'تازه آباد ـ ثلاث باباجاني'
        elif city_code == '67981':
            code = 'جوانرود'
        elif city_code == '67961':
            code = 'روانسر'
        elif city_code == '67651':
            code = 'ريجاب'
        elif city_code == '67741':
            code = 'سراب ذهاب'
        elif city_code == '6771':
            code = 'سرپل ذهاب'
        elif city_code == '6751':
            code = 'سنقر'
        elif city_code == '67461':
            code = 'صحنه'
        elif city_code == '67441':
            code = 'فرامان'
        elif city_code == '67431':
            code = 'فش'
        elif city_code == '6781':
            code = 'قصرشيرين'
        elif city_code == '671':
            code = 'كرمانشاه'
        elif city_code == '6741':
            code = 'كنگاور'
        elif city_code == '67871':
            code = 'گيلانغرب'
        elif city_code == '67951':
            code = 'نودشه'
        elif city_code == '6731':
            code = 'هرسين'
        elif city_code == '67341':
            code = 'هلشي'

    elif state_code == '20':
        if city_code == '6871':
            code = 'ازنا'
        elif city_code == '6891':
            code = 'الشتر ـ سلسله'
        elif city_code == '6861':
            code = 'اليگودرز'
        elif city_code == '68331':
            code = 'برخوردار'
        elif city_code == '691':
            code = 'بروجرد'
        elif city_code == '6851':
            code = 'پل دختر'
        elif city_code == '68391':
            code = 'تقي آباد'
        elif city_code == '68181':
            code = 'چغلوندی'
        elif city_code == '68451':
            code = 'چقابل'
        elif city_code == '681':
            code = 'خرم آباد'
        elif city_code == '6881':
            code = 'دورود'
        elif city_code == '68761':
            code = 'زاغه'
        elif city_code == '68861':
            code = 'سپيددشت'
        elif city_code == '68671':
            code = 'شول آباد'
        elif city_code == '68471':
            code = 'كوناني'
        elif city_code == '6841':
            code = 'كوهدشت'
        elif city_code == '68571':
            code = 'معمولان'
        elif city_code == '6831':
            code = 'نورآباد ـ دلفان'
        elif city_code == '68541':
            code = 'واشيان نصيرتپه'

    elif state_code == '21':
        if city_code == '75551':
            code = 'ابدان'
        elif city_code == '7551':
            code = 'اهرم ـ تنگستان'
        elif city_code == '75491':
            code = 'آباد'
        elif city_code == '75651':
            code = 'آبپخش'
        elif city_code == '75431':
            code = 'بادوله'
        elif city_code == '7561':
            code = 'برازجان ـ دشتستان'
        elif city_code == '75531':
            code = 'بردخون'
        elif city_code == '75541':
            code = 'بندردير'
        elif city_code == '75361':
            code = 'بندرديلم'
        elif city_code == '75331':
            code = 'بندرريگ'
        elif city_code == '75571':
            code = 'بندركنگان'
        elif city_code == '7531':
            code = 'بندرگناوه'
        elif city_code == '751':
            code = 'بوشهر'
        elif city_code == '75681':
            code = 'تنگ ارم'
        elif city_code == '75461':
            code = 'جزيره خارك'
        elif city_code == '75581':
            code = 'جم'
        elif city_code == '75381':
            code = 'چغارك'
        elif city_code == '7541':
            code = 'خورموج ـ دشتي'
        elif city_code == '75471':
            code = 'دلوار'
        elif city_code == '75561':
            code = 'ريز'
        elif city_code == '75661':
            code = 'سعدآباد'
        elif city_code == '75641':
            code = 'شبانكاره'
        elif city_code == '75441':
            code = 'شنبه'
        elif city_code == '75351':
            code = 'شول'
        elif city_code == '75196':
            code = 'عالی شهر'
        elif city_code == '75391':
            code = 'عسلويه'
        elif city_code == '75451':
            code = 'كاكي'
        elif city_code == '75691':
            code = 'كلمه'
        elif city_code == '75111':
            code = 'نخل تقي'
        elif city_code == '75671':
            code = 'وحدتيه'

    elif state_code == '22':
        if city_code == '76381':
            code = 'اختيارآباد'
        elif city_code == '78591':
            code = 'ارزوئیه'
        elif city_code == '77431':
            code = 'امين شهر'
        elif city_code == '7741':
            code = 'انار'
        elif city_code == '76371':
            code = 'باغين'
        elif city_code == '7851':
            code = 'بافت'
        elif city_code == '7841':
            code = 'بردسير'
        elif city_code == '78791':
            code = 'بلوك'
        elif city_code == '7661':
            code = 'بم'
        elif city_code == '77461':
            code = 'بهرمان'
        elif city_code == '7831':
            code = 'پاريز'
        elif city_code == '77471':
            code = 'جواديه فلاح'
        elif city_code == '76431':
            code = 'جوشان'
        elif city_code == '7861':
            code = 'جيرفت'
        elif city_code == '7791':
            code = 'چترود'
        elif city_code == '77761':
            code = 'خانوك'
        elif city_code == '78771':
            code = 'دوساري'
        elif city_code == '78561':
            code = 'رابر'
        elif city_code == '7651':
            code = 'راور'
        elif city_code == '7681':
            code = 'راين'
        elif city_code == '771':
            code = 'رفسنجان'
        elif city_code == '78831':
            code = 'رودبار'
        elif city_code == '76761':
            code = 'ريگان'
        elif city_code == '7761':
            code = 'زرند'
        elif city_code == '76391':
            code = 'زنگي آباد'
        elif city_code == '7731':
            code = 'سرچشمه'
        elif city_code == '77751':
            code = 'سريز'
        elif city_code == '781':
            code = 'سيرجان'
        elif city_code == '7751':
            code = 'شهربابك'
        elif city_code == '77391':
            code = 'صفائيه'
        elif city_code == '7871':
            code = 'عنبرآباد'
        elif city_code == '78871':
            code = 'فارياب'
        elif city_code == '76741':
            code = 'فهرج'
        elif city_code == '78841':
            code = 'قلعه گنج'
        elif city_code == '77951':
            code = 'كاظم آباد'
        elif city_code == '761':
            code = 'كرمان'
        elif city_code == '7881':
            code = 'كهنوج'
        elif city_code == '77941':
            code = 'كهنوج( مغزآباد)'
        elif city_code == '7781':
            code = 'كوهبنان'
        elif city_code == '7771':
            code = 'كيان شهر'
        elif city_code == '7641':
            code = 'گلباف'
        elif city_code == '7631':
            code = 'ماهان'
        elif city_code == '7691':
            code = 'محمدآباد ـ ريگان'
        elif city_code == '76891':
            code = 'محي آباد'
        elif city_code == '7891':
            code = 'منوجان'
        elif city_code == '78151':
            code = 'نجف شهر'
        elif city_code == '78431':
            code = 'نگار'

    elif state_code == '23':
        if city_code == '79591':
            code = 'ابوموسي'
        elif city_code == '79331':
            code = 'ايسين'
        elif city_code == '7961':
            code = 'بستك'
        elif city_code == '7931':
            code = 'بندرخمير'
        elif city_code == '791':
            code = 'بندرعباس'
        elif city_code == '7971':
            code = 'بندر لنگه'
        elif city_code == '79981':
            code = 'بندزك كهنه'
        elif city_code == '79771':
            code = 'پارسيان'
        elif city_code == '79631':
            code = 'پدل'
        elif city_code == '79341':
            code = 'پل شرقي'
        elif city_code == '79971':
            code = 'تياب'
        elif city_code == '79791':
            code = 'جاسك'
        elif city_code == '79581':
            code = 'جزيره سيري'
        elif city_code == '79781':
            code = 'جزيره لاوان'
        elif city_code == '79571':
            code = 'جزيره هنگام'
        elif city_code == '79561':
            code = 'جزيره لارك'
        elif city_code == '79611':
            code = 'جناح'
        elif city_code == '79751':
            code = 'چارك'
        elif city_code == '79391':
            code = 'حاجي آباد'
        elif city_code == '79531':
            code = 'درگهان'
        elif city_code == '79761':
            code = 'دشتي'
        elif city_code == '7991':
            code = 'دهبارز ـ رودان'
        elif city_code == '79661':
            code = 'رويدر'
        elif city_code == '79941':
            code = 'زيارت علي'
        elif city_code == '79881':
            code = 'سردشت ـ بشاگرد'
        elif city_code == '79841':
            code = 'سندرك'
        elif city_code == '79461':
            code = 'سيريك'
        elif city_code == '79371':
            code = 'فارغان'
        elif city_code == '79351':
            code = 'فين'
        elif city_code == '7951':
            code = 'قشم'
        elif city_code == '79641':
            code = 'كنگ'
        elif city_code == '7941':
            code = 'كيش'
        elif city_code == '7981':
            code = 'ميناب'

    elif state_code == '24':
        if city_code == '8881':
            code = 'اردل'
        elif city_code == '88941':
            code = 'آلوني'
        elif city_code == '88631':
            code = 'باباحيدر'
        elif city_code == '8871':
            code = 'بروجن'
        elif city_code == '88761':
            code = 'بلداجي'
        elif city_code == '88581':
            code = 'بن'
        elif city_code == '88671':
            code = 'جونقان'
        elif city_code == '88471':
            code = 'چالشتر'
        elif city_code == '88651':
            code = 'چلگرد ـ كوهرنگ'
        elif city_code == '8834':
            code = 'دزك'
        elif city_code == '88361':
            code = 'دستنائ'
        elif city_code == '88881':
            code = 'دشتك'
        elif city_code == '8851':
            code = 'سامان'
        elif city_code == '88461':
            code = 'سودجان'
        elif city_code == '88431':
            code = 'سورشجان'
        elif city_code == '88371':
            code = 'شلمزار ـ كيار'
        elif city_code == '881':
            code = 'شهركرد'
        elif city_code == '8861':
            code = 'فارسان'
        elif city_code == '88741':
            code = 'فرادنبه'
        elif city_code == '8831':
            code = 'فرخ شهر'
        elif city_code == '88139':
            code = 'كیان'
        elif city_code == '88781':
            code = 'گندمان'
        elif city_code == '88381':
            code = 'گهرو'
        elif city_code == '8891':
            code = 'لردگان'
        elif city_code == '88951':
            code = 'مال خليفه'
        elif city_code == '88831':
            code = 'ناغان'
        elif city_code == '8844':
            code = 'هاروني'
        elif city_code == '8841':
            code = 'هفشجان'
        elif city_code == '88571':
            code = 'وردنجان'

    elif state_code == '25':
        if city_code == '8931':
            code = 'ابركوه'
        elif city_code == '89531':
            code = 'احمدآباد'
        elif city_code == '8951':
            code = 'اردكان'
        elif city_code == '8971':
            code = 'بافق'
        elif city_code == '89631':
            code = 'بفروئيه'
        elif city_code == '89761':
            code = 'بهاباد'
        elif city_code == '8991':
            code = 'تفت'
        elif city_code == '89491':
            code = 'حميديا'
        elif city_code == '89418':
            code = 'زارچ'
        elif city_code == '89431':
            code = 'شاهديه'
        elif city_code == '8941':
            code = 'صدوق'
        elif city_code == '9791':
            code = 'طبس'
        elif city_code == '97981':
            code = 'عشق آباد'
        elif city_code == '89331':
            code = 'فراغه'
        elif city_code == '89871':
            code = 'مروست'
        elif city_code == '8981':
            code = 'مهريز'
        elif city_code == '8961':
            code = 'ميبد'
        elif city_code == '89961':
            code = 'نير'
        elif city_code == '89881':
            code = 'هرات ـ خاتم'
        elif city_code == '891':
            code = 'يزد'

    elif state_code == '26':
        if city_code == '99431':
            code = 'اسپكه'
        elif city_code == '991':
            code = 'ايرانشهر'
        elif city_code == '99491':
            code = 'بزمان'
        elif city_code == '9941':
            code = 'بمپور'
        elif city_code == '99451':
            code = 'بنت'
        elif city_code == '98691':
            code = 'بنجار'
        elif city_code == '99641':
            code = 'پسكو'
        elif city_code == '98641':
            code = 'تيموراباد'
        elif city_code == '99561':
            code = 'جالق'
        elif city_code == '9971':
            code = 'چابهار'
        elif city_code == '9891':
            code = 'خاش'
        elif city_code == '9851':
            code = 'دوست محمد ـ هيرمند'
        elif city_code == '99361':
            code = 'راسك'
        elif city_code == '9861':
            code = 'زابل'
        elif city_code == '99661':
            code = 'زابلي'
        elif city_code == '981':
            code = 'زاهدان'
        elif city_code == '9871':
            code = 'زهك'
        elif city_code == '99991':
            code = 'ساربوك'
        elif city_code == '9951':
            code = 'سراوان'
        elif city_code == '9931':
            code = 'سرباز'
        elif city_code == '98971':
            code = 'سنگان'
        elif city_code == '9961':
            code = 'سوران ـ سيب سوران'
        elif city_code == '99571':
            code = 'سيركان'
        elif city_code == '99461':
            code = 'فنوج'
        elif city_code == '99961':
            code = 'قصرقند'
        elif city_code == '9981':
            code = 'كنارك'
        elif city_code == '99881':
            code = 'كيتج'
        elif city_code == '99471':
            code = 'گلمورتي ـ دلگان'
        elif city_code == '98931':
            code = 'گوهركوه'
        elif city_code == '98681':
            code = 'محمدآباد'
        elif city_code == '9841':
            code = 'ميرجاوه'
        elif city_code == '9831':
            code = 'نصرت آباد'
        elif city_code == '99761':
            code = 'نگور'
        elif city_code == '9991':
            code = 'نيك شهر'
        elif city_code == '99671':
            code = 'هيدوچ'

    elif state_code == '27':
        if city_code == '69971':
            code = 'اركواز'
        elif city_code == '69641':
            code = 'ارمو'
        elif city_code == '6931':
            code = 'ايلام'
        elif city_code == '6941':
            code = 'ايوان'
        elif city_code == '6971':
            code = 'آبدانان'
        elif city_code == '69561':
            code = 'آسمان آباد'
        elif city_code == '69671':
            code = 'بدره'
        elif city_code == '69531':
            code = 'توحيد'
        elif city_code == '69661':
            code = 'چشمه شيرين'
        elif city_code == '69361':
            code = 'چوار'
        elif city_code == '6961':
            code = 'دره شهر'
        elif city_code == '6981':
            code = 'دهلران'
        elif city_code == '6951':
            code = 'سرابله ـ شيروان و چرداول'
        elif city_code == '69511':
            code = 'شباب'
        elif city_code == '69931':
            code = 'شهرك اسلاميه'
        elif city_code == '69551':
            code = 'لومار'
        elif city_code == '6991':
            code = 'مهران'
        elif city_code == '69841':
            code = 'موسيان'
        elif city_code == '69861':
            code = 'ميمه'

    elif state_code == '28':
        if city_code == '75881':
            code = 'باشت'
        elif city_code == '75981':
            code = 'پاتاوه'
        elif city_code == '75761':
            code = 'چرام'
        elif city_code == '7571':
            code = 'دهدشت ـ كهگيلويه'
        elif city_code == '7581':
            code = 'دوگنبدان ـ گچساران'
        elif city_code == '75771':
            code = 'ديشموك'
        elif city_code == '75931':
            code = 'سپيدار'
        elif city_code == '75731':
            code = 'سوق'
        elif city_code == '75991':
            code = 'سي سخت ـ دنا'
        elif city_code == '75781':
            code = 'قلعه رئيسي'
        elif city_code == '75741':
            code = 'لنده'
        elif city_code == '75751':
            code = 'ليكك'
        elif city_code == '75911':
            code = 'مادوان'
        elif city_code == '7591':
            code = 'ياسوج'

    elif state_code == '29':
        if city_code == '9661':
            code = 'اسفراين'
        elif city_code == '94331':
            code = 'ايور'
        elif city_code == '9451':
            code = 'آشخانه ـ مانه و سلمقان'
        elif city_code == '941':
            code = 'بجنورد'
        elif city_code == '9441':
            code = 'جاجرم'
        elif city_code == '94311':
            code = 'درق'
        elif city_code == '94561':
            code = 'راز'
        elif city_code == '94471':
            code = 'شوقان'
        elif city_code == '9461':
            code = 'شيروان'
        elif city_code == '9481':
            code = 'فاروج'
        elif city_code == '9431':
            code = 'گرمه'

    elif state_code == '30':
        if city_code == '97831':
            code = 'ارسك'
        elif city_code == '97441':
            code = 'اسديه ـ درميان'
        elif city_code == '97631':
            code = 'آرين شهر'
        elif city_code == '97791':
            code = 'آيسك'
        elif city_code == '9781':
            code = 'بشرويه'
        elif city_code == '971':
            code = 'بیرجند'
        elif city_code == '97671':
            code = 'حاجي آباد'
        elif city_code == '97661':
            code = 'خضري دشت بياض'
        elif city_code == '97351':
            code = 'خوسف'
        elif city_code == '97691':
            code = 'زهان'
        elif city_code == '9741':
            code = 'سر بیشه'
        elif city_code == '97771':
            code = 'سرايان'
        elif city_code == '97891':
            code = 'سه قلعه'
        elif city_code == '9771':
            code = 'فردوس'
        elif city_code == '9761':
            code = 'قائن ـ قائنات'
        elif city_code == '97461':
            code = 'گزيک'
        elif city_code == '97311':
            code = 'مود'
        elif city_code == '9751':
            code = 'نهبندان'
        elif city_code == '97443':
            code = 'نیمبلوك'

    elif state_code == '31':
        if city_code == '31871':
            code = 'اشتهارد'
        elif city_code == '31551':
            code = 'آسارا'
        elif city_code == '33661':
            code = 'چهارباغ'
        elif city_code == '33611':
            code = 'سيف آباد'
        elif city_code == '33618':
            code = 'شهر جديد هشتگرد'
        elif city_code == '33691':
            code = 'طالقان'
        elif city_code == '31':
            code = 'كرج'
        elif city_code == '31991':
            code = 'كمال شهر'
        elif city_code == '33651':
            code = 'كوهسار ـ چندار'
        elif city_code == '31638':
            code = 'گرمدره'
        elif city_code == '31849':
            code = 'ماهدشت'
        elif city_code == '31778':
            code = 'محمدشهر'
        elif city_code == '31776':
            code = 'مشکين دشت'
        elif city_code == '3331':
            code = 'نظرآباد'
        elif city_code == '3361':
            code = 'هشتگرد ـ ساوجبلاغ'

    return code
