# -*- coding:utf-8 -*-
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from django.db.models import Q
from channels.exceptions import DenyConnection
from django.contrib.auth.models import AnonymousUser
from rest_framework.authtoken.models import Token
from channels.auth import login
import random
from channels.db import database_sync_to_async
from registration.models import Patient_registration, Doctor, Account,Polyclinic,Location
import redis
import json
from datetime import datetime
import requests
from django.core import serializers
from .translate_lang import transliterate
from django.conf import settings
from registration.date import get_time_to_city
from .staging_database import DoctorState
from asgiref.sync import sync_to_async,async_to_sync
import codecs
from django.contrib.auth import authenticate, login
import logging
import time

logger = logging.getLogger(__name__)

class TrakkingConsumer(AsyncWebsocketConsumer):
    try:
        async def connect(self): # Подключение к веб сокетам !!!
            try:
                self.call = dict()
                self.list_pacient = dict()                
                self.coordinates = self.scope['url_route']['kwargs']['user_token']
                self.user = await self.get_user_decr(self.coordinates)
                self.coordinates_group_name = 'coordinates__for_user_%s' % self.coordinates
                self.db_name = 'State'
                self.client = DoctorState(self.db_name)
                self.create_user = self.client.initialize_object_in_db(self.user)
                self.town, self.list_pacient = await self.get_pacient(self.user)

                logging.info(self.list_pacient)
                await self.channel_layer.group_add(
                    self.coordinates_group_name,
                    self.channel_name,
                )
                
                await self.accept()
                logging.info('CONNECT')
                if self.create_user == False:
                    logging.info('Work last state')
                    self.new_connection = False
                    self.ids_list = [ids['id'] for ids in self.list_pacient]
                    self.town, self.list_pacient = await self.get_pacient(self.user,self.ids_list)
                else:
                    logging.info('New state')
                    self.ids_list = [ids['id'] for ids in self.list_pacient]
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[2], len(self.list_pacient))
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[3], json.dumps(self.ids_list))
                    
                    
                    await self.send(text_data=json.dumps({'list_pacient' : self.list_pacient})) 
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[9], False)
                
                self.users_state_db = self.client.get_user_parametrs(self.user)
            except Exception as e:
                logging.error('===== connect ==== : %s '%(e))

        async def disconnect(self, close_code): # Отключение
            logging.info(close_code)
            try:
                if close_code == 1000:
                    self.client.clean_db(self.user)
                    logging.info('DB DELETE :  %s ' % (self.client.get_all_users()))
            except Exception as e:
                logging.info(e)
            logging.info(close_code)
            await self.channel_layer.group_discard(
                self.coordinates_group_name,
                self.channel_name,
            )

            # self.client.clear_all_state()
            # logging.info('DB DELETE : %s ' % (self.client.get_all_users()))




        async def receive(self, text_data): # Прослушивание сокета для обработки данных 
            try:
                parameters_list ={}
                text_data_json = json.loads(text_data)

                if 'type_of_movement' in text_data_json:
                    type_of_movement = text_data_json['type_of_movement']
                    parameters_list['type_of_movement'] = type_of_movement
                else:
                    type_of_movement = ''

                if 'started_to' in text_data_json:
                    current_user = text_data_json['started_to']
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[1], current_user)
                    parameters_list['started_to'] = current_user
                else:
                    current_user = ''

                if 'lat' in text_data_json:
                    lat = text_data_json['lat']
                else:
                    lat = ''
                if 'lon' in text_data_json:
                    lon = text_data_json['lon']
                else:
                    lon = ''


                if 'delete_pacient_in_list' in text_data_json:
                    new_finish_lat = text_data_json['current_start_lat']
                    new_finish_lon = text_data_json['current_start_lon']
                    logging.warning('%s -- %s'% (new_finish_lat,new_finish_lon))
                    delete_pacient_in_list = text_data_json['delete_pacient_in_list']
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[0], json.dumps([delete_pacient_in_list]))
                    parameters_list['delete_pacient_in_list'] = 'Delete complite'
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[6], new_finish_lat)
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[7], new_finish_lon)
                    if 'time_close_call' in text_data_json:
                        finish_to = text_data_json['delete_pacient_in_list']
                        time_close_call = text_data_json['time_close_call']
                        logging.warning('==== intentional deletion time_close_call ==== : %s' % (time_close_call))
                        await self.close_call(int(finish_to),time_close_call)
                
                logging.info(self.client.get_all_users())
                if 'finished' in text_data_json:
                    finish_to = text_data_json['finished']

                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[0], json.dumps([finish_to]))
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[5], finish_to)
                    new_finish_lat = text_data_json['finish_lat']
                    new_finish_lon = text_data_json['finish_lon']
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[6], new_finish_lat)
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[7], new_finish_lon)
                    
                    accepted = 'OK'
                    parameters_list['finished'] = accepted
                    if 'time_close_call' in text_data_json:
                        time_close_call = text_data_json['time_close_call']
                        logging.warning('==== time_close_call ==== : %s' % (time_close_call))
                        await self.close_call(int(finish_to),time_close_call)
                if self.client.get_user_parametrs(self.user)['count_pacient'] == await self.get_count_pacient_in_db(self.user):
                    self.change = False
                else:
                    self.change = True

                
                polyclinic = await self.get_poluclinic_info(self.user)
                polyclinic = json.loads(polyclinic['polyclinic'])
                logging.warning('==== change ==== : %s' % (self.change))
                if self.change:
                    # try:
                    if self.client.get_user_parametrs(self.user)['create_rout']:
                        start_point_lat = self.client.get_user_parametrs(self.user)['new_finish_lat']
                        start_point_lon = self.client.get_user_parametrs(self.user)['new_finish_lon']
                        finish_point_lat      =   polyclinic['lat'] 
                        finish_point_lon      =   polyclinic['lon']
                        name_start_point      =   'Point_A'
                        name_finish_point     =   polyclinic['name']
                        exclude_ids = json.loads(self.client.get_user_parametrs(self.user)['exclude_ids'])
                        self.town, self.new_list_pacient = await self.get_pacient(self.user,exclude_ids)
                        self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[2], len(self.new_list_pacient))
                        json_data_update = {}
                        parameters_list['new_list_pacient'] = self.new_list_pacient
                        self.list_init_points = [
                            {
                                'strart_poin' : {
                                    'start_point_lat' : start_point_lat,
                                    'start_point_lon' : start_point_lon,
                                },
                                'finish_poin' : {
                                    'finish_point_lat' : finish_point_lat,
                                    'finish_point_lon' : finish_point_lon,
                                },
                                'name_start_point' : name_start_point,
                                'name_finish_point' : name_finish_point,

                            }
                        ]
                        if 'pedo' == self.client.get_user_parametrs(self.user)['type_of_movement']:
                            logging.info('One choise')
                            sort_point, new_complite_rout = self.get_a_ready_route(
                                self.town, 
                                self.list_init_points, 
                                self.new_list_pacient, 
                                self.client.get_user_parametrs(self.user)['type_of_movement']
                            )
                            logging.info(' === new_complite_rout === : %s' % (new_complite_rout))
                            parameters_list['new_complite_rout'] = new_complite_rout
                            parameters_list['new_sort_point'] = sort_point
                        else:
                            logging.info('Two choise')
                            sort_point, new_complite_rout = self.get_a_ready_route(
                                self.town, 
                                self.list_init_points, 
                                self.new_list_pacient, 
                                self.client.get_user_parametrs(self.user)['type_of_movement']
                            )
                            parameters_list['new_complite_rout'] = new_complite_rout
                            parameters_list['new_sort_point'] = sort_point
                    # except Exception as e:
                    #     print('Errors')
                    else:
                        finish_point_lat      =   polyclinic['lat'] # Больница
                        finish_point_lon      =   polyclinic['lon']# Больница
                        name_start_point      =   'Point_A'
                        name_finish_point     =   polyclinic['name'] # Больница
                else:
                    finish_point_lat      =   polyclinic['lat'] # Больница
                    finish_point_lon      =   polyclinic['lon']# Больница
                    name_start_point      =   'Point_A'
                    name_finish_point     =   polyclinic['name'] # Больница



                if 'start_point_lat' in text_data_json:
                    self.start_point_lat = text_data_json['start_point_lat']
                    parameters_list['start_point_lat'] =  self.start_point_lat
                else:
                    self.start_point_lat = 0
                    

                if 'start_point_lon' in text_data_json:
                    self.start_point_lon = text_data_json['start_point_lon']
                    parameters_list['start_point_lon'] = self.start_point_lon
                else:
                    self.start_point_lon = 0

                

                self.list_init_points = [
                    {
                        'strart_poin' : {
                            'start_point_lat' : self.start_point_lat,
                            'start_point_lon' : self.start_point_lon,
                        },
                        'finish_poin' : {
                            'finish_point_lat' : finish_point_lat,
                            'finish_point_lon' : finish_point_lon,
                        },
                        'name_start_point' : name_start_point,
                        'name_finish_point' : name_finish_point,

                    }
                ]
                
                
                parameters_list['type'] = 'auntification_user'
                
                await self.channel_layer.group_send( self.coordinates_group_name, parameters_list)
            except Exception as e:
                logging.error('==== receive ==== : %s' %(e))

        async def auntification_user(self, event): # Метод отправки данных
            try:
                logging.info(event)

                parameters_list = {}
                if 'type_of_movement' in event:
                    type_of_movement = event['type_of_movement']
                    self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[8], type_of_movement)

                    try:
                        if self.client.get_user_parametrs(self.user)['count_pacient'] == await self.get_count_pacient_in_db(self.user):
                            self.current_patient_list = self.list_pacient
                            parameters_list['initial_dispatch_list'] = self.current_patient_list
                        else:
                            self.town, self.current_patient_list = await self.get_pacient(self.user)
                            self.client.set_user_parametrs(self.user, DoctorState.LIST_KEY[2], len(self.current_patient_list))
                            parameters_list['initial_dispatch_list'] = self.current_patient_list
                    except Exception as e:
                        pass

                    if 'pedo' == self.client.get_user_parametrs(self.user)['type_of_movement']:
                        sort_point, complite_rout= self.get_a_ready_route(
                            self.town, 
                            self.list_init_points, 
                            self.current_patient_list, 
                            type_of_movement
                        )
                        parameters_list['complite_rout'] = complite_rout
                        parameters_list['sort_point'] = sort_point
                        self.client.set_user_parametrs(self.user, 'create_rout', True)
                    else:
                        sort_point, complite_rout = self.get_a_ready_route(
                            self.town, 
                            self.list_init_points, 
                            self.current_patient_list, 
                            type_of_movement
                        )
                        parameters_list['complite_rout'] = complite_rout
                        parameters_list['sort_point'] = sort_point
                        self.client.set_user_parametrs(self.user, 'create_rout', True)

                else:
                    type_of_movement = ''

                if 'current_user' in event:
                    current_user = event['current_user']
                    parameters_list['current_user'] = current_user
                else:
                    current_user = ''
                if 'get_user' in event:
                    get_user = event['get_user']
                    parameters_list['get_user'] = get_user
                else:
                    get_user = ''
                if 'get_rout' in event:
                    get_rout = event['get_rout']
                    parameters_list['get_rout'] = get_rout
                else:
                    get_rout = ''
                
                if 'close_state' in event:
                    close_state = event['close_state']
                    
                    parameters_list['close_state'] = close_state
                else:
                    close_state = False
                

                if 'finished' in event:
                    finish_to = event['finished']
                    accepted = 'OK'
                    
                    parameters_list['finished'] = accepted 
                    if 'new_sort_point' in event:
                        parameters_list['new_sort_point'] = event['new_sort_point']
                    if 'new_list_pacient' in event:
                        parameters_list['new_list_pacient'] = event['new_list_pacient']
                    if 'new_complite_rout' in event:
                        parameters_list['new_complite_rout'] = event['new_complite_rout']
                if 'delete_pacient_in_list' in event:
                    accepted = 'Delete complite'
                    parameters_list['delete_pacient_in_list'] = accepted 
                    if 'new_sort_point' in event:
                        parameters_list['new_sort_point'] = event['new_sort_point']
                    if 'new_list_pacient' in event:
                        parameters_list['new_list_pacient'] = event['new_list_pacient']
                    if 'new_complite_rout' in event:
                        parameters_list['new_complite_rout'] = event['new_complite_rout']

                logging.info('===== event ==== : %s' % (event))
                logging.info(self.client.get_all_users())
                await self.send(text_data=json.dumps(parameters_list))
            except Exception as e:
                logging.error('=====  auntification_user ==== : %s ' % (e))


        @database_sync_to_async
        def close_call(self, id_pacient, time):
            try:
                pacient = Patient_registration.objects.get(id = id_pacient)
                pacient.close_call = True
                pacient.time_close_call = time
                pacient.save()
            except Exception as e:
                logging.info('==== close_call ==== : %s' % (e))

        @database_sync_to_async
        def get_user_decr(self, token): # Аунтификация юзера по токену 
            token = Token.objects.get(key = token)
            ids = token.user.id
            return ids

        @database_sync_to_async
        def get_poluclinic_info(self, user):
            try:
                polyclinic = Doctor.objects.select_related('polyclinic').get(user = user)
                fields = {
                    'lat': polyclinic.polyclinic.lat,
                    'lon': polyclinic.polyclinic.lon,
                    'name': 'Polyclinic'
                }
                mapp = {
                    'polyclinic' : json.dumps(fields)
                }
                mapp = json.dumps(mapp)
                return json.loads(mapp)
            except Exception as e:
                logging.error('==== get_poluclinic_info ==== : %s' % (e))

        @database_sync_to_async
        def get_count_pacient_in_db(self,user_id):
            try:
                doctor = Doctor.objects.get(user__id = user_id)
                list_pacient = Patient_registration.objects.all().filter(
                    doctor = doctor, 
                    recording_time__date = get_time_to_city(doctor.town.time_shifting),
                    call_cancellation_state = False,
                    close_call = False                    
                )
                count_pacient = list_pacient.count()
                return count_pacient
            except Exception as e:
                logging.error('==== get_count_pacient_in_db ==== : %s ' % (e))

        @database_sync_to_async
        def get_pacient(self, user_id, exclude_id = None): 
            """ Получение пациентов для получение адресов """
            try:
                logging.info(user_id)
                doctor = Doctor.objects.get(user__id = user_id)
                logging.info(doctor)
                list_pacient = Patient_registration.objects
                if exclude_id:
                    list_pacient = list_pacient.filter(
                        doctor = doctor, 
                        recording_time__date = get_time_to_city(doctor.town.time_shifting),
                        call_cancellation_state = False,
                        close_call = False
                    ).exclude(id__in=exclude_id)
                    
                else:
                    list_pacient = list_pacient.filter(
                        doctor = doctor, 
                        recording_time__date = get_time_to_city(doctor.town.time_shifting),
                        call_cancellation_state = False,
                        close_call = False
                    )
                doctor_dict = {
                    'town' : doctor.town.name
                }


                json_list_pacient = serializers.serialize('json', list_pacient)
                json_list_pacient = json.loads(json_list_pacient)
                logging.info(list_pacient)
                complite_list = []
                print(json_list_pacient)
                for i in json_list_pacient:
                    location = Location.objects.get(id = i['fields']['address_fk'])
                    address = doctor_dict['town'] + ', ' + str(location.street) + ', ' + str(location.building)
                    points = self.get_points_at_the_address(address)
                    logging.info(points)
                    complite_list.append({
						'id' : i['pk'],
						'name': i['fields']['name'],
						'surname': i['fields']['surname'],
						'patronymic': i['fields']['patronymic'],
						'address' : address,
						'date_of_birth': i['fields']['date_of_birth'],
						'intercom_code': i['fields']['intercom_code'],
						'flat': i['fields']['flat'],
						'floor': i['fields']['floor'],
						'phone': i['fields']['phone'],
						'SNILS': i['fields']['SNILS'],
						'C_M_O_policy': i['fields']['C_M_O_policy'],
						'reason_for_calling': i['fields']['reason_for_calling'],
						'temperature': i['fields']['temperature'],
						'cough': i['fields']['cough'],
						'smell': i['fields']['smell'],
						'points' : points,
                        'coordinates'  : {
                            'lat': points['result']['items'][0]['point']['lat'],
                            'lon': points['result']['items'][0]['point']['lon']
                            }
					})
                return doctor_dict['town'], complite_list
            except Exception as e:
                logging.error('==== get_pacient =====  : %s ' % (e))
                return '',[]

        def completed_points(self, responses):
            """Из запроса  по ключю берём данные"""
            try:
                list_info = {}
                points = responses['result']['items'][0]['point']
                name = responses['result']['items'][0]['name']
                full_name = responses['result']['items'][0]['full_name']
                list_info['points'] = points
                list_info['name'] = name
                return list_info
            except Exception as e:
                logging.error('==== completed_points ==== %s ' % (e))

        def get_sort_points(self, start_lat,start_lon,finish_lat, finish_lon,points):
            """Сортировка точек , метод возвращает отсортированный json Набор геометрий """
            # Заголовки для запроса 
            try:
                headers = {
                'Content-type': 'application/json',  # Определение типа данных
                }
                sort_list_points_array = []
                for i in points:
                    lat = i['points']['lat']
                    lon = i['points']['lon']
                    sort_list_points_array.append({
                    "lat": lat,
                    "lon": lon,
                    "delay": 1200
                })
                request  = [{
                    "start": {
                        "lat": start_lat,
                        "lon": start_lon
                    },
                    "finish": {
                        "lat": finish_lat,
                        "lon": finish_lon
                    },
                    "checkpoints": sort_list_points_array,
                    "start_time": "2020-04-26T07:05:30Z"
                }]
                url_sort_points = 'http://catalog.api.2gis.ru/get_tsp?key=' + SECRET_KEY
                answer = requests.get(url_sort_points,data=json.dumps(request[0]), headers=headers)
                response = answer.json()  # Получаем json формат
    
                # logging.info(response)
                for i in [response]:
                    mapp = {}
                    finish = i['finish']['start_id']
                    start = i['start']['target_id']
                    status = i['status']
                    
                    start_index = start
                    for j in i['routes']:
                        mapp.update({j['start_id'] : j['target_id']})
                        
                    res = [points[start_index]]
                    for i in range(len(points)-1):
                        keyy = mapp[start_index]
                        res.append(points[keyy])
                        start_index = keyy
                return res
            except Exception as e:
                logging.error('==== get_sort_points ==== : %s' % (e))


        def get_way_on_carrouting(self, rout, start_point_name, finish_point_name,list_init_points):
            """
            По методу ctx шлём запрос на получения готового маршрута по точкам, 
            start_point --> Название точи старта, 
            finish_point --> Название конечной точки
            """
            try:
                complite_arr = []
                rout.insert(0,{
                    'points' : {
                        'lat': list_init_points[0]['strart_poin']['start_point_lat'], 
                        'lon': list_init_points[0]['strart_poin']['start_point_lon']
                    },
                    'name' : list_init_points[0]['name_start_point']
                })
                rout[len(rout):] = [{
                    'points' : {
                        'lat': list_init_points[0]['finish_poin']['finish_point_lat'], 
                        'lon': list_init_points[0]['finish_poin']['finish_point_lon']
                    },
                    'name' : list_init_points[0]['name_finish_point']
                }]
                for index in range(1,len(rout),1):
                    json_parametr = {
                        "locale": "ru",
                        "point_a_name" : rout[index-1]['name'],
                        "point_b_name" : rout[index]['name'],
                        "points": [
                            {
                            "type": "pedo",
                            "x": rout[index-1]['points']['lon'],
                            "y": rout[index-1]['points']['lat']
                            },
                            {
                            "object_id": "141476222741292",
                            "type": "pedo",
                            "x": rout[index]['points']['lon'],
                            "y": rout[index]['points']['lat']
                            }
                        ],
                        "type": "jam",
                    }
                    headers = {
                        'Content-type': 'application/json',  # Определение типа данных
                    }
                    json_data = json.dumps(json_parametr)
                    url_get_rout = 'https://catalog.api.2gis.com/carrouting/6.0.0/global?key=' + SECRET_KEY
                    answer = requests.post(url_get_rout,data=json_data, headers=headers)
                    response = answer.json()  # Получаем json формат
                    complite_arr.append(response)
                return complite_arr

            except Exception as e:
                logging.error('==== get_way_on_carrouting ==== : %s' % (e))

        def get_a_ready_route(self,town, list_init_points, json_list_pacient,type_of_movement):
            try:
                json_array = []
                for i in json_list_pacient:
                    complite_date = self.completed_points(i['points'])
                    json_array.append(complite_date)
                sort_point = self.get_sort_points(
                        list_init_points[0]['strart_poin']['start_point_lat'],
                        list_init_points[0]['strart_poin']['start_point_lon'],
                        list_init_points[0]['finish_poin']['finish_point_lat'],
                        list_init_points[0]['finish_poin']['finish_point_lon'],
                        json_array
                )
                if type_of_movement == 'pedo':
                    complite_rout = self.get_way_on_public_transport(
                        sort_point,
                        list_init_points,
                        town
                    )
                    return sort_point, complite_rout
                else:
                    name_start_point = list_init_points[0]['name_start_point']
                    name_finish_point = list_init_points[0]['name_finish_point']
                    complite_rout = self.get_way_on_carrouting(
                        sort_point, 
                        name_start_point,
                        name_finish_point,
                        list_init_points
                    )
                    return sort_point, complite_rout
            except Exception as e:
                logging.error('==== get_a_ready_route ==== : %s' % (e))

        def get_points_at_the_address(self, address):
            """Получаем точки из запроса по улице"""
            url_get_points = 'https://catalog.api.2gis.com/3.0/items/geocode?q=' + address + \
                            '&fields=items.point&key=' + settings.SECRET_KEY
            answer = requests.get(url_get_points) # data=json.dumps(data), headers=headers

            response = answer.json()  # Получаем json формат
            return response




        def get_way_on_public_transport(self, points, list_init_points,town):
            try:
                points.insert(0,{
                    'points' : {
                        'lat': list_init_points[0]['strart_poin']['start_point_lat'], 
                        'lon': list_init_points[0]['strart_poin']['start_point_lon']
                    },
                    'name' : list_init_points[0]['name_start_point']
                })
                points[len(points):] = [{
                    'points' : {
                        'lat': list_init_points[0]['finish_poin']['finish_point_lat'], 
                        'lon': list_init_points[0]['finish_poin']['finish_point_lon']
                    },
                    'name' : list_init_points[0]['name_finish_point']
                }]
                # logging.info(points)
                complite_arr = []
                for index in range(1,len(points),1):
                    transport ={
                        "locale": "ru",
                        "source": {
                            "name": points[index-1]['name'],
                            "point": {
                            "lat": points[index-1]['points']['lat'],
                            "lon": points[index-1]['points']['lon']
                            },
                            # "object_id": f"{users_state}"
                        },
                        "target": {
                            "name": points[index]['name'],
                            "point": {
                            "lat": points[index]['points']['lat'],
                            "lon": points[index]['points']['lon']
                            },
                            # "object_id": f"{users_state}"
                        },
                        "purpose": "routeSearch",
                        "transport": [
                            "pedestrian",
                            "bus",
                            "trolleybus",
                            "tram",
                            "shuttle_bus",
                            "metro",
                            "suburban_train",
                            "funicular_railway",
                            "monorail",
                            "river_transport",
                            "cable_car",
                            "light_rail",
                            "premetro",
                            "light_metro",
                            "aeroexpress"
                        ]
                    }
                    
                    headers = {
                        'Content-type': 'application/json',  # Определение типа данных
                    }
                    
                    json_data = json.dumps(transport)
                    url_get_rout = f'http://catalog.api.2gis.ru/ctx/2.0/{transliterate(town).lower()}/?key=' + SECRET_KEY
                    answer = requests.post(url_get_rout,data=json_data, headers=headers)
                    response = answer.json()  # Получаем json формат
                    complite_arr.append(response)
                return complite_arr
            except Exception as e:
                logging.error('==== get_way_on_public_transport ==== : %s' %(e))

    except Exception as e:
        logging.error(e)