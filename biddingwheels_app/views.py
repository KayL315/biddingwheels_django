import datetime
import json
import os
import dotenv
from pymysql import DatabaseError, IntegrityError
from .models import User
from .models import Message
from django.db import connection
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.shortcuts import render, HttpResponse, redirect
from dotenv import load_dotenv
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password
from datetime import datetime
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.shortcuts import get_object_or_404
import logging
from datetime import datetime
from django.utils import timezone


logging.basicConfig(level=logging.DEBUG)  


logger = logging.getLogger(__name__)

load_dotenv()
# Create your views here.


def server_start(request):
    return HttpResponse(
        "Server started successfully. \n Make sure to double"
        "check environment variables for allowed hosts."
    )


def admin_reports(request):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """
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
                        INNER JOIN user u ON u.user_id = r.reporter_id
                ) as with_listid ON c.listid = with_listid.Lister
                INNER JOIN user u ON u.user_id = c.sellerid
        """
        )
        rows = cursor.fetchall()

        data = [
            {
                "ListId": row[0],
                "Image": row[1],
                "Make": row[2],
                "Model": row[3],
                "Seller": row[4],
                "SellerId": row[5],
                "Description": row[6],
                "Reporter": row[7],
                "ReporterId": row[8],
            }
            for row in rows
        ]
        return JsonResponse(data, safe=False)

    except Exception as e:
        return HttpResponse(str(e), status=404)


def all_listings(request):
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT 
            cl.listid, cl.licenseNumber, cl.engineSerialNumber, cl.make, cl.model, 
            cl.year, cl.mileage, cl.city, cl.color, cl.additionalFeatures, 
            cl.description, cl.startingPrice, cl.biddingDeadline, cl.highestBid, 
            cl.highestBidHolder, cl.image
        FROM 
            CarListing cl
        WHERE
            cl.biddingDeadline > NOW()
    """
    )

    rows = cursor.fetchall()

    data = [
        {
            "listid": row[0],
            "licenseNumber": row[1],
            "engineSerialNumber": row[2],
            "make": row[3],
            "model": row[4],
            "year": row[5],
            "mileage": row[6],
            "city": row[7],
            "color": row[8],
            "additionalFeatures": row[9],
            "description": row[10],
            "startingPrice": row[11],
            "biddingDeadline": row[12],
            "highestBid": row[13],
            "highestBidHolder": row[14],
            "image": row[15],
        }
        for row in rows
    ]

    return JsonResponse(data, safe=False)


def website_stats(request):
    try:
        cursor = connection.cursor()
        cursor.execute(
            """SELECT 
            COUNT(*) as Total_Sales, 
             date
        FROM Transactions
        GROUP BY 
            date;"""
        )
        rows = cursor.fetchall()
        cursor.execute(
            """
            SELECT COUNT(model)as model_sales, model
            FROM
            (SELECT 
                COUNT(*) as Total_Sales, 
                model, date
            FROM (
                SELECT * 
                FROM Transactions t
                INNER JOIN CarListing c ON t.list_id = c.listid
            ) as joint
            GROUP BY 
                date, 
                model) as sub
                GROUP BY model
            ORDER BY model_sales DESC;
        """
        )
        rows2 = cursor.fetchall()
        sales = [{"Total_Sales": row[0], "Date": row[1]} for row in rows]
        model_sales = [{"Sold": row[0], "Model": row[1]} for row in rows2]
        data = {"sales": sales, "model_sales": model_sales}
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse(str(e), status=404)


def detail_page(request, listid):
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            SELECT 
                cl.listid, cl.licenseNumber, cl.engineSerialNumber, cl.make, cl.model, 
                cl.year, cl.mileage, cl.city, cl.color, cl.additionalFeatures, 
                cl.description, cl.startingPrice, cl.biddingDeadline, cl.highestBid, 
                cl.highestBidHolder, u.username, u.user_id as seller, b.username AS highestBidHolderUsername, 
                b.user_id as highestBidHolder, cl.image
            FROM 
                CarListing cl
                JOIN user u ON cl.sellerID = u.user_id
                LEFT JOIN user b ON cl.highestBidHolder = b.user_id
            WHERE 
                cl.listid = %s
        """,
            [listid],
        )

        row = cursor.fetchone()

        if row:
            car_data = {
                "listid": row[0],
                "licenseNumber": row[1],
                "engineSerialNumber": row[2],
                "make": row[3],
                "model": row[4],
                "year": row[5],
                "mileage": row[6],
                "city": row[7],
                "color": row[8],
                "additionalFeatures": row[9],
                "description": row[10],
                "startingPrice": row[11],
                "biddingDeadline": row[12],
                "highestBid": row[13],
                "highestBidHolder": row[14],
                "sellerUsername": row[15],
                "seller": row[16],
                "highestBidHolderUsername": (
                    row[17] if row[17] else "No highest bid holder"
                ),
                "highestBidHolder": row[18],
                "image": row[19],
            }

            return JsonResponse(car_data)
        else:
            return HttpResponse(status=404)
    finally:
        cursor.close()


