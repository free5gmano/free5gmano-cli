import uuid

import requests
import random
import time
import base64

from nm.nmctl import settings

nm_url = settings.NM_URL + 'ObjectManagement/{0}/{1}/{2}'
service_mapping_url = settings.NM_URL + '{0}/{1}/{2}'
template_url = settings.NM_URL + '{0}/{1}/{2}'
headers = {'Content-Type': 'application/json'}
zip_headers = {
    'Accept': "application/json,application/zip",
    'accept-encoding': "gzip, deflate"
}


def allocate_nssi(data):
    allocate_nssi_url = nm_url.format('NSS', 'SliceProfiles', '')
    return requests.post(allocate_nssi_url, data=data, headers=headers)


def deallocate_nssi(nss_instance_id):
    deallocate_nssi_url = nm_url.format('NSS', 'SliceProfiles', nss_instance_id)
    return requests.delete(deallocate_nssi_url, headers=headers)


def create_moi(model_name, data):
    create_moi_url = nm_url.format(model_name, uuid.uuid4().__str__())
    return requests.put(create_moi_url, data=data, headers=headers)


def get_moi_attributes(model_name, identify, scope_type, scope_level, _filter):
    get_moi_url = nm_url.format(model_name, identify)
    scope = '["' + scope_type + '",' + str(get_scope_level(scope_type, scope_level)) + ']'
    params = {'scope': scope, 'filter': _filter}
    return requests.get(get_moi_url, params=params, headers=headers)


def modify_moi_attributes(model_name, identify, scope_type, scope_level, filter, data):
    modify_moi_url = nm_url.format(model_name, identify)
    scope = '["' + scope_type + '",' + str(get_scope_level(scope_type, scope_level)) + ']'
    params = {'scope': scope, 'filter': filter}
    return requests.patch(modify_moi_url, data=data, params=params, headers=headers)


def delete_moi(model_name, identify, scope_type, scope_level, filter):
    delete_moi_url = nm_url.format(model_name, identify)
    scope = '["' + scope_type + '",' + str(get_scope_level(scope_type, scope_level)) + ']'
    params = {'scope': scope, 'filter': filter}
    return requests.delete(delete_moi_url, params=params, headers=headers)


def register_service_mapping_plugin(data, files):
    register_plugin_url = service_mapping_url.format('plugin', 'management', '')
    return requests.post(register_plugin_url, files=files, data=data, headers=zip_headers)


def get_service_mapping_plugin(name):
    register_plugin_url = service_mapping_url.format('plugin', 'management', name)
    return requests.get(register_plugin_url)


def update_service_mapping_plugin(data, files):
    register_plugin_url = service_mapping_url.format('plugin', 'management', data['name'] + "/")
    return requests.patch(register_plugin_url, files=files, data=data, headers=zip_headers)


def delete_service_mapping_plugin(name):
    register_plugin_url = service_mapping_url.format('plugin', 'management', name + "/")
    return requests.delete(register_plugin_url, headers=headers)


def create_nss_template(data):
    create_template_url = template_url.format('ObjectManagement', 'SliceTemplate', '')
    return requests.post(create_template_url, data=data, headers=headers)


def get_nss_template_list():
    get_template_url = template_url.format('ObjectManagement', 'SliceTemplate', '')
    return requests.get(get_template_url, headers=headers)


def get_single_nss_template(nss_template_id):
    get_template_url = template_url.format('ObjectManagement', 'SliceTemplate',
                                           nss_template_id + '/')
    return requests.get(get_template_url, headers=headers)


def delete_nss_template(template_id):
    delete_template_url = template_url.format('ObjectManagement', 'SliceTemplate',
                                              template_id + '/')
    return requests.delete(delete_template_url, headers=headers)


def create_template(data):
    create_template_url = template_url.format('ObjectManagement', 'GenericTemplate', '')
    return requests.post(create_template_url, data=data, headers=headers)


def download_template(template_type,example_type):
    download_template_url = template_url.format('ObjectManagement', 'GenericTemplate',
                                                'example_download/{}/{}/'.format(example_type,template_type))
    return requests.get(download_template_url, headers=headers)


def on_board_template(template_id, files, data):
    on_board_template_url = template_url.format('ObjectManagement', 'GenericTemplate',
                                                template_id + '/')
    return requests.put(on_board_template_url, files=files, data=data, headers=zip_headers)


def get_template_list():
    get_template_url = template_url.format('ObjectManagement', 'GenericTemplate', '')
    return requests.get(get_template_url, headers=headers)


def get_single_template(template_id):
    get_template_url = template_url.format('ObjectManagement', 'GenericTemplate', template_id + '/')
    return requests.get(get_template_url, headers=headers)


def delete_template(template_id):
    delete_template_url = template_url.format('ObjectManagement', 'GenericTemplate',
                                              template_id)
    return requests.delete(delete_template_url, headers=headers)


def get_scope_level(level_selection, level):
    if level_selection == 'BASE_ONLY':
        return 0
    elif level_selection == 'BASE_NTH_LEVEL':
        return level
    elif level_selection == 'BASE_SUBTREE':
        return level + 1
    elif level_selection == 'BASE_ALL':
        return 10


def create_fm_subscriptions(nss_instance_id):
    uri = settings.NM_URL + "subscriptions/"
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    data = {
        "filter": {
        "nsInstanceSubscriptionFilter": {
            "nSSIId": [
                nss_instance_id
                ]
            }
        },
        "callbackUri": settings.Kafka_URL + "topics/fault_alarm/",
        "timeTick": 1
    }
    return requests.post(uri, data=json.dumps(data), headers=headers)


def create_consumers():
    url = settings.Kafka_URL + "consumers/group"
    data = {
        "id": str(int(random.random()*100)),
        "format": "binary",
        "auto.offset.reset": "earliest",
        "auto.commit.enable": "false"
        }
    return requests.post(url=url, json=data, headers=kafka_header)


def create_topic(url,data):
    data = {"topics": ["fault_alarm"]}
    return requests.post(url=url,json=data, headers=kafka_header)


def get_record(url):
    header = {"Content-Type": "application/vnd.kafka.json.v2+json"}
    return requests.get(url=url, headers=header)