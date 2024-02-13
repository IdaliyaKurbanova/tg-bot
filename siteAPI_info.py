import requests
import json
from config_data import config
from database.utils import AirlineMethods
from datetime import datetime


def transfers_suffix(transfers):
    if transfers % 10 == 1 and transfers % 100 != 11:
        return f"{transfers} пересадка"
    elif 4 >= transfers % 10 >= 2:
        return f"{transfers} пересадки"
    else:
        return f"{transfers} пересадок"


class APIResult:

    @staticmethod
    def get_airlines_codes():
        url = ('https://api.travelpayouts.com/data/ru/airlines.json?'
               '_gl=1*j9491*_ga*MTczNTg1NzUxMC4xNzA2NjE1ODg2*_ga_1WLL0NEBEH*MTc'
               'wNzI1MTkwMC45LjEuMTcwNzI1MjA3Ni40MS4wLjA.')
        airline_codes = json.loads(requests.request("GET", url).text)
        return airline_codes

    @staticmethod
    def get_cities_codes():
        url = ('https://api.travelpayouts.com/data/ru/cities.json?'
               '_gl=1*18dq1nk*_ga*MTczNTg1NzUxMC4xNzA2NjE1ODg2*_ga_'
               '1WLL0NEBEH*MTcwNzMzODU4MS4xMC4xLjE3MDczMzk3MDkuNjAuMC4w')
        cities_codes = json.loads(requests.request("GET", url).text)
        print(cities_codes)
        return cities_codes


    @staticmethod
    def get_cheapest_ticket(**kwargs):
        data_list = [f'{name}={value}' for name, value in kwargs.items()]
        data_str = "&".join(data_list)
        url = (f'https://api.travelpayouts.com/aviasales/v3/prices_for_dates?{data_str}'
               f'&unique=false&sorting=price&direct=false&cy=rub&limit=30&page=1&token={config.API_KEY}')
        response = json.loads(requests.request("GET", url).text)['data']
        print(response)
        if response:
            if response[0].get("return_at", 0):
                selected_data = [f"Цена за 2 билета: {flight['price']}\n "
                                 f"Авиакомпания (первая - при пересадках): {AirlineMethods.get_airline_name(flight['airline'])}\n"
                                 f"Дата вылета туда: {datetime.fromisoformat(flight['departure_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"Время в воздухе туда: {flight['duration_to'] // 60} ч {flight['duration_to'] % 60} мин. ({transfers_suffix(flight['transfers'])})\n"
                                 f"Дата вылета обратно: {datetime.fromisoformat(flight['return_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"Время в воздухе обратно: {flight['duration_back'] // 60} ч {flight['duration_back'] % 60} мин. ({transfers_suffix(flight['return_transfers'])})\n"
                                 for flight in response]
            else:
                selected_data = [f"Цена: {flight['price']}\n "
                                 f"Авиакомпания (первая - при пересадках): {AirlineMethods.get_airline_name(flight['airline'])}\n"
                                 f"Дата и время вылета: {datetime.fromisoformat(flight['departure_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"Общее время в пути: {flight['duration'] // 60} ч {flight['duration'] % 60} мин. ({transfers_suffix(flight['transfers'])})\n"
                                 for flight in response]
            return selected_data
        return response

    @staticmethod
    def get_month_ticket(**kwargs):
        data_list = [f'{name}={value}' for name, value in kwargs.items()]
        data_str = "&".join(data_list)
        url = (f'http://api.travelpayouts.com/v2/prices/month-matrix?{data_str}'
               f'&show_to_affiliates=true&token={config.API_KEY}')
        response = json.loads(requests.request("GET", url).text)['data']
        print(response)
        if response:
            selected_data = [f"Цена: {flight['value']}\n"
                             f"Дата вылета: {datetime.fromisoformat(flight['depart_date']).strftime('%d-%m-%Y')}\n"
                             f"Общее время в пути: {flight['duration'] // 60} ч {flight['duration'] % 60} мин. "
                             f"({transfers_suffix(flight['number_of_changes'])})\n"
                             for flight in response]
            return selected_data
        return response





# APIResult.get_month_ticket(origin='KZN', destination='IST', month='2024-02-01')

# APIResult.get_airlines_codes()









