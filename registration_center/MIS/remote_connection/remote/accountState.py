import redis
import json
from collections import OrderedDict
import logging
from datetime import datetime, timedelta
from registration.models import Account
from channels.db import database_sync_to_async
from asgiref.sync import sync_to_async

class AccoutnState:
    LIST_KEY_FOR_POLYCLINIC = (
    )
    
    def __init__(self, db_name):
        """Конструктор класса промежуточного состаяния"""
        self.connection = redis.Redis(host='localhost', port=6379,db=10)
        self.db_name = db_name


    async def InitializeObjectInDB(self, user_id) -> bool:
        """Создаёт нового пользователя в бд"""
        try:
            all_connection = self.connection.hgetall(self.db_name)
            type_account = await self.GetTypeAccount(user_id)
            if bytes('pacient_{}'.format(user_id),encoding='utf-8') in all_connection:
                return False
            else:
                person = {
                    'ID' : user_id,
                    'date_time_start': datetime.strftime(datetime.now(), '%Y-%m-%d'),
                    'date_time_end': datetime.strftime(datetime.now() + timedelta(days=1), '%Y-%m-%d'),
                    'type' : type_account,
                }
                if type_account == 'Stuff polyclinic':
                    person['mac'] = ''
                
                objects = {
                    f'pacient_{user_id}' : json.dumps(person)
                }
                print(objects)
                self.connection.hmset(self.db_name, objects)
            return True
        except Exception as e:
            print('==== initialize_object_in_db ==== : %s' % (e))
            return False

    def CleanDB(self, id_key):
        """Очищает бд по ключу, путём перезаписыванием словаря"""
        try:
            key = bytes(
                'pacient_{}'.format(id_key),
                encoding='utf-8'
            )
            compound = self.connection.hgetall(self.db_name)
            del compound[key]
            self.connection.flushdb()
            self.connection.hmset(self.db_name, compound)

            try:
                if self.connection.hgetall(self.db_name)[key]:
                    return True
                else:
                    return False
            except:
                return True
        except Exception as e:
            print('==== clean_db ==== %s' %(e))

    def GetAllUsers(self) -> json:
        """Возвращает все данные из бд"""
        return self.connection.hgetall(self.db_name)

    def ClearAllState(self):
        """Очищает всю используемую бд"""
        # self.connection.unlink(self.db_name)
        self.connection.flushdb()

    @sync_to_async
    def GetTypeAccount(self, user_id) -> str:
        """Возвращает тип аккаунта"""
        account = Account.objects.get(user__id = user_id).user_type
        return str(account)

    def GetUserParametrs(self, id_key) -> json:
        """Геттер класса DoctorState (Возвращает по ключу значение из бд Redis)"""
        try:
            key = bytes(
                'pacient_{}'.format(id_key),
                encoding='utf-8'
            )
            compound = json.loads(
                self.connection.hgetall(self.db_name)[key].decode('utf-8')
            )
            return compound
        except Exception as e:
            print('==== get_user_parametrs ==== %s ' % (e))


    def SetUserParametrs(self, id_key, key_parametr, value):
        """Устанавливает по ключу значение переданных через параметры метада , бд Redis"""
        try:
            key = bytes(
            'pacient_{}'.format(id_key),
            encoding='utf-8'
            )
            compound = json.loads(
                self.connection.hgetall(self.db_name)[key].decode('utf-8')
            )

            # try:
            # 	if (key_parametr == self.LIST_KEY[0]) and (key_parametr in compound):
            # 		try:
            # 			value = json.loads(value)
            # 		except Exception as e:
            # 			value = value
            # 		if compound[key_parametr] in compound.values():
            # 			mapp = json.loads(compound[key_parametr])
            # 			for i in value:
            # 				mapp.append(i)
            # 			compound[key_parametr] = json.dumps(mapp)
            # 			self.connection.hset(self.db_name, key, json.dumps(compound))
            # 			return True
                
                
                    
            # 	if (key_parametr == self.LIST_KEY[3]) and (key_parametr in compound):
            # 		try:
            # 			value = json.loads(value)
            # 		except Exception as e:
            # 			value = value
            # 		if compound[key_parametr] in compound.values():
            # 			mapp = json.loads(compound[key_parametr])
            # 			for i in value:
            # 				mapp.append(i)
            # 			mapp = list(OrderedDict.fromkeys(mapp))
            # 			compound[key_parametr] = json.dumps(mapp)
            # 			self.connection.hset(self.db_name, key, json.dumps(compound))
            # 			return True

            # except Exception as e:
            # 	print('==== set_user_parametrs (level 2) ==== %s ' %(e))
            # 	return False
            # print(compound[key_parametr])
            compound[key_parametr] = value
            self.connection.hset(self.db_name, key, json.dumps(compound))
            return True
        except Exception as e:
            return False
            print('==== set_user_parametrs ==== %s ' % (e))
            # pass