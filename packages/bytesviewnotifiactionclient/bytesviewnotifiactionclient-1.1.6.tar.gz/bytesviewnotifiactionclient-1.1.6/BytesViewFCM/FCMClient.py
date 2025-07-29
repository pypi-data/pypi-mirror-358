import firebase_admin
from firebase_admin import credentials, messaging
import json

class FCMClient:

    _initialized_apps = {}     
    def create_fcm_message(self, device_token:str, title:str, body:str, image:str, data:dict):
        return messaging.Message(
            token=device_token,
            notification=messaging.Notification(
                title=title, body=body, image=image
            ),
            data=data
        )
    
    def create_multicast_message(self,device_tokens:list,title:str,body:str,image,data:dict):
        return messaging.MulticastMessage(
        notification=messaging.Notification(
            title=title,
            body=body,
            image=image
        ),
        data=data,
        tokens=device_tokens
    )
        
    def fcm_send(self, app_name:str, credential:json, message:messaging.Message):
        if app_name not in FCMClient._initialized_apps:
            FCMClient._initialized_apps[app_name] = firebase_admin.initialize_app(credentials.Certificate(credential))
        response = messaging.send(message, app=FCMClient._initialized_apps[app_name])
        return response

    def fcm_bulk_send(self, app_name:str, credential:json, batch_of_message:list):
        service_delivery_result={"service":"fcm","notif_data":[],"failed":[]}
        if app_name not in FCMClient._initialized_apps:
            FCMClient._initialized_apps[app_name] = firebase_admin.initialize_app(credentials.Certificate(credential))
        service_response = messaging.send_each(batch_of_message, app=FCMClient._initialized_apps[app_name])
        for idx, resp in enumerate(service_response.responses):
                if not resp.success :
                    service_delivery_result['failed'].append({"data":batch_of_message[idx].data,"error":resp.exception.args[0],"code":resp.exception.code})
                else:
                    service_delivery_result['notif_data'].append({"data":batch_of_message[idx].data})
        return service_delivery_result
    
    def send_multicast(self,app_name:str,credential:json,message):
        invalid_tokens=[]
        uninstalled_tokens=[]
        if app_name not in FCMClient._initialized_apps:
            FCMClient._initialized_apps[app_name] = firebase_admin.initialize_app(credentials.Certificate(credential))
        response = messaging.send_each_for_multicast(message, app=FCMClient._initialized_apps[app_name])
        for idx, res in enumerate(response.responses):
            if not res.success:
                err_msg = str(res.exception)
                invalid_tokens.append(message.tokens[idx])
                if "Requested entity was not found" in err_msg:
                    uninstalled_tokens.append(message.tokens[idx])
        return invalid_tokens,uninstalled_tokens

        
        