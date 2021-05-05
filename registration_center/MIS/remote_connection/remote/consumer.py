import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.generic.websocket import WebsocketConsumer
from asgiref.sync import sync_to_async,async_to_sync
from rest_framework.authtoken.models import Token
from channels.db import database_sync_to_async
from .accountState import AccoutnState

class RemoteConsumer(AsyncWebsocketConsumer):
    try:
        async def connect(self): # Подключение к веб сокетам !!!
            try:
                self.remoute_user = self.scope['url_route']['kwargs']['user_token']
                self.user = await self.get_user_decr(self.remoute_user)

                self.remoute_user_group_name = 'remoute_user__for_user_%s' % self.remoute_user
                print(self.remoute_user_group_name)
                self.db_name = 'RemoteState'
                self.client = AccoutnState(self.db_name)
                self.create_user = await self.client.InitializeObjectInDB(self.user)
                print(self.client.GetAllUsers())

                print(self.client.GetUserParametrs(self.user))


                await self.channel_layer.group_add(
                    self.remoute_user_group_name,
                    self.channel_name,
                )
                
                await self.accept()
            except Exception as e:
                print('===== connect ==== : %s '%(e))

        async def disconnect(self, close_code): # Отключение

            await self.channel_layer.group_discard(
                self.remoute_user_group_name,
                self.channel_name,
            )

            # self.client.clear_all_state()
            # logging.info('DB DELETE : %s ' % (self.client.get_all_users()))




        async def receive(self, text_data): # Прослушивание сокета для обработки данных 
            try:


                parameters_list ={}
                text_data_json = json.loads(text_data)
                message = text_data_json['message']
                print(text_data_json)
                parameters_list['type'] = 'auntification_user'
                parameters_list['message'] = message




                await self.channel_layer.group_send( self.remoute_user_group_name, parameters_list)
            except Exception as e:
                print('==== receive ==== : %s' %(e))

        async def auntification_user(self, event): # Метод отправки данных
            try:
                print(event)

                parameters_list = {}
                await self.send(text_data=json.dumps(parameters_list))
            except Exception as e:
                print('=====  auntification_user ==== : %s ' % (e))


        @database_sync_to_async
        def get_user_decr(self, token): # Аунтификация юзера по токену 
            token = Token.objects.get(key = token)
            ids = token.user.id
            return ids

    except Exception as e:
        print(e)