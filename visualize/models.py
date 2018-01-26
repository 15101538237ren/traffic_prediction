# -*- coding: utf-8 -*-
# from django.db import models
#
# # Create your models here.
# class Violations_Array(models.Model):
#     DAWN = 0
#     MORNING_RUSH = 1
#     MORNING_WORKING = 2
#     NOON = 3
#     AFTERNOON_WORK = 4
#     AFTERNOON_RUSH = 5
#     NIGHT = 6
#
#     TIME_SEG_TYPE = (
#         (DAWN, "午夜"),
#         (MORNING_RUSH,"早高峰"),
#         (MORNING_WORKING,"早工作"),
#         (NOON,"中午休息"),
#         (AFTERNOON_WORK,"下午工作"),
#         (AFTERNOON_RUSH,"下午高峰"),
#         (NIGHT,"晚间"),
#
#     )
#
#     time_interval = models.IntegerField('时间间隔/min')
#     spatial_interval = models.IntegerField('空间间隔/m')
#     create_time = models.DateTimeField('时间区间')
#     content = models.TextField('事故内容')
#
#     highest_temperature = models.IntegerField('最高气温')
#     lowest_temperature = models.IntegerField('最低气温')
#     wind = models.DecimalField('风力',max_digits=5, decimal_places=2)
#     weather_severity = models.DecimalField('天气严重性', max_digits = 5, decimal_places = 3)
#
#     aqi = models.IntegerField('空气质量指数AQI')
#     pm25 = models.IntegerField('PM2.5')
#
#     is_holiday = models.BooleanField('是否节假日')
#     is_weekend = models.BooleanField('是否周末')
#     time_segment = models.SmallIntegerField('时间段', choices= TIME_SEG_TYPE)

# class Accidents_Array(models.Model):
#     DAWN = 0
#     MORNING_RUSH = 1
#     MORNING_WORKING = 2
#     NOON = 3
#     AFTERNOON_WORK = 4
#     AFTERNOON_RUSH = 5
#     NIGHT = 6
#
#     TIME_SEG_TYPE = (
#         (DAWN, "午夜"),
#         (MORNING_RUSH,"早高峰"),
#         (MORNING_WORKING,"早工作"),
#         (NOON,"中午休息"),
#         (AFTERNOON_WORK,"下午工作"),
#         (AFTERNOON_RUSH,"下午高峰"),
#         (NIGHT,"晚间"),
#
#     )
#
#     time_interval = models.IntegerField('时间间隔/min')
#     spatial_interval = models.IntegerField('空间间隔/m')
#     create_time = models.DateTimeField('时间区间')
#     content = models.TextField('事故内容')
#
#     highest_temperature = models.IntegerField('最高气温')
#     lowest_temperature = models.IntegerField('最低气温')
#     wind = models.DecimalField('风力',max_digits=5, decimal_places=2)
#     weather_severity = models.DecimalField('天气严重性', max_digits = 5, decimal_places = 3)
#
#     aqi = models.IntegerField('空气质量指数AQI')
#     pm25 = models.IntegerField('PM2.5')
#
#     is_holiday = models.BooleanField('是否节假日')
#     is_weekend = models.BooleanField('是否周末')
#     time_segment = models.SmallIntegerField('时间段', choices= TIME_SEG_TYPE)