@csrf_exempt
def fetch_payment_info(request):
    if request.method == "POST":
        # get user_id from request body
        data = json.loads(request.body)
        user_id = data.get("user_id")
    if request.method == "POST":
        # get user_id from request body
        data = json.loads(request.body)
        user_id = data.get("user_id")

        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT p.payment_id, p.cardName, p.cardNumber, p.expMonth, p.expYear, p.cvv from Payment p WHERE p.user_id = {user_id}
        """
        )
        rows = cursor.fetchall()
        cardInfo = [
            {
                "payment_id": row[0],
                "cardName": row[1],
                "cardNumber": row[2],
                "expMonth": row[3],
                "expYear": row[4],
                "cvv": row[5],
            }
            for row in rows
        ]
        cursor = connection.cursor()
        cursor.execute(
            f"""
            SELECT p.payment_id, p.cardName, p.cardNumber, p.expMonth, p.expYear, p.cvv from Payment p WHERE p.user_id = {user_id}
        """
        )
        rows = cursor.fetchall()
        cardInfo = [
            {
                "payment_id": row[0],
                "cardName": row[1],
                "cardNumber": row[2],
                "expMonth": row[3],
                "expYear": row[4],
                "cvv": row[5],
            }
            for row in rows
        ]

        cursor.execute(
            f"""
            SELECT a.address_id, a.fullName, a.address, a.city, a.state, a.zip, a.email from Address a WHERE a.user_id = {user_id}
        """
        )
        rows = cursor.fetchall()
        addressInfo = [
            {
                "address_id": row[0],
                "fullName": row[1],
                "address": row[2],
                "city": row[3],
                "state": row[4],
                "zip": row[5],
                "email": row[6],
            }
            for row in rows
        ]
        cursor.execute(
            f"""
            SELECT a.address_id, a.fullName, a.address, a.city, a.state, a.zip, a.email from Address a WHERE a.user_id = {user_id}
        """
        )
        rows = cursor.fetchall()
        addressInfo = [
            {
                "address_id": row[0],
                "fullName": row[1],
                "address": row[2],
                "city": row[3],
                "state": row[4],
                "zip": row[5],
                "email": row[6],
            }
            for row in rows
        ]

        return JsonResponse({"cardInfo": cardInfo, "addressInfo": addressInfo})
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def post_listing(request):
    if request.method == "POST":
        if not request.session.get("user_id"):
            return JsonResponse(
                {"success": False, "message": "User not logged in"}, status=401
            )
        try:
            data = json.loads(request.body)
            print(request.session.get("user_id"))

            values = (
                request.session.get("user_id"),
                data.get("licenseNumber", ""),
                data.get("engineSerialNumber", ""),
                data.get("make", ""),
                data.get("model", ""),
                data.get("year", 2024),
                data.get("mileage", 0),
                data.get("city", ""),
                data.get("color", ""),
                data.get("additionalFeatures", ""),
                data.get("description", ""),
                data.get("startingPrice", 0),
                data.get("biddingDeadline", ""),
                data.get("highestBid"),
                request.session.get("user_id"),
                data.get("image", ""),
            )
            print(values)

            # Execute the SQL query.
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO CarListing
                    (sellerID, licenseNumber, engineSerialNumber, make, model, year, mileage, city, color, additionalFeatures, description, startingPrice, biddingDeadline, highestBid, highestBidHolder, image)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, STR_TO_DATE(%s, '%%Y-%%m-%%dT%%H:%%i:%%sZ'), %s, %s, %s)
                """,
                    values,
                )

            return JsonResponse(
                {"status": "success", "message": "Listing created successfully"}
            )

        except Exception as e:
            # Handle other exceptions
            return JsonResponse(
                {"status": "error", "message": "An error occurred: " + str(e)}
            )
    else:
        # If the method is not POST, return an error
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )


