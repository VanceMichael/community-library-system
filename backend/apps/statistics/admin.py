from django.contrib import admin


class StatisticsAdmin(admin.AdminSite):
    site_header = '借阅统计管理'
    site_title = '借阅统计'

statistics_admin = StatisticsAdmin(name='statistics_admin')
