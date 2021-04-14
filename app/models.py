import django
from django.contrib.auth.models import User
from django.db import models


class Location(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    state = models.CharField(max_length=256, null=False)
    city = models.CharField(max_length=256, null=False)
    address = models.TextField(null=False)
    postal_code = models.CharField(max_length=256, null=False, default='')


class User_img(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='app/', null=True, blank=True)


class Good(models.Model):
    name = models.CharField(max_length=100, null=False)
    price = models.IntegerField(null=False, default=0)
    real_price = models.IntegerField(null=False, default=0)
    num = models.IntegerField(null=False)
    discount = models.IntegerField(default=0)
    release_date = models.DateTimeField(default=django.utils.timezone.now)
    score = models.FloatField(default=0)
    score_num = models.IntegerField(default=0)
    category_status = (
        ('Electronic', 'Electronic'), ('Clothes', 'Clothes'), ('HomeAppliances', 'HomeAppliances'), ('Sport', 'Sport'),
        ('Stationery', 'Stationery'))
    category = models.CharField(max_length=20, default='Electronic', choices=category_status)

    def __str__(self):
        return self.name


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE, null=True)
    number = models.IntegerField(null=False, default=1)
    id = models.AutoField(primary_key=True)


class Interesting(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    good = models.ForeignKey(Good, on_delete=models.CASCADE, null=True)
    id = models.AutoField(primary_key=True)


class Image(models.Model):
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    img_src = models.CharField(max_length=200, default='app/goods_image')


class Comment(models.Model):
    good = models.ForeignKey(Good, on_delete=models.CASCADE)
    text = models.TextField(max_length=400)
    name = models.CharField(max_length=30)
    date = models.DateTimeField(default=django.utils.timezone.now)


class Electronic(models.Model):
    good = models.OneToOneField(Good, on_delete=models.CASCADE)
    brand_status = (('Huawei', 'Huawei'), ('ASUS', 'ASUS'), ('Samsung', 'Samsung'), ('Apple', 'Apple'))
    brand = models.CharField(max_length=20, default='Huawei', choices=brand_status)
    weight = models.FloatField(null=False)
    category_elec_status = (('LapTop', 'LapTop'), ('Mobile', 'Mobile'), ('Headset', 'Headset'), ('Charger', 'Charger'))
    category_elec = models.CharField(max_length=20, default='LapTop', choices=category_elec_status)

    def __str__(self):
        return self.good.name


class Clothes(models.Model):
    good = models.OneToOneField(Good, on_delete=models.CASCADE)
    type = models.CharField(max_length=100)
    gender_status = (('female', 'Female'), ('male', 'Male'))
    gender = models.CharField(max_length=20, default='female', choices=gender_status)
    category_clothes_status = (
        ('Shirt', 'Shirt'), ('Tshirt', 'Tshirt'), ('Pants', 'Pants'), ('Manto', 'Manto'), ('Blouse', 'Blouse'))
    category_clothes = models.CharField(max_length=20, default='Shirt', choices=category_clothes_status)
    size_status = (('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'))
    size_this = models.CharField(max_length=10, default='L', choices=size_status)

    def __str__(self):
        return self.good.name


class HomeAppliances(models.Model):
    good = models.OneToOneField(Good, on_delete=models.CASCADE)
    category_happ_status = (
        ('Refrigerator', 'Refrigerator'), ('TV', 'TV'), ('Washing_machine', 'Washing_machine'), ('Sofa', 'Sofa'))
    category_happ = models.CharField(max_length=20, default='Refrigerator', choices=category_happ_status)

    def __str__(self):
        return self.good.name


class Sport(models.Model):
    good = models.OneToOneField(Good, on_delete=models.CASCADE)
    category_sport_status = (('Bicycle', 'Bicycle'), ('Treadmill', 'Treadmill'), ('Ball', 'Ball'))
    category_sport = models.CharField(max_length=20, default='Bicycle', choices=category_sport_status)

    def __str__(self):
        return self.good.name


class Stationery(models.Model):
    good = models.OneToOneField(Good, on_delete=models.CASCADE)
    category_st_status = (('NoteBook', 'NoteBook'), ('Pen', 'Pen'), ('Crayons', 'Crayons'), ('Eraser', 'Eraser'))
    category_st = models.CharField(max_length=20, default='NoteBook', choices=category_st_status)

    def __str__(self):
        return self.good.name


class LapTop(models.Model):
    electronic = models.OneToOneField(Electronic, on_delete=models.CASCADE)
    storage = models.IntegerField(null=False, default=0)
    ram = models.IntegerField(null=False, default=0)
    color_status = (('blue', 'blue'), ('black', 'black'), ('gray', 'gray'), ('brown', 'brown'), ('navy', 'navy'))
    color_this = models.CharField(max_length=20, default='blue', choices=color_status)
    color_choose = models.CharField(max_length=20,null=True)


class Mobile(models.Model):
    electronic = models.OneToOneField(Electronic, on_delete=models.CASCADE)
    memory = models.IntegerField(null=False, default=0)
    ram = models.IntegerField(null=False, default=0)
    color_status = (('blue', 'blue'), ('black', 'black'), ('gray', 'gray'), ('brown', 'brown'), ('navy', 'navy'))
    color_this = models.CharField(max_length=20, default='blue', choices=color_status)
    color_choose = models.CharField(max_length=20,null=True)


class Headset(models.Model):
    electronic = models.OneToOneField(Electronic, on_delete=models.CASCADE)
    connectionType_status = (('wire', 'Wire'), ('wireless', 'Wireless'))
    connectionType = models.CharField(max_length=20, default='wire', choices=connectionType_status)
    led_indicator = models.BooleanField()


class Charger(models.Model):
    electronic = models.OneToOneField(Electronic, on_delete=models.CASCADE)
    usb_num = models.IntegerField(null=False, default=1)
    cable_type_status = (('C', 'C Type'), ('Micro', 'Micro Type'))
    cable_type = models.CharField(max_length=20, default='C', choices=cable_type_status)


class Shirt(models.Model):
    clothes = models.OneToOneField(Clothes, on_delete=models.CASCADE)
    sleeve_height_status = (('Short', 'Short'), ('Long', 'Long'))
    sleeve_height = models.CharField(max_length=20, default='Short', choices=sleeve_height_status)
    size_this = models.CharField(max_length=20,null=True)


class Tshirt(models.Model):
    clothes = models.OneToOneField(Clothes, on_delete=models.CASCADE)
    collar = models.CharField(max_length=20, null=False)
    size_this = models.CharField(max_length=20, null=True)


class Pants(models.Model):
    clothes = models.OneToOneField(Clothes, on_delete=models.CASCADE)
    model = models.CharField(max_length=20, null=False)


class Manto(models.Model):
    clothes = models.OneToOneField(Clothes, on_delete=models.CASCADE)
    how_close = models.CharField(max_length=30, null=False)
    belt = models.CharField(max_length=20, null=False)


class Blouse(models.Model):
    clothes = models.OneToOneField(Clothes, on_delete=models.CASCADE)
    collar = models.CharField(max_length=20, null=False)


class Refrigerator(models.Model):
    homeAppliances = models.OneToOneField(HomeAppliances, on_delete=models.CASCADE)
    height = models.IntegerField(null=False, default=0)
    deep = models.IntegerField(null=False, default=0)
    brand_status = (('Emersun', 'Emersun'), ('Snowa', 'Snowa'))
    brand = models.CharField(max_length=20, default='Emersun', choices=brand_status)


class TV(models.Model):
    homeAppliances = models.OneToOneField(HomeAppliances, on_delete=models.CASCADE)
    size = models.IntegerField(null=False, default=0)
    bluetooth = models.BooleanField()
    brand_status = (('LG', 'LG'), ('Samsung', 'Samsung'))
    brand = models.CharField(max_length=20, default='LG', choices=brand_status)


class Washing_machine(models.Model):
    homeAppliances = models.OneToOneField(HomeAppliances, on_delete=models.CASCADE)
    height = models.IntegerField(null=False, default=0)
    capacity = models.IntegerField(null=False, default=0)
    brand_status = (('Bosch', 'Bosch'), ('Gplus', 'Gplus'))
    brand = models.CharField(max_length=20, default='Bosch', choices=brand_status)


class Sofa(models.Model):
    homeAppliances = models.OneToOneField(HomeAppliances, on_delete=models.CASCADE)
    bodyMaterial = models.CharField(max_length=20, null=False)
    coverMaterial = models.CharField(max_length=20, null=False)


class Bicycle(models.Model):
    sport = models.OneToOneField(Sport, on_delete=models.CASCADE)
    weight = models.IntegerField(null=False, default=0)
    size = models.IntegerField(null=False, default=0)


class Treadmill(models.Model):
    sport = models.OneToOneField(Sport, on_delete=models.CASCADE)
    self_weight = models.IntegerField(null=False, default=0)
    max_weight = models.IntegerField(null=False, default=0)


class Ball(models.Model):
    sport = models.OneToOneField(Sport, on_delete=models.CASCADE)
    size = models.IntegerField(null=False)
    weight = models.IntegerField(null=False)


class NoteBook(models.Model):
    stationery = models.OneToOneField(Stationery, on_delete=models.CASCADE)
    num_pages = models.IntegerField(null=False)


class Pen(models.Model):
    stationery = models.OneToOneField(Stationery, on_delete=models.CASCADE)
    color_status = (('blue', 'blue'), ('black', 'black'), ('red', 'red'))
    color = models.CharField(max_length=20, default='blue', choices=color_status)


class Crayons(models.Model):
    stationery = models.OneToOneField(Stationery, on_delete=models.CASCADE)
    num = models.IntegerField(null=False)


class Eraser(models.Model):
    stationery = models.OneToOneField(Stationery, on_delete=models.CASCADE)
    weight = models.IntegerField(null=False)


class Color(models.Model):
    electronic = models.ForeignKey(Electronic, on_delete=models.CASCADE)
    color_status = (
        ('not choice', 'not choice'), ('blue', 'blue'), ('black', 'black'), ('gray', 'gray'), ('brown', 'brown'),
        ('navy', 'navy'))
    color = models.CharField(max_length=20, default='not choice', choices=color_status)


class Size(models.Model):
    clothes = models.ForeignKey(Clothes, on_delete=models.CASCADE)
    size_status = (('no_size', 'no_size'), ('L', 'L'), ('XL', 'XL'), ('XXL', 'XXL'))
    size = models.CharField(max_length=10, default='no_size', choices=size_status)


class Discount_code(models.Model):
    code = models.CharField(max_length=40, default='')