@csrf_exempt
def submit_bid(request):
    if not request.method == "POST":
        return JsonResponse(
            {"success": False, "message": "Invalid request method"}, status=405
        )

    if not request.session.get("user_id"):
        return JsonResponse(
            {"success": False, "message": "User not logged in"}, status=401
        )

    try:
        data = json.loads(request.body)
        bid = float(data.get("bid"))
        listing_id = data.get("listing_id")
        user_id = data.get("user_id")  # buyer_id
        owner_id = data.get("owner_id")
        payment_id = data.get("payment_id")
        address_id = data.get("address_id")

        with connection.cursor() as cursor:
            # Fetch the current highest bid
            cursor.execute(
                "SELECT highestBid FROM CarListing WHERE listid = {listing_id}"
            )
            row = cursor.fetchone()
            if row:
                # add this record to the Transactions table
                # check if the user had bid before
                cursor.execute(
                    f"SELECT * FROM Transactions WHERE buyer_id = {user_id} AND list_id = {listing_id}"
                )
                bidhistory = cursor.fetchone()
                if bidhistory:
                    # update the bid amount and date
                    cursor.execute(
                        "UPDATE Transactions SET amount = %s, date = %s WHERE buyer_id = %s AND list_id = %s",
                        [bid, datetime.now(), user_id, listing_id],
                    )
                else:
                    query = """ INSERT INTO Transactions (owner_id, buyer_id, list_id, amount, date, payment_id, address_id, done) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
                    params = (
                        owner_id,
                        user_id,
                        listing_id,
                        bid,
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        payment_id,
                        address_id,
                        0,
                    )
                    cursor.execute(query, params)

                current_highest_bid = row[0]
                if bid > current_highest_bid:
                    # Update the bid
                    cursor.execute(
                        "UPDATE CarListing SET highestBid = %s, highestBidHolder = %s WHERE listid = %s",
                        [bid, user_id, listing_id],
                    )
                    # Fetch the username of the highest bid holder
                    cursor.execute(
                        "SELECT username FROM user WHERE user_id = %s", [user_id]
                    )
                    user_row = cursor.fetchone()
                    if user_row:
                        highest_bid_holder_username = user_row[0]
                        return JsonResponse(
                            {
                                "success": True,
                                "message": "Bid placed successfully",
                                "highestBidHolderUsername": highest_bid_holder_username,  # include the username in the response
                            }
                        )
                    else:
                        return JsonResponse(
                            {"success": False, "message": "User not found"}, status=404
                        )
            else:
                return JsonResponse(
                    {"success": False, "message": "Car listing not found"}, status=404
                )

    except KeyError:
        return JsonResponse(
            {"success": False, "message": "Missing required data"}, status=400
        )
    except ValueError:
        return JsonResponse(
            {"success": False, "message": "Invalid bid value"}, status=400
        )
    except Exception as e:
        return JsonResponse(
            {"success": False, "message": f"An unexpected error occurred: {e}"},
            status=500,
        )


@csrf_exempt
def post_report(request):
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid request method")
    if request.method == "POST":
        if not request.session.get("user_id"):
            return JsonResponse({"error": "User not logged in"}, status=401)

        try:
            data = json.loads(request.body)
            reporter_id = request.session.get("user_id")
            description = data["description"]
            listing_id = int(data["listing_id"])
            submit_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # submit_time = datetime.now()

            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO ListingReport (reporter_id, submit_time, description, listing_id) 
                    VALUES (%s, %s, %s, %s)
                """,
                    [reporter_id, submit_time, description, listing_id],
                )

            return JsonResponse({"message": "Report submitted successfully"})

        except KeyError as e:
            return HttpResponseBadRequest(f"Missing field: {e}")
        except ValueError as e:
            # This will catch issues like conversion errors
            return HttpResponseBadRequest(f"Invalid data: {e}")
        except DatabaseError as e:
            # Specific handling for database errors
            return HttpResponseBadRequest(f"Database error: {e}")
        except Exception as e:
            # Catch-all for any other exceptions
            return HttpResponseBadRequest(f"An unexpected error occurred: {e}")


