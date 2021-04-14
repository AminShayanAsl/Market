from django.contrib import admin

from . import models


class ImageInline(admin.TabularInline):
    model = models.Image
    extra = 1


class LapTopInline(admin.TabularInline):
    model = models.LapTop


class MobileInline(admin.TabularInline):
    model = models.Mobile


class HeadsetInline(admin.TabularInline):
    model = models.Headset


class ChargerInline(admin.TabularInline):
    model = models.Charger


class ShirtInline(admin.TabularInline):
    model = models.Shirt


class TshirtInline(admin.TabularInline):
    model = models.Tshirt


class PantsInline(admin.TabularInline):
    model = models.Pants


class MantoInline(admin.TabularInline):
    model = models.Manto


class BlouseInline(admin.TabularInline):
    model = models.Blouse


class RefrigeratorInline(admin.TabularInline):
    model = models.Refrigerator


class TVInline(admin.TabularInline):
    model = models.TV


class Washing_machineInline(admin.TabularInline):
    model = models.Washing_machine


class SofaInline(admin.TabularInline):
    model = models.Sofa


class BicycleInline(admin.TabularInline):
    model = models.Bicycle


class TreadmillInline(admin.TabularInline):
    model = models.Treadmill


class BallInline(admin.TabularInline):
    model = models.Ball


class NoteBookInline(admin.TabularInline):
    model = models.NoteBook


class PenInline(admin.TabularInline):
    model = models.Pen


class CrayonsInline(admin.TabularInline):
    model = models.Crayons


class EraserInline(admin.TabularInline):
    model = models.Eraser


class ColorInline(admin.TabularInline):
    model = models.Color
    extra = 1


class SizeInline(admin.TabularInline):
    model = models.Size
    extra = 1


@admin.register(models.Good)
class GoodAdmin(admin.ModelAdmin):
    inlines = [ImageInline]


@admin.register(models.Electronic)
class ElectronicAdmin(admin.ModelAdmin):
    inlines = [ColorInline, LapTopInline, MobileInline, HeadsetInline, ChargerInline]


@admin.register(models.Clothes)
class ClothesAdmin(admin.ModelAdmin):
    inlines = [SizeInline, ShirtInline, TshirtInline, PantsInline, MantoInline, BlouseInline]


@admin.register(models.HomeAppliances)
class HomeAppliancesAdmin(admin.ModelAdmin):
    inlines = [RefrigeratorInline, TVInline, Washing_machineInline, SofaInline]


@admin.register(models.Sport)
class SportAdmin(admin.ModelAdmin):
    inlines = [BicycleInline, TreadmillInline, BallInline]


@admin.register(models.Stationery)
class StationeryAdmin(admin.ModelAdmin):
    inlines = [NoteBookInline, PenInline, CrayonsInline, EraserInline]


@admin.register(models.Discount_code)
class Discount_codeAdmin(admin.ModelAdmin):
    pass


@admin.register(models.Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
