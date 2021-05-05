# -*- coding: utf8 -
import redis
import json
from collections import OrderedDict
import logging


class DoctorState:
	LIST_KEY = (
		'exclude_ids',
		'current_user',
		'count_pacient',
		'ids_pacient',
		'current_rout',
		'finish_to',
		'new_finish_lat',
		'new_finish_lon',
		'type_of_movement',
	)
	def __init__(self, db_name):
		"""Конструктор класса промежуточного состаяния на момент вызова врача"""
		self.connection = redis.Redis(host='localhost', port=6379,db=10)
		self.db_name = db_name

	def initialize_object_in_db(self, user_id):
		"""Создаёт нового пользователя в бд"""
		try:
			all_connection = self.connection.hgetall(self.db_name)
			if bytes('users_{}'.format(user_id),encoding='utf-8') in all_connection:
				return False
			else:
				person = {
					'id' : user_id,
					'call_id': len(self.connection.hgetall(self.db_name)) + 1,
					'create_rout' : False
				}
				objects = {
					f'users_{user_id}' : json.dumps(person)
				}
				self.connection.hmset(self.db_name, objects)
			return True
		except Exception as e:
			logging.info('==== initialize_object_in_db ==== : %s' % (e))
			# pass
	
	def clean_db(self, id_key):
		"""Очищает бд по ключу, путём перезаписыванием словаря"""
		try:
			key = bytes(
				'users_{}'.format(id_key),
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
			logging.info('==== clean_db ==== %s' %(e))

	def get_all_users(self):
		"""Возвращает все данные из бд"""
		return self.connection.hgetall(self.db_name)

	def clear_all_state(self):
		"""Очищает всю используемую бд"""
		# self.connection.unlink(self.db_name) Для старой версии Redis
		self.connection.flushdb()

	def get_user_parametrs(self, id_key):
		"""Геттер класса DoctorState (Возвращает по ключу значение из бд Redis)"""
		try:
			key = bytes(
				'users_{}'.format(id_key),
				encoding='utf-8'
			)
			compound = json.loads(
				self.connection.hgetall(self.db_name)[key].decode('utf-8')
			)
			return compound
		except Exception as e:
			logging.info('==== get_user_parametrs ==== %s ' % (e))
	def set_user_parametrs(self, id_key, key_parametr, value):
		"""Устанавливает по ключу значение переданных через параметры метада , бд Redis"""
		try:
			key = bytes(
			'users_{}'.format(id_key),
			encoding='utf-8'
			)
			compound = json.loads(
				self.connection.hgetall(self.db_name)[key].decode('utf-8')
			)
			try:
				if (key_parametr == self.LIST_KEY[0]) and (key_parametr in compound):
					try:
						value = json.loads(value)
					except Exception as e:
						value = value
					if compound[key_parametr] in compound.values():
						mapp = json.loads(compound[key_parametr])
						for i in value:
							mapp.append(i)
						compound[key_parametr] = json.dumps(mapp)
						self.connection.hset(self.db_name, key, json.dumps(compound))
						return True
					
				if (key_parametr == self.LIST_KEY[3]) and (key_parametr in compound):
					try:
						value = json.loads(value)
					except Exception as e:
						value = value
					if compound[key_parametr] in compound.values():
						mapp = json.loads(compound[key_parametr])
						for i in value:
							mapp.append(i)
						mapp = list(OrderedDict.fromkeys(mapp))
						compound[key_parametr] = json.dumps(mapp)
						self.connection.hset(self.db_name, key, json.dumps(compound))
						return True

			except Exception as e:
				logging.info('==== set_user_parametrs (level 2) ==== %s ' %(e))
				return False

			compound[key_parametr] = value
			self.connection.hset(self.db_name, key, json.dumps(compound))
			return True
		except Exception as e:
			return False
			logging.info('==== set_user_parametrs ==== %s ' % (e))