# signup logic
@csrf_exempt  #allow cross origin requests
def signup(request):
    if request.method == "POST":
        # get username and password from request body
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        # check if the username already exists
        if User.objects.filter(username=username).exists():
            return JsonResponse({"error": "Username already exists"}, status=400)
        # create a new user
        user = User.objects.create(username=username, password=password, role="normal")

        # signup successful
        response = JsonResponse({"message": "User created successfully"})
        response["Access-Control-Allow-Origin"] = (
            "http://localhost:3000"  
        )
        response["Access-Control-Allow-Credentials"] = True  # alllow cookies
    else:
        response = JsonResponse({"error": "Invalid request method"}, status=405)

    return response


# login
@csrf_exempt
def login(request):
    logger.debug("Login request received") 

    if request.method == "OPTIONS":
        logger.debug("Handling preflight request")  
        response = JsonResponse({"message": "Preflight request handled successfully"})
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Credentials"] = True
        response["Access-Control-Allow-Headers"] = "Content-Type"
        response["Access-Control-Allow-Methods"] = "POST"
        return response

    elif request.method == "POST":
        logger.debug("Handling POST request") 
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            logger.error("User does not exist") 
            response = JsonResponse({"error": "Username does not exist"}, status=404)
            response["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response["Access-Control-Allow-Credentials"] = True
            return response

        print("输入的密码:", password)
        print("数据库中存储的密码:", user.password)

        # check if the password is correct
        if password != user.password:
            logger.error("Invalid password") 
            response = JsonResponse({"error": "Invalid password"}, status=401)
            response["Access-Control-Allow-Origin"] = "http://localhost:3000"
            response["Access-Control-Allow-Credentials"] = True
            return response

        # create a session to store user information
        request.session["user_id"] = user.user_id
        request.session["user_role"] = user.role
        print(request.session["user_role"])
        print(request.session["user_id"])
        response = JsonResponse(
            {
                "message": "Login successful",
                "user_id": user.user_id,
                "user_role": user.role,
            }
        )
        response["Access-Control-Allow-Origin"] = "http://localhost:3000"
        response["Access-Control-Allow-Credentials"] = True
        return response

    else:
        logger.error("Invalid request method")  
        response = JsonResponse({"error": "Invalid request method"}, status=405)
        return response


# check if the user is logged in
@csrf_exempt
def check_session(request):
    if "user_id" in request.session and "user_role" in request.session:
        # get user_id and user_role from session
        user_id = request.session["user_id"]
        user_role = request.session["user_role"]
        print(request.session["user_role"])
        # return JsonResponse({'user_id': user_id, 'user_role': user_role})
        try:
            user = User.objects.get(pk=user_id)
            # return user data
            user_data = {
                "user_id": user.user_id,
                "username": user.username,
                "avatar": user.avatar,
                "address": user.address,
                "payment_method": user.payment_method,
                "user_role": user_role,
            }
            print("User data:", user_data) 
            return JsonResponse(user_data)
        except User.DoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)
    else:
        return JsonResponse({"error": "Not logged in"}, status=401)

    

@csrf_exempt
def check_id(request):
    if "user_id" in request.session and "user_role" in request.session:
        user_id = request.session["user_id"]
        print(request.session["user_id"])
        try:
            user = User.objects.get(pk=user_id)
            user_data = {
                "user_id": user.user_id,
            }
            print("User data:", user_data)
            return JsonResponse(user_data)
        except User.DoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)
    else:
        return JsonResponse({"error": "Not logged in"}, status=401)


