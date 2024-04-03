import json
import os
import dotenv
from django.db import connection
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from dotenv import load_dotenv
load_dotenv()


# Create your views here.


def server_start(request):
    return HttpResponse("Server started successfully. \n Make sure to double"
                        "check environment variables for allowed hosts.")


def admin_reports(request):
    cursor = connection.cursor()
    cursor.execute('''
        SELECT 
            c.listid as Listing_id, c.image, c.make as Make, c.model as Model, 
            u.username as Seller, u.user_id as SellerId, 
            with_listid.description, with_listid.Reporter, with_listid.Reporter_id
        FROM
            CarListing c
            INNER JOIN (
                SELECT 
                    r.listing_id as Lister, r.description, 
                    u.username as Reporter, r.reporter_id as Reporter_id
                FROM 
                    biddingwheels.ListingReport r
                    INNER JOIN User u ON u.user_id = r.reporter_id
            ) as with_listid ON c.listid = with_listid.Lister
            INNER JOIN User u ON u.user_id = c.sellerid
    ''')
    rows = cursor.fetchall()

    if rows:
        data = [
            {
                'ListId': row[0],
                'Image': row[1],
                'Make': row[2],
                'Model': row[3],
                'Seller': row[4],
                'SellerId': row[5],
                'Description': row[6],
                'Reporter': row[7],
                'ReporterId': row[8]
            }
            for row in rows
        ]
        return JsonResponse(data, safe=False)
    else:
        return HttpResponse(status=404)


def website_stats(request):
    class Stats:
        def __init__(self, dates, sales):
            self.dates = dates
            self.sales = sales

        def serialize(self):
            return{
                "dates": self.dates,
                "sales": self.sales,
            }

    stat = Stats(["Mar-01", "Mar-02", "Mar-03", "Mar-04", "Mar-05"],
                 [34, 60, 23, 55, 69])
    stat_json = json.dumps(stat.serialize())
    if stat_json:
        return HttpResponse(stat_json)
    else:
        return HttpResponse(status=404)


def detail_page(request, listid):
    cursor = connection.cursor()
    try:
        cursor.execute('''
            SELECT 
                cl.listid, cl.licenseNumber, cl.engineSerialNumber, cl.make, cl.model, 
                cl.year, cl.mileage, cl.city, cl.color, cl.additionalFeatures, 
                cl.description, cl.startingPrice, cl.biddingDeadline, cl.highestBid, 
                cl.highestBidHolder, u.username, cl.image
            FROM 
                CarListing cl
                JOIN User u ON cl.sellerID = u.user_id
            WHERE 
                cl.listid = %s
        ''', [listid])

        row = cursor.fetchone()

        if row:
            car_data = {
                'listid': row[0],
                'licenseNumber': row[1],
                'engineSerialNumber': row[2],
                'make': row[3],
                'model': row[4],
                'year': row[5],
                'mileage': row[6],
                'city': row[7],
                'color': row[8],
                'additionalFeatures': row[9],
                'description': row[10],
                'startingPrice': row[11],
                'biddingDeadline': row[12],
                'highestBid': row[13],
                'highestBidHolder': row[14],
                'sellerUsername': row[15],
                'image': row[16]
            }

            return JsonResponse(car_data)
        else:
            return HttpResponse(status=404)
    finally:
        cursor.close()
