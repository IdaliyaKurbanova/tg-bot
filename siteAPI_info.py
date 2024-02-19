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


def get_cheapest_ticket(response):
    list_of_prices = [value['price'] for value in response.values()]
    min_price = min(list_of_prices)
    return list_of_prices.index(min_price)


def get_fastest_ticket(response):
    list_of_durations = [(value['duration'] // 60 + value['duration'] % 60 * 0.01) for value in response.values()]
    min_duration = min(list_of_durations)
    return list_of_durations.index(min_duration)


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
        return cities_codes

    @staticmethod
    def get_cheapest_ticket(**kwargs):
        data_list = [f'{name}={value}' for name, value in kwargs.items()]
        data_str = "&".join(data_list)
        url = (f'https://api.travelpayouts.com/aviasales/v3/prices_for_dates?{data_str}'
               f'&unique=false&sorting=price&direct=false&cy=rub&limit=30&page=1&token={config.API_KEY}')
        response = json.loads(requests.request("GET", url).text)['data']
        if response:
            if response[0].get("return_at", 0):
                selected_data = [f"Цена за 2 билета: {flight['price']}\n "
                                 f"Авиакомпания (первая - при пересадках): {AirlineMethods.get_airline_name(flight['airline'])}\n"
                                 f"Дата вылета туда: {datetime.fromisoformat(flight['departure_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"Дата вылета обратно: {datetime.fromisoformat(flight['return_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"Время в пути туда+обратно: {flight['duration'] // 60} ч {flight['duration'] % 60} мин.\n"
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
    def get_direct_ticket(**kwargs):
        data_list = [f'{name}={value}' for name, value in kwargs.items()]
        data_str = "&".join(data_list)
        url = (f'http://api.travelpayouts.com/v1/prices/direct?{data_str}'
               f'&token={config.API_KEY}')
        response = json.loads(requests.request("GET", url).text)['data']
        print(response)
        if response:
            response = response[kwargs['destination']]
            if "return_at" in kwargs.keys():
                selected_data = [f"Цена за 2 билета: {value['price']}\n"
                                 f"Авиакомпания: {AirlineMethods.get_airline_name(value['airline'])}\n"
                                 f"Дата вылета туда: {datetime.fromisoformat(value['departure_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"Дата вылета обратно: {datetime.fromisoformat(value['return_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 for key, value in response.items()]
            else:
                selected_data = [f"Цена: {value['price']}\n"
                                 f"Авиакомпания: {AirlineMethods.get_airline_name(value['airline'])}\n"
                                 f"Дата вылета: {datetime.fromisoformat(value['departure_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 for key, value in response.items()]
            return selected_data
        return response

    @staticmethod
    def get_custom_tickets_detailed(**kwargs):
        data_list = [f'{name}={value}' for name, value in kwargs.items() if name != "one_way"]
        data_str = "&".join(data_list)
        url = (f'https://api.travelpayouts.com/aviasales/v3/grouped_prices?{data_str}'
               f'&token={config.API_KEY}')
        response = json.loads(requests.request("GET", url).text)['data']
        if response:
            if "return_at" in kwargs.keys():
                selected_data = [f"Дата: {key}\n "
                                 f"  Цена за 2 билета: {value['price']}\n "
                                 f"  Авиакомпания (первая - при пересадках): {AirlineMethods.get_airline_name(value['airline'])}\n"
                                 f"  Дата вылета туда: {datetime.fromisoformat(value['departure_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"  Время в воздухе туда: {value['duration_to'] // 60} ч {value['duration_to'] % 60} мин. ({transfers_suffix(value['transfers'])})\n"
                                 f"  Дата вылета обратно: {datetime.fromisoformat(value['return_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"  Время в воздухе обратно: {value['duration_back'] // 60} ч {value['duration_back'] % 60} мин. ({transfers_suffix(value['return_transfers'])})\n"
                                 for key, value in response.items()]
            else:
                selected_data = [f"Дата: {key}\n "
                                 f"  Цена: {value['price']}\n "
                                 f"  Авиакомпания (первая - при пересадках): {AirlineMethods.get_airline_name(value['airline'])}\n"
                                 f"  Дата и время вылета: {datetime.fromisoformat(value['departure_at']).strftime('%d-%m-%Y %H:%M')}\n"
                                 f"  Общее время в пути: {value['duration'] // 60} ч {value['duration'] % 60} мин. ({transfers_suffix(value['transfers'])})\n"
                                 for key, value in response.items()]
            return selected_data
        return response

    @staticmethod
    def get_custom_tickets_short(**kwargs):
        data_list = [f'{name}={value}' for name, value in kwargs.items() if name != "one_way"]
        data_str = "&".join(data_list)
        url = (f'https://api.travelpayouts.com/aviasales/v3/grouped_prices?{data_str}'
               f'&token={config.API_KEY}')
        response = json.loads(requests.request("GET", url).text)['data']
        min_price = get_cheapest_ticket(response)
        min_duration = get_fastest_ticket(response)
        if response:
            if "return_at" in kwargs.keys():
                if kwargs.get("group_by") == "departure_at":
                    selected_data = [(f"{datetime.fromisoformat(value['departure_at']).strftime('%d.%m.%y')}   "
                                      f"{datetime.fromisoformat(value['return_at']).strftime('%d.%m.%y')}  "
                                      f"{value['price']} р.  "
                                      f"{value['duration'] // 60}ч {value['duration'] % 60}м.")
                                     for key, value in response.items()]
                else:
                    selected_data = [(f"{datetime.fromisoformat(value['return_at']).strftime('%d.%m.%y')}   "
                                      f"{datetime.fromisoformat(value['departure_at']).strftime('%d.%m.%y')}   "
                                      f"{value['price']} р.  "
                                      f"{value['duration'] // 60}ч {value['duration'] % 60}м.")
                                     for key, value in response.items()]
            else:
                selected_data = [f"{datetime.fromisoformat(value['departure_at']).strftime('%d-%m-%y')}    "
                                 f"{value['price']} р.    "
                                 f"{value['duration'] // 60} ч {value['duration'] % 60} м."
                                 for key, value in response.items()]
            selected_data[min_price] = selected_data[min_price] + "   * \n- один из самых дешёвых"
            selected_data[min_duration] = selected_data[min_duration] + "   # \n- один из самых быстрых"
            return "\n".join(selected_data)
        return response