# card info
@csrf_exempt
def card_info(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get("user_id")
        user_id = data.get("user_id")
        cardName = data.get("cardName")
        cardNumber = data.get("cardNumber")
        expMonth = data.get("expMonth")
        expYear = data.get("expYear")
        cvv = data.get("cvv")

        # check user exists in user table
        user = User.objects.filter(user_id=user_id).first()

        if not user:
            return JsonResponse({"error": "User is not authenticated"}, status=401)

        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO Payment (user_id, cardName, cardNumber, expMonth, expYear, cvv)
            VALUES ({user_id}, '{cardName}', '{cardNumber}', '{expMonth}', '{expYear}', '{cvv}')
        """
        )

        # get the attributes  of the last inserted row
        cursor.execute(
            f"""
            SELECT payment_id, cardName, cardNumber, expMonth, expYear, cvv
            FROM Payment
            WHERE payment_id = LAST_INSERT_ID()
        """
        )
        rows = cursor.fetchall()

        data = [
            {
                "payment_id": row[0],
                "cardName": row[1],
                "cardNumber": row[2],
                "expMonth": row[3],
                "expYear": row[4],
                "cvv": row[5],
            }
            for row in rows
        ]

        return JsonResponse(
            {"message": "Payment successful", "cardInfo": data}, status=200
        )
    elif request.method == "DELETE":
        data = json.loads(request.body)
        payment_id = data.get("payment_id")

        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM Payment WHERE payment_id = {payment_id}")

        return JsonResponse({"message": "Payment delete successful"}, status=200)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


# card info
@csrf_exempt
def address_info(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_id = data.get("user_id")
        fullName = data.get("fullName")
        email = data.get("email")
        address = data.get("address")
        city = data.get("city")
        state = data.get("state")
        zip = data.get("zip")

        # check user exists in user table
        user = User.objects.filter(user_id=user_id).first()

        if not user:
            return JsonResponse({"error": "User is not authenticated"}, status=401)

        cursor = connection.cursor()
        cursor.execute(
            f"""
            INSERT INTO Address (user_id, fullName, email, address, city, state, zip)
            VALUES ({user_id}, '{fullName}', '{email}', '{address}', '{city}', '{state}', '{zip}')
        """
        )

        # get the attributes  of the last inserted row
        cursor.execute(
            f"""
            SELECT address_id, fullName, email, address, city, state, zip
            FROM Address
            WHERE address_id = LAST_INSERT_ID()
        """
        )
        rows = cursor.fetchall()

        data = [
            {
                "address_id": row[0],
                "fullName": row[1],
                "email": row[2],
                "address": row[3],
                "city": row[4],
                "state": row[5],
                "zip": row[6],
            }
            for row in rows
        ]

        return JsonResponse(
            {"message": "Payment successful", "address": data}, status=200
        )
    elif request.method == "DELETE":
        data = json.loads(request.body)
        address_id = data.get("address_id")

        with connection.cursor() as cursor:
            cursor.execute(f"DELETE FROM Address WHERE address_id = {address_id}")

        return JsonResponse({"message": "Address delete successful"}, status=200)

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


def check_table(request, tablename):
    cursor = connection.cursor()
    cursor.execute(f"DESCRIBE {tablename}")
    rows = cursor.fetchall()
    return JsonResponse(rows, safe=False)


def fecth_table_data(request, tablename):
    cursor = connection.cursor()
    cursor.execute(f"SELECT * FROM {tablename}")
    rows = cursor.fetchall()
    return JsonResponse(rows, safe=False)


def create_transaction_tables(request):
    cursor = connection.cursor()
    # # start a transaction
    # cursor.execute("START TRANSACTION")
    # cursor.execute("DROP TABLE IF EXISTS Payment")
    cursor.execute("DROP TABLE IF EXISTS Shipping")
    # cursor.execute("DROP TABLE IF EXISTS Address")
    cursor.execute("DROP TABLE IF EXISTS Transactions")

    # cursor.execute(
    #     """
    #     CREATE TABLE Payment (
    #         payment_id INT PRIMARY KEY AUTO_INCREMENT,
    #         user_id INT,
    #         cardName VARCHAR(255) NOT NULL,
    #         cardNumber VARCHAR(255) NOT NULL,
    #         expMonth VARCHAR(255) NOT NULL,
    #         expYear VARCHAR(255) NOT NULL,
    #         cvv VARCHAR(255) NOT NULL,

    #         FOREIGN KEY (user_id) REFERENCES user(user_id)
    #     )
    # """
    # )

    # cursor.execute(
    #     """
    #     CREATE TABLE Address (
    #         address_id INT PRIMARY KEY AUTO_INCREMENT,
    #         user_id INT,
    #         fullName VARCHAR(255) NOT NULL,
    #         address VARCHAR(255) NOT NULL,
    #         city VARCHAR(255) NOT NULL,
    #         state VARCHAR(255) NOT NULL,
    #         zip VARCHAR(255) NOT NULL,
    #         email VARCHAR(255) NOT NULL,

    #         FOREIGN KEY (user_id) REFERENCES user(user_id)
    #     )
    #     """
    # )

    cursor.execute(
        """
        CREATE TABLE Transactions (
            transaction_id INT PRIMARY KEY AUTO_INCREMENT,
            owner_id INT,
            buyer_id INT,
            list_id INT NOT NULL,
            amount FLOAT NOT NULL,
            date DATE NOT NULL,
            payment_id INT,
            address_id INT,
            done BOOLEAN NOT NULL DEFAULT 0,

            FOREIGN KEY (owner_id) REFERENCES user(user_id),
            FOREIGN KEY (buyer_id) REFERENCES user(user_id),
            FOREIGN KEY (list_id) REFERENCES CarListing(listid),
            FOREIGN KEY (payment_id) REFERENCES Payment(payment_id),
            FOREIGN KEY (address_id) REFERENCES Address(address_id))
    """
    )

    cursor.execute(
        """
        CREATE TABLE Shipping (
            shipping_id INT PRIMARY KEY AUTO_INCREMENT,
            user_id INT,
            transaction_id INT,
            tracking_number VARCHAR(255) NOT NULL,
            address_id INT,
            status VARCHAR(255) NOT NULL,
            date DATE NOT NULL,

            FOREIGN KEY (user_id) REFERENCES user(user_id),
            FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id),
            FOREIGN KEY (address_id) REFERENCES Address(address_id))
    """
    )
    # fecth description of all Transactions table
    cursor.execute("DESCRIBE Transactions")
    rows = cursor.fetchall()

    return JsonResponse(rows, safe=False)


# fetch all transactions
@csrf_exempt
def fetch_transactions(request):
    if request.method == "GET":
        cursor = connection.cursor()
        cursor.execute(
            """
            SELECT t.transaction_id, t.cardName, t.cardNumber, t.expMonth, t.expYear, t.cvv, t.firstName, t.address, t.city, t.state, t.zip, t.email, t.amount, t.user_id
            FROM Transaction t
        """
        )

        rows = cursor.fetchall()
        data = [
            {
                "transaction_id": row[0],
                "cardName": row[1],
                "cardNumber": row[2],
                "expMonth": row[3],
                "expYear": row[4],
                "cvv": row[5],
                "firstName": row[6],
                "address": row[7],
                "city": row[8],
                "state": row[9],
                "zip": row[10],
                "email": row[11],
                "amount": row[12],
                "user_id": row[13],
            }
            for row in rows
        ]

        return JsonResponse(data, safe=False)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


# personal profile
@csrf_exempt
def profile(request):
    if request.method == "PUT":
        if not "user_id" in request.session:
            return JsonResponse({"error": "User is not authenticated"}, status=401)

        data = json.loads(request.body)
        user_id = request.session["user_id"]

        try:
            user = User.objects.get(pk=user_id)  # find the user according to the user_id
        except User.DoesNotExist:
            return JsonResponse({"error": "User does not exist"}, status=404)

        # update the user profile
        user.username = data.get("username", user.username)
        # user.avatar = data.get("avatar", user.avatar)
        user.password = data.get("password", user.password)
        user.address = data.get("address", user.address)
        user.payment_method = data.get("payment_method", user.payment_method)
        user.save()

        return JsonResponse({"message": "Profile updated successfully"})

    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


# logout
def logout_view(request):
    logout(request)
    print("Logged out successfully")
    return JsonResponse({"message": "Logout successful"})


# user listings
@csrf_exempt
def user_listings(request):
    if request.method == "GET":
        user_id = request.session.get("user_id")  # get user_id from session
        print(user_id)
        if user_id:
            cursor = connection.cursor()
            try:
                cursor.execute(
                    """
                    SELECT 
                        cl.listid, cl.licenseNumber, cl.engineSerialNumber, cl.make, cl.model, 
                        cl.year, cl.mileage, cl.city, cl.color, cl.additionalFeatures, 
                        cl.description, cl.startingPrice, cl.biddingDeadline, cl.highestBid, 
                        cl.highestBidHolder, cl.image
                    FROM 
                        CarListing cl
                    WHERE 
                        cl.sellerID = %s
                    """,
                    [user_id],
                )

                listings = []
                rows = cursor.fetchall()
                for row in rows:
                    listing_data = {
                        "listid": row[0],
                        "licenseNumber": row[1],
                        "engineSerialNumber": row[2],
                        "make": row[3],
                        "model": row[4],
                        "year": row[5],
                        "mileage": row[6],
                        "city": row[7],
                        "color": row[8],
                        "additionalFeatures": row[9],
                        "description": row[10],
                        "startingPrice": row[11],
                        "biddingDeadline": row[12],
                        "highestBid": row[13],
                        "highestBidHolder": row[14],
                        "image": row[15],
                    }
                    listings.append(listing_data)
                    print("each listing:", listing_data)
                print("Listings:", listings)

                return JsonResponse({"status": "success", "listings": listings})
            except Exception as e:
                return JsonResponse(
                    {"status": "error", "message": "An error occurred: " + str(e)}
                )
            finally:
                cursor.close()
        else:
            return JsonResponse(
                {"status": "error", "message": "User not logged in"}, status=401
            )
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )


@csrf_exempt
def other_profile(request, username):
    print("Received username:", username)
    if request.method == "GET":
        # find the user according to the username
        cursor = connection.cursor()
        try:
            print("Fetching profile for user:", username)
            cursor.execute(
                """
                SELECT user_id
                FROM user
                WHERE username = %s
                """,
                [username],
            )
            user_row = cursor.fetchone()
            print("User row:", user_row)
            if user_row:
                user_id = user_row[0]

                cursor.execute(
                    """
                    SELECT 
                        cl.listid, cl.licenseNumber, cl.engineSerialNumber, cl.make, cl.model, 
                        cl.year, cl.mileage, cl.city, cl.color, cl.additionalFeatures, 
                        cl.description, cl.startingPrice, cl.biddingDeadline, cl.highestBid, 
                        cl.highestBidHolder, cl.image
                    FROM 
                        CarListing cl
                    WHERE 
                        cl.sellerID = %s
                    """,
                    [user_id],
                )

                listings = []
                rows = cursor.fetchall()
                for row in rows:
                    listing_data = {
                        "listid": row[0],
                        "licenseNumber": row[1],
                        "engineSerialNumber": row[2],
                        "make": row[3],
                        "model": row[4],
                        "year": row[5],
                        "mileage": row[6],
                        "city": row[7],
                        "color": row[8],
                        "additionalFeatures": row[9],
                        "description": row[10],
                        "startingPrice": row[11],
                        "biddingDeadline": row[12],
                        "highestBid": row[13],
                        "highestBidHolder": row[14],
                        "image": row[15],
                    }
                    listings.append(listing_data)

                # return JsonResponse({"status": "success", "listings": listings})
                return JsonResponse({"status": "success", "username": username, "listings": listings, "user_id": user_id})

            else:
                return JsonResponse(
                    {"status": "error", "message": "User not found"}, status=404
                )
        except Exception as e:
            print("An error occurred:", e)
            return JsonResponse(
                {"status": "error", "message": "An error occurred: " + str(e)}
            )
        finally:
            cursor.close()
    else:
        return JsonResponse(
            {"status": "error", "message": "Invalid request method"}, status=405
        )


