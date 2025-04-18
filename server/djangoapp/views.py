from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import CarMake, CarModel
from .populate import initiate
from .restapis import get_request, analyze_review_sentiments, post_review
import logging
import json

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)


@csrf_exempt
def logout_request(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST allowed"}, status=405)
    logout(request)
    return JsonResponse({"status": "Logged out"})


@csrf_exempt
def registration(request):
    data = json.loads(request.body)
    username = data["userName"]
    password = data["password"]
    first_name = data["firstName"]
    last_name = data["lastName"]
    email = data["email"]
    username_exist = False
    try:
        User.objects.get(username=username)
        username_exist = True
    except Exception:
        logger.debug("{} is new user".format(username))

    if not username_exist:
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
            email=email,
        )
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    else:
        data = {"userName": username, "error": "Already Registered"}

    return JsonResponse(data)


def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related("car_make")
    cars = [{"CarModel": cm.name, "CarMake": cm.car_make.name} for cm in car_models]
    return JsonResponse({"CarModels": cars})


def get_dealerships(request, state="All"):
    endpoint = "/fetchDealers" if state == "All" else f"/fetchDealers/{state}"
    dealerships = get_request(endpoint)
    return JsonResponse({"status": 200, "dealers": dealerships})


def get_dealer_reviews(request, dealer_id):
    if dealer_id:
        try:
            endpoint = f"/fetchReviews/dealer/{dealer_id}"
            reviews = get_request(endpoint)
            if not isinstance(reviews, list):
                return JsonResponse({"status": 200, "reviews": []})

            for review_detail in reviews:
                try:
                    review_text = review_detail.get("review", "")
                    response = analyze_review_sentiments(review_text)
                    sentiment = (
                        response.get("sentiment", "neutral") if response else "neutral"
                    )
                    review_detail["sentiment"] = sentiment
                except Exception as sentiment_error:
                    logger.warning(f"Sentiment analysis failed: {sentiment_error}")
                    review_detail["sentiment"] = "neutral"

            return JsonResponse({"status": 200, "reviews": reviews})

        except Exception as e:
            logger.error(f"Error in get_dealer_reviews: {e}")
            return JsonResponse(
                {"status": 500, "message": "Server error loading reviews"}
            )

    return JsonResponse({"status": 400, "message": "Invalid dealer ID"})


def get_dealer_details(request, dealer_id):
    if dealer_id:
        endpoint = f"/fetchDealer/{dealer_id}"
        dealership = get_request(endpoint)
        return JsonResponse({"status": 200, "dealer": dealership})
    return JsonResponse({"status": 400, "message": "Bad Request"})


def add_review(request):
    if not request.user.is_anonymous:
        data = json.loads(request.body)
        try:
            post_review(data)
            return JsonResponse({"status": 200})
        except Exception as e:
            logger.error(f"Error posting review: {e}")
            return JsonResponse({"status": 401, "message": "Error in posting review"})
    return JsonResponse({"status": 403, "message": "Unauthorized"})
