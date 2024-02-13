from siteAPI_info import APIResult
from database.models import Airline, City, Session


def necessary_codes_creation() -> None:
    airline_codes = APIResult.get_airlines_codes()
    cities_codes = APIResult.get_cities_codes()
    with Session() as session:
        list_of_airline_codes = [Airline(code=line['code'], name=line['name_translations']['en'])
                                for line in airline_codes]
        list_of_cities_codes = [City(code=city['code'], name=str(city['name']).lower())
                                for city in cities_codes]
        session.add_all(list_of_airline_codes)
        session.add_all(list_of_cities_codes)
        session.commit()


if __name__ == "__main__":
    necessary_codes_creation()