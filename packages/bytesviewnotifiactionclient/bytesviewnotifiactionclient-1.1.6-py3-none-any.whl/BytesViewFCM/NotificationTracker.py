import mysql.connector
from mysql.connector import Error
from BytesViewFCM.notification_exception import TableNotExistError
import json
from BytesViewFCM.utils import get_redis_connection
class NotificationTracker:

    def __init__(self,database_config,redis_config=None):
        self.host =database_config ['host']
        self.database =database_config ['database']
        self.user = database_config['user']
        self.port=int(database_config.get('port',"3306"))
        self.password = database_config['password']
        self.notification_log_table=database_config.get('notification_log_table','user_notification_tracking')
        self.device_token_table=database_config.get('device_token_table','user_device_info')
        self.connection=None
        self.redis_config=redis_config
        self.redis_connecion=None


    def update_invalid_tokens_in_redis(self, user_device_list):
        try:
            user_device_map = {}
            for item in user_device_list:
                user_device_map.setdefault(item['user_id'], set()).add(item['device_id'])
            pipeline = self.redis_connecion.pipeline()
            redis_keys = {user_id: f"user:{user_id}" for user_id in user_device_map}
            for redis_key in redis_keys.values():
                pipeline.hget(redis_key, "devices")
            redis_data = pipeline.execute()
            pipeline = self.redis_connecion.pipeline()
            for index, (user_id, devices_to_remove) in enumerate(user_device_map.items()):
                redis_key = redis_keys[user_id]
                existing_data = redis_data[index]               
                if existing_data:
                    parsed_devices = json.loads(existing_data)
                    updated_devices = [device for device in parsed_devices if device['device_id'] not in devices_to_remove]
                    if not updated_devices:
                        pipeline.delete(redis_key)
                    if len(updated_devices) != len(parsed_devices):
                        pipeline.hset(redis_key, mapping={"devices": json.dumps(updated_devices)})
            pipeline.execute()
        except Exception as e:
            raise

    def set_connection(self):
        if not self.connection or not self.connection.is_connected():
            self.connection = mysql.connector.connect(host=self.host,port=self.port,user=self.user,passwd=self.password,database=self.database)
        
        if self.redis_config:
            self.redis_connecion=get_redis_connection(host=self.redis_config.get('host'),port=self.redis_config.get('port'),
                                                      db=self.redis_config.get('db'),password=self.redis_config.get('password')
                                                      )
        
    def close_connection(self):
        self.connection.close()
        if self.redis_connecion:
            self.redis_connecion.close()
        
    def append_notification(self,notification_data, data_obj, service_name, status,is_success,total_notifications,failed_to_sent,total_clicks):
        """Append notification data to the list."""
        data = data_obj.get('data', {})
        notification_data.append((
            data.get('device',None),
            data.get('u_id'),
            data.get('uuid'),
            data.get('category'),
            service_name,
            status,
            is_success,total_notifications,failed_to_sent,total_clicks
    ))
    def log_notifications(self, service_result):
        cursor = self.connection.cursor()
        notification_data = []
        for data_obj in service_result.get('notif_data', []):
            self.append_notification(notification_data, data_obj, service_result.get('service', 'unknown'), "success",is_success=1,total_notifications=1,failed_to_sent=0,total_clicks=0)
        for data_obj in service_result.get('failed', []):
            self.append_notification(notification_data, data_obj, service_result.get('service', 'unknown'), data_obj.get('error', "unknown"),is_success=0,total_notifications=1,failed_to_sent=1,total_clicks=0)
        try:
            cursor.executemany(f"""INSERT INTO {self.notification_log_table} (device_id, user_id, uuid, category_id, service_name, status,is_success,total_notifications,failed_to_sent,total_clicks)
                                VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s,%s)""", notification_data)
            self.connection.commit()

        except Error as e:
            if e.errno == mysql.connector.errorcode.ER_NO_SUCH_TABLE:
                raise TableNotExistError(f"Table {self.device_token_table} doesn't exist and required columns are device_id, user_id, uuid, category_id, service_name, status ")
            else:
                raise
        finally:
            cursor.close()

    def update_invalid_device_tokens(self,invalid_tokens=None,device_with_invalid_tokens=None):
        if invalid_tokens:
            user_device_ids = []
            device_ids = []
            for sublist in invalid_tokens:
                for token in sublist:
                    if 'code' in token and token['code'] == 'NOT_FOUND':
                        user_device_ids.append({'user_id':token['data']['u_id'],'device_id':token['data']['device']})
                        device_ids.append(token['data']['device'])
        else:
            user_device_ids=device_with_invalid_tokens
            device_ids = [item['device_id'] for item in user_device_ids]

            
        if self.redis_connecion:
            self.update_invalid_tokens_in_redis(user_device_list=user_device_ids)
            
        if user_device_ids:
            cursor = self.connection.cursor()
            try:
                for i in range(0, len(device_ids), 100):
                    batch = device_ids[i:i + 100]

                cursor.execute(f"""UPDATE {self.device_token_table} SET invalid_token = 1,is_uninstalled = 1 WHERE id IN ({', '.join(['%s'] * len(batch))})""", batch)
                self.connection.commit()
            except Exception as e:
                raise
            finally:
                cursor.close()
                
    def log_multicast_notifications(self,message_data,service_name,total_notification,failed_to_sent):
        try:
            category_id=message_data.get('category',None)
            uuid=message_data.get('uuid',None)
            cursor=self.connection.cursor()
            cursor.execute(f"""INSERT INTO {self.notification_log_table} (device_id,uuid, category_id, service_name, status,is_success,total_notifications,failed_to_sent,total_clicks)
                                VALUES (%s, %s, %s, %s, %s, %s,%s,%s,%s)""", (None,uuid,category_id,service_name,"success",'1',total_notification,failed_to_sent,'0'))
            self.connection.commit()
            
        except Exception as e:
            raise
        finally:
            cursor.close()

    def update_uninstalled_tokens(self, tokens=None):
        """
        Sets is_uninstalled = 1 in user_device_info for the provided tokens.
        """
        if not tokens:
            return
    
        cursor = self.connection.cursor()
        try:
            for i in range(0, len(tokens), 100):
                batch = tokens[i:i+100]
                placeholders = ','.join(['%s'] * len(batch))
                cursor.execute(
                    f"""
                    UPDATE {self.device_token_table}
                    SET is_uninstalled = 1
                    WHERE device_token IN ({placeholders})
                    """,
                    batch
                )
            self.connection.commit()
        except Exception as e:
            raise
        finally:
            cursor.close()        