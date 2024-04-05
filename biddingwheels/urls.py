"""
URL configuration for biddingwheels project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from biddingwheels_app import views


urlpatterns = [
    path('', views.server_start),
    path('reported-items', views.admin_reports),
    path('website-stats', views.website_stats),
    path('car-details/<int:listid>/', views.detail_page),
    path('post-report', views.post_report),
    path('signup', views.signup),
    path('login', views.login),
    path('check_session', views.check_session),
    path('profile', views.profile),
    path('submit-bid', views.submit_bid),
    path('all-listings', views.all_listings),
    path('payment', views.payment),
    path('transactions', views.fetch_transactions),
    path('post-listing', views.post_listing),
    path('create-transaction-table', views.create_transaction_table),
    path('check-table-desp/<tablename>', views.check_table),
    path('fetch-table-data/<tablename>', views.fecth_table_data),
    path('add-fake-data', views.add_fake_data),
]
