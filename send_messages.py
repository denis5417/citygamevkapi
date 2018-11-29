import vk_api
import random
import wikipedia
import requests
import re
import os
from vk_api.longpoll import VkLongPoll, VkEventType

cities = open("cities.txt").read().lower().split("\n")
used_cities = {}
last_answer = {}
wikipedia.set_lang("ru")


def check_city(city):
    if city not in cities:
        return False
    try:
        if not current_city.startswith(last_answer[current_user_id][-1]):
            return "wrong_last_letter"
    except KeyError:
        last_answer[current_user_id] = None
    try:
        if city in used_cities[current_user_id]:
            return "used_city"
    except KeyError:
        used_cities[current_user_id] = list()
    return True


def find_city(city):
    tmp_list = list(filter(lambda c: c not in used_cities[current_user_id] and c.startswith(city[-1]), cities))
    return tmp_list[random.randint(0, len(tmp_list) - 1)] if len(tmp_list) != 0 else 0


def get_info(search):
    try:
        inf = wikipedia.page(wikipedia.search(search + " (город)")[0])
        return inf.summary + "\n" + inf.url if "город" in inf.summary else None
    except:
        pass


def add_new_city(city):
    try:
        url = "https://maps.googleapis.com/maps/api/geocode/json?address={}&language=ru".format(city)
        r = requests.get(url)
        report = r.json()
        if report["results"][0]["types"][0] == "locality":
            return report["results"][0]["address_components"][0]["long_name"]
    except:
        pass


access_token = 'TOKEN'
values = {'out': 0, 'count': 100, 'time_offset': 60}
vk = vk_api.VkApi(token=access_token)
longpoll = VkLongPoll(vk)

for event in longpoll.listen():
    if not (event.type == VkEventType.MESSAGE_NEW and event.to_me):
        continue
    current_user_id = ""
    try:
        #response = vk.method('messages.get', values)
        #print(response)
        if True:
            #values['last_message_id'] = response['items'][0]['id']
            current_user_id = event.user_id
            current_city = event.text.lower()
            current_city = re.sub(r'-\d+', "", current_city)
            if current_city == "":
                vk.method('messages.send', {'user_id': current_user_id, 'message': "Пришли название города"})
            if current_city == "сдаюсь":
                vk.method('messages.send', {'user_id': current_user_id, 'message': "Я победил) Начнем заново? Ты ходишь!"})
                del used_cities[current_user_id]
                del last_answer[current_user_id]
                continue
            if "инфо" in current_city:
                if current_city.replace("инфо ", "") in cities:
                    info = get_info(current_city.replace("инфо ", ""))
                    if info:
                        vk.method('messages.send' , {'user_id': current_user_id , 'message': info})
                    else:
                        vk.method('messages.send' , {'user_id': current_user_id , 'message': "Возникла ошибка при поиске статьи об этом городе"})
                else:
                    vk.method('messages.send' , {'user_id': current_user_id , 'message': "Такого города нет в списке"})
                continue
            if "добавить" in current_city:
                vk.method('messages.send' , {'user_id': current_user_id ,'message': "Google MAPS API теперь платное"})
                #add = add_new_city(current_city.replace("добавить ", ""))
                #if current_city.replace("добавить", "") == "":
                #    vk.method('messages.send', {'user_id': current_user_id, 'message': "Некорректная команда или такой город не найден"})
                #try:
                #    add = re.sub(r'-\d+', "", add)
                #except:
                #    pass
                #if add:
                #    if add.lower() in cities:
                #        vk.method('messages.send', {'user_id': current_user_id , 'message': "Город {} уже есть в списке".format(add)})
                #        continue
                #    file = open("cities.txt", "a")
                #    file.write("\n" + add)
                #    file.close()
                #    cities.append(add.lower())
                #    vk.method('messages.send' , {'user_id': current_user_id , 'message': "Город {} добавлен в список городов".format(add)})
                #else:
                #    vk.method('messages.send' , {'user_id': current_user_id ,'message': "Некорректная команда или такой город не найден"})
                #continue
            check = check_city(current_city)
            if current_city[-1] == "ь" or current_city[-1] == "ъ" or current_city[-1] == "ы":
                current_city1 = current_city[0:-1]
            else:
                current_city1 = current_city
            if check:
                if check == "used_city":
                    vk.method('messages.send', {'user_id': current_user_id, 'message': "Этот город уже был"})
                elif check == "wrong_last_letter":
                    vk.method('messages.send', {'user_id': current_user_id, 'message': "Город должен начинаться с буквы {}".format(last_answer[current_user_id][-1])})
                else:
                    used_cities[current_user_id].append(current_city)
                    answer_city = find_city(current_city1)
                    if answer_city:
                        used_cities[current_user_id].append(answer_city)
                        if answer_city[-1] == "ь" or answer_city[-1] == "ъ" or answer_city[-1] == "ы":
                            last_answer[current_user_id] = answer_city[0:-1]
                        else:
                            last_answer[current_user_id] = answer_city
                        vk.method('messages.send', {'user_id': current_user_id , 'message': answer_city.title()})
                    else:
                        vk.method('messages.send', {'user_id': current_user_id , 'message': "Я сдаюсь, ты выиграл! Начнем заново? Ты ходишь!"})
                        del used_cities[current_user_id]
                        del last_answer[current_user_id]
            else:
                vk.method('messages.send', {'user_id': current_user_id, 'message': "Такого города нет в списке"})
    except wikipedia.exceptions.DisambiguationError:
        vk.method('messages.send' , {'user_id': current_user_id , 'message': "Возникла ошибка при поиске статьи об этом городе"})
    except:
        pass



