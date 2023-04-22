from django.shortcuts import render,redirect
from django.http import HttpResponse,JsonResponse
from django.core.exceptions import ValidationError
from django.contrib import messages
import ast
from amadeus import  ResponseError
from .forms import FlightForm
from .api import amadeus


def get_flights(form):
    origin_location = form.cleaned_data.get('from_location')
    destination_location = form.cleaned_data.get('to_location')
    departure_date = form.cleaned_data.get('departure_date')
    return_date = form.cleaned_data.get('return_date')
    travel_class = form.cleaned_data.get('travel_class')
    adults = form.cleaned_data.get('adults')
    kids = form.cleaned_data.get('kids')

    origin_code  = amadeus.reference_data.locations.get(
        subType='CITY',
        keyword=origin_location ,
        view='LIGHT'
    ).data[0]['iataCode']

    destination_code = amadeus.reference_data.locations.get(
        subType='CITY',
        keyword=destination_location,
        view='LIGHT'
    ).data[0]['iataCode']

    try:
        # Search for flight offers
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin_code,
            destinationLocationCode=destination_code,
            departureDate=departure_date,
            returnDate=return_date,
            adults=adults,
            max=15
            # kids=kids
        )
        return response
    except Exception as error:
        print(error)
        raise ValidationError("Error occurred while searching for flights")


def my_view(request):
    if request.method == 'POST':
        form = FlightForm(request.POST)
        if form.is_valid():
            try:
                response = get_flights(form)
                print(len(response.data))
                context = {'form': form, 'errors': form.errors,'response': response.data}
                return render(request, 'index.html', context)
            except Exception as e:
                print(e)
                context = {'form': form, 'errors': {'error':[e]}}
                return render(request, 'index.html', context)
        else:
            # If the form is not valid, re-render the form with error messages
            context = {'form': form, 'errors': form.errors}
            return render(request, 'index.html', context)
    else:
        form = FlightForm()
    return render(request, 'index.html', {'form': form})

def confirmation(request, confirmation_number):
    # Render the confirmation template with the confirmation number
    return render(request, 'confirmation.html', {'confirmation_number': confirmation_number})


def test(request):    
    try:
        origin_response = amadeus.reference_data.locations.get(
        subType='CITY',
        keyword='CAIRO',
        view='LIGHT'
        )

        origin_code = origin_response.data[0]['iataCode']

    # Use the Amadeus location search API to get the IATA code for the destination city
        destination_response = amadeus.reference_data.locations.get(
            subType='CITY',
            keyword='LONDON',
            view='LIGHT'
        )
      
        destination_code = destination_response.data[0]['iataCode']
        response = amadeus.shopping.flight_offers_search.get(
                originLocationCode= origin_code,
                destinationLocationCode=destination_code,
                departureDate='2023-11-01',
                adults=1,max=1)

     
        return HttpResponse(response.data, "application/json")
    except ResponseError as error:
        print(error)
        return HttpResponse("response.data", "application/json")

def amadeus_location_autocomplete(request):
    query = request.GET.get('term', '')

    try:
        locations = amadeus.reference_data.locations.get(
            subType='CITY',
            keyword=query
        ).data
    except ResponseError as error:
        print(error)
        return JsonResponse([], safe=False)

    location_codes = [location['name'] for location in locations]

    return JsonResponse(location_codes, safe=False)

def book_flight(request):
    flight = request.POST.get('flight')
    # Create a fake traveler profile for booking
    traveler = {
        "id": "1",
        "dateOfBirth": "1982-01-16",
        "name": {"firstName": "JORGE", "lastName": "GONZALES"},
        "gender": "MALE",
        "contact": {
            "emailAddress": "jorge.gonzales833@telefonica.es",
            "phones": [
                {
                    "deviceType": "MOBILE",
                    "countryCallingCode": "34",
                    "number": "480080076",
                }
            ],
        },
        "documents": [
            {
                "documentType": "PASSPORT",
                "birthPlace": "Madrid",
                "issuanceLocation": "Madrid",
                "issuanceDate": "2015-04-14",
                "number": "00000000",
                "expiryDate": "2025-04-14",
                "issuanceCountry": "ES",
                "validityCountry": "ES",
                "nationality": "ES",
                "holder": True,
            }
        ],
    }
    # Use Flight Offers Price to confirm price and availability
    try:
        flight_price_confirmed = amadeus.shopping.flight_offers.pricing.post(
            ast.literal_eval(flight)
        ).data["flightOffers"]
    except ResponseError as error:
        messages.error(request, error.response.body)
        return redirect('book_flight')

    # Use Flight Create Orders to perform the booking
    try:
        order = amadeus.booking.flight_orders.post(
            flight_price_confirmed, traveler
        ).data
    except ResponseError as error:
        messages.error(
            request, error.response.result["errors"][0]["detail"]
        )
        return redirect('book_flight')

    # Redirect to confirmation page on success
    confirmation_number = order['id']
    print(order)
    context = {'confirmation_number': confirmation_number}
    return render(request, 'confirmation.html', context)