@csrf_exempt
def send_message(request):
    data = json.loads(request.body)
    description = data.get("description")
    receiver_id = data.get("receiver_id")
    sender_id = data.get("user_id")

    print('Description:', description)
    print('Receiver ID:', receiver_id)
    print('Sender ID:', sender_id)
    timestamp = datetime.now()
    with connection.cursor() as cursor:
        cursor.execute(
            """
                    INSERT INTO Message (senderID, receiverID, description, timestamp) 
                    VALUES (%s, %s, %s, %s)
                """,
            [sender_id, receiver_id, description, timestamp],
        )

    return JsonResponse({'message': 'Message sent successfully'})


@csrf_exempt
def get_messages(request):
    if request.method == "GET":
        if "user_id" in request.session:
            user_id = request.session["user_id"]
            messages = Message.objects.filter(receiver_id=user_id)
            messages_data = []
            for message in messages:
                sender = User.objects.get(pk=message.sender_id_id)

                message_info = {
                    "description": message.description,
                    "sender_username": sender.username,
                }
                messages_data.append(message_info)
            return JsonResponse({"messages": messages_data})

        else:
            return JsonResponse({"error": "User is not logged in"}, status=401)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=405)


@csrf_exempt
def can_rate(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            owner_id = data.get("owner")
            buyer_id = data.get("buyer")
            rater = data.get("rater")
            rated = data.get("rated")

            cursor = connection.cursor()

            # Determine if a transaction exists in the DB, return 404 if not
            cursor.execute(
                f"""
                SELECT transaction_id FROM Transactions
                WHERE owner_id = {owner_id} AND buyer_id = {buyer_id};
            """
            )
            transaction_rows = cursor.fetchone()
            if transaction_rows is None:
                return HttpResponse("Transaction not found", status=404)

            cursor.execute(
                f"""
                SELECT id FROM User_ratings
                WHERE rater_id = {rater} AND rated_user_id = {rated};
            """
            )
            rating_rows = cursor.fetchone()
            if rating_rows is not None:
                return HttpResponse("Already rated", status=403)

            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(e, status=500)
    return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def add_rating(request):
    if request.method == "PUT":
        try:
            data = json.loads(request.body)
            rater = data.get("rater")
            rated = data.get("rated")
            rating = data.get("rating")

            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    INSERT INTO User_ratings(rater_id, rated_user_id, rating) 
                    VALUES({rater}, {rated}, {rating});
                """
                )
            return HttpResponse(status=200)
        except Exception as e:
            return HttpResponse(e, status=500)
    return HttpResponse("Method not allowed", status=405)


@csrf_exempt
def fetch_rating(request, user_id):
    if request.method == "GET":
        try:
            with connection.cursor() as cursor:
                cursor.execute(
                    f"""
                    SELECT rated_user_id, AVG(rating) FROM biddingwheels.
                    User_ratings GROUP BY rated_user_id 
                    HAVING rated_user_id = {user_id};
                """
                )
                rows = cursor.fetchone()

                if rows is not None:
                    rating = rows[1]
                    return HttpResponse(str(rating), status=200)
                else:
                    return HttpResponse("0", status=200)
        except Exception as e:
            return HttpResponse(e, status=500)
    else:
        return HttpResponse("Method not allowed", status=405)



def update_transactions():
    cursor = connection.cursor()
    # start SQL transaction
    cursor.execute("START TRANSACTION")
    # find all carlist that are out of date
    cursor.execute(
        """
            WITH BidList as (SELECT listid, highestBid, highestBidHolder FROM CarListing WHERE biddingDeadline < NOW() AND isSold = 0)
            UPDATE Transactions SET done = 1 WHERE list_id in (SELECT listid FROM BidList)
        """
    )

    cursor.execute(
        """
            WITH BidList as (SELECT listid, highestBid, highestBidHolder FROM CarListing WHERE biddingDeadline < NOW() AND isSold = 0)
            DELETE FROM Transactions WHERE list_id IN (SELECT listid as list_id FROM BidList) AND buyer_id NOT IN (SELECT highestBidHolder FROM BidList)
        """
    )

    # add shipment data
    cursor.execute(
        """
        SELECT t.buyer_id, t.transaction_id, t.address_id 
    FROM Transactions t
    inner JOIN CarListing c ON t.list_id = c.listid
    WHERE c.biddingDeadline > NOW() 
    AND c.isSold = 0
    AND t.buyer_id = c.highestBidHolder
    """
    )

    transaction = cursor.fetchall()

    if transaction:
        for row in transaction:
            cursor.execute(
                "INSERT INTO Shipping (user_id, transaction_id, tracking_number, address_id, status, date) VALUES (%s, %s, FLOOR(RAND() * 10000000000), %s, 'Pending', NOW()) ",
                [row[0], row[1], row[2]],
            )

    # update the status of the carlist to sold if the bidding deadline is passed, suppose we have more than one carlist that are out of date
    cursor.execute(
        """
            WITH BidList as (SELECT listid, highestBid, highestBidHolder FROM CarListing WHERE biddingDeadline < NOW() AND isSold = 0)
            UPDATE CarListing SET isSold = 1 WHERE listid in (SELECT listid FROM BidList)
        """
    )

    # end SQL transaction
    cursor.execute("Commit")

    print("Updated transactions")
    return JsonResponse({"message": "success"})




