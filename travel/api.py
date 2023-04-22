from django.core.exceptions import ValidationError
from amadeus import Client, ResponseError



amadeus = Client(
    client_id='7DaMu2phgdMK1CmWSKPI6vZqfb3NlWcN',
    client_secret='ZAYlQleVPu3spA5J'
)

def validate_amadeus_location(value):
    try:
        locations = amadeus.reference_data.locations.get(
            subType='CITY',
            keyword=value,
        ).data
    except ResponseError as error:
        raise ValidationError("Invalid location")

    if not locations:
        raise ValidationError("There is no airport at this location")