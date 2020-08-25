import json
import os
import zipfile
import click
import io
import pandas as pd

from nm import settings

from utils import api

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])


@click.group()
@click.version_option()
def cli():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def register():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def create():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def get():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def modify():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def update():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def delete():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def onboard():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def allocate():
    pass


@cli.group(context_settings=CONTEXT_SETTINGS)
def deallocate():
    pass


@create.command('nsst')
@click.argument('template_id', nargs=3)
@click.option('-n', '--nfvo', required=True)
def create_nss_template(template_id, nfvo):
    request_data = {'genericTemplates': list(template_id), 'nfvoType': [nfvo]}
    click.echo(request_data)
    response = api.create_nss_template(json.dumps(request_data))
    click.echo(response.json())
    if response.status_code == 201:
        click.echo('OperationSucceeded, NSST is combined.')
        click.echo('NSST Id: ' + response.json()['templateId'])
    else:
        click.echo('OperationFailed')


@get.command('nsst')
@click.argument('nss_template_id', required=False)
def get_nss_template(nss_template_id):
    if nss_template_id is None:
        response = api.get_nss_template_list()
    else:
        response = api.get_single_nss_template(nss_template_id)
    data = dict()
    data['templateId'] = list()
    data['description'] = list()
    data['nfvo'] = list()
    data['VNF'] = list()
    data['NSD'] = list()
    data['NRM'] = list()

    if response.status_code == 200:
        output = str
        if not response.json():
            data['templateId'].append('None')
            data['description'].append('None')
            data['nfvo'].append('None')
            data['VNF'].append('None')
            data['NSD'].append('None')
            data['NRM'].append('None')
            output = pd.DataFrame(data=data)
        else:
            data_obj = response.json()
            if type(data_obj) == list:
                for template in data_obj:
                    data['templateId'].append(template['templateId'])
                    data['description'].append(template['description'])
                    data['nfvo'].append(template['nfvoType'][0])
                    obj = {
                        'VNF': 'None',
                        'NSD': 'None',
                        'NRM': 'None'
                    }
                    for index in template['genericTemplates']:
                        obj[index['templateType']] = index['templateId']
                    data['VNF'].append(obj['VNF'])
                    data['NSD'].append(obj['NSD'])
                    data['NRM'].append(obj['NRM'])
                output = pd.DataFrame(data=data)
            else:
                data['templateId'].append(data_obj['templateId'])
                data['description'].append(data_obj['description'])
                data['nfvo'].append(data_obj['nfvoType'][0])
                obj = {
                    'VNF': 'None',
                    'NSD': 'None',
                    'NRM': 'None'
                }
                for index in data_obj['genericTemplates']:
                    obj[index] = data_obj['genericTemplates'][index][0]
                data['VNF'].append(obj['VNF'])
                data['NSD'].append(obj['NSD'])
                data['NRM'].append(obj['NRM'])
                output = pd.DataFrame(data=data)
        click.echo(output.to_string(index=False,
                                    columns=['templateId', 'description', 'nfvo',
                                             'VNF', 'NSD', 'NRM']))
    else:
        click.echo('OperationFailed')


@delete.command('nsst')
@click.argument('nss_template_id', required=True)
def delete_nss_template(nss_template_id):
    response = api.delete_nss_template(nss_template_id)
    if response.status_code == 204:
        click.echo("OperationSucceeded")
    else:
        click.echo('OperationFailed')


@create.command('template')
@click.option('-t', '--template-type', required=True,
              type=click.Choice(['VNF', 'NSD', 'NRM'], case_sensitive=False))
@click.option('-n', '--nfvo', required=True)
def create_template(template_type, nfvo):
    # if os.path.exists(os.path.join(os.getcwd(), nfvo)):
    #     click.echo('example_template directory is existed.')
    #     return

    request_data = {'templateType': template_type, 'nfvoType': nfvo}
    response = api.create_template(json.dumps(request_data))

    if response.status_code == 201:
        download = click.confirm('Do you want to download example?')
        if download:
            click.echo('Downloading...')
            download_obj = api.download_template(template_type)
            with zipfile.ZipFile(io.BytesIO(download_obj.content)) as zf:
                zf.extractall(path=os.path.join(os.getcwd(), template_type))
            click.echo('OperationSucceeded, template example created in this directory.')
        else:
            click.echo('OperationSucceeded')
        click.echo('Template Id: ' + response.json()['templateId'])
    else:
        click.echo('OperationFailed')


@onboard.command('template')
@click.argument('template_id')
@click.option('-f', '--folder', required=True, help='on board template folder')
def on_board_template(template_id, folder):
    if not os.path.exists(folder):
        click.echo('No such file or directory.')
        return
    response = api.get_single_template(template_id)
    template = response.json()
    if not template:
        click.echo('No such find Template Id')

    data = {'templateType': template['templateType'], 'nfvoType': template['nfvoType']}

    os.chdir(os.path.abspath(folder))

    with zipfile.ZipFile(os.path.basename(os.path.abspath(folder)) + '.zip',
                         mode='w') as template_zip:
        for root, folders, files in os.walk('.'):
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path.__contains__('git') and not file_path.__contains__('.zip'):
                    template_zip.write(file_path)
        template_zip.close()
        file_name = os.path.basename(os.getcwd() + '.zip')
        zipfile_path = os.path.join(os.getcwd(), os.path.basename(os.path.abspath(folder))) + '.zip'
        files = {'templateFile': (file_name, open(zipfile_path, 'rb').read(),
                          'application/zip', {'Expires': '0'})}
        response = api.on_board_template(template_id, files, data)

        if response.status_code == 204:
            click.echo('OperationSucceeded')
        else:
            click.echo(response.status_code)
            click.echo('OperationFailed')

        os.remove(zipfile_path)


@get.command('template')
@click.argument('template_id', required=False)
def get_template(template_id):
    if template_id is None:
        response = api.get_template_list()
    else:
        response = api.get_single_template(template_id)

    data = dict()
    data['templateId'] = list()
    data['nfvo'] = list()
    data['status'] = list()
    data['type'] = list()

    if response.status_code == 200:
        output = str()
        if not response.json():
            data['templateId'].append('None')
            data['nfvo'].append('None')
            data['status'].append('None')
            data['type'].append('None')
            output = pd.DataFrame(data=data)
        else:
            data_obj = response.json()
            if type(data_obj) == list:
                for template in data_obj:
                    data['templateId'].append(template['templateId'])
                    data['nfvo'].append(template['nfvoType'])
                    data['status'].append(template['operationStatus'])
                    data['type'].append(template['templateType'])
                    output = pd.DataFrame(data=data)
            else:
                data['templateId'].append(data_obj['templateId'])
                data['nfvo'].append(data_obj['nfvoType'])
                data['status'].append(data_obj['operationStatus'])
                data['type'].append(data_obj['templateType'])
                output = pd.DataFrame(data=data)
        click.echo(output.to_string(index=False,
                                    columns=['templateId', 'nfvo', 'status', 'type']))
    else:
        click.echo('OperationFailed')


@delete.command('template')
@click.argument('template_id', required=False)
def delete_template(template_id):
    response = api.delete_template(template_id)
    if response.status_code == 204:
        click.echo("OperationSucceeded")
    else:
        click.echo('OperationFailed')


@register.command('plugin')
@click.argument('name', required=True)
@click.option('-f', '--folder', required=True, help='Project file path')
def register_plugin(name, folder):
    data = {'name': name}

    os.chdir(os.path.abspath(folder))

    with zipfile.ZipFile(os.path.basename(os.path.abspath(folder)) + '.zip',
                         mode='w') as plugin_zip:
        for root, folders, files in os.walk('.'):
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path.__contains__('git') and not file_path.__contains__('.zip'):
                    plugin_zip.write(file_path)
        plugin_zip.close()
        file_name = os.path.basename(os.getcwd() + '.zip')
        zipfile_path = os.path.join(os.getcwd(), os.path.basename(os.path.abspath(folder))) + '.zip'
        files = {'pluginFile': (file_name, open(zipfile_path, 'rb').read(),
                                'application/zip', {'Expires': '0'})}
        response = api.register_service_mapping_plugin(data, files)

        if response.status_code == 201:
            click.echo('OperationSucceeded')
        else:
            click.echo('OperationFailed')

        os.remove(zipfile_path)


@get.command('plugin')
@click.argument('plugin_name', required=False)
def get_plugin(plugin_name):
    if plugin_name is None:
        plugin_name = ''
    response = api.get_service_mapping_plugin(plugin_name)
    data = dict()
    output = ''
    data['name'] = list()
    data['allocate_nssi'] = list()
    data['deallocate_nssi'] = list()

    if response.status_code == 200:
        for plugin in response.json():
            data['name'].append(plugin['name'])
            data['allocate_nssi'].append(plugin['allocate_nssi'])
            data['deallocate_nssi'].append(plugin['deallocate_nssi'])
            output = pd.DataFrame(data=data)
        click.echo(output.to_string(index=False,
                                    columns=['name', 'allocate_nssi', 'deallocate_nssi']))
    else:
        click.echo(response.json()['status'])


@update.command('plugin')
@click.argument('name')
@click.option('-f', '--folder', required=True, help='Project file path')
def update_plugin(name, folder):
    os.chdir(os.path.abspath(folder))
    data = {'name': name}
    with zipfile.ZipFile(os.path.basename(os.path.abspath(folder)) + '.zip',
                         mode='w') as plugin_zip:
        for root, folders, files in os.walk('.'):
            for file in files:
                file_path = os.path.join(root, file)
                if not file_path.__contains__('git') and not file_path.__contains__('.zip'):
                    plugin_zip.write(file_path)
        plugin_zip.close()
        file_name = os.path.basename(os.getcwd() + '.zip')
        zipfile_path = os.path.join(os.getcwd(), os.path.basename(os.path.abspath(folder))) + '.zip'
        files = {'pluginFile': (file_name, open(zipfile_path, 'rb').read(),
                                'application/zip', {'Expires': '0'})}
        response = api.update_service_mapping_plugin(data, files)

        if response.status_code == 200:
            click.echo('Update Success')

        os.remove(zipfile_path)


@delete.command('plugin')
@click.argument('plugin_name')
def delete_plugin(plugin_name):
    response = api.delete_service_mapping_plugin(plugin_name)
    click.echo(response.json()['status'])


@allocate.command('nssi')
@click.argument('nss_template_id', required=True)
def allocate_nssi(nss_template_id):

    response = api.get_single_nss_template(nss_template_id)
    if response.status_code == 200:
        choise = click.confirm('Do you want to Using exist Nssi?')
        if choise:
            using_exist = click.prompt('Nssi ID: ')
            click.echo('Modify Nssi {}...'.format(using_exist))
            data = {
                'attributeListIn': {
                    'nsstid': nss_template_id,
                    "using_existed": using_exist
                }
            }
            response = api.allocate_nssi(json.dumps(data))
            click.echo('OperationSucceeded')
        else:
            click.echo('Create Nssi...')
            data = {
                'attributeListIn': {
                    'nsstid': nss_template_id,
                    "using_existed": ""
                }
            }
            response = api.allocate_nssi(json.dumps(data))
            click.echo('OperationSucceeded')
            click.echo('Nssi ID: {}'.format(response.json()['nSSIId']))


@deallocate.command('nssi')
@click.argument('nss_instance_id', required=True)
def deallocate_nssi(nss_instance_id):
    click.echo('Delete Nssi...')
    response = api.deallocate_nssi(nss_instance_id)
    if response.status_code == 200:
        click.echo('OperationSucceeded')
    else:
        click.echo('OperationFailed')


@create.command('subscriptions')
@click.argument('nss_instance_id', required=True)
def create_subscriptions(nss_instance_id):
    import requests
    import json
    import random
    import time
    import base64
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
    response = requests.post(uri, data=json.dumps(data), headers=headers)
    if response.status_code == 201:
        click.echo("notification Id:", response.json()['data']['notificationId'])
        url = settings.Kafka_URL + "consumers/group"
        data = {
            "id": str(int(random.random()*100)),
            "format": "binary",
            "auto.offset.reset": "earliest",
            "auto.commit.enable": "false"
        }
        header = {"Content-Type": "application/vnd.kafka.v2+json"}
        consumers = requests.post(url=url, json=data, headers=header)
        click.echo("Listen Kafka:")
        click.echo(consumers.json()['base_uri'] + "/subscription")
        data = {"topics": ["alarm"]}
        subscribe = requests.post(url=consumers.json()['base_uri'] + "/subscription",
                                  json=data, headers=header)
        header = {"Content-Type": "application/vnd.kafka.json.v2+json"}

        while 1:
            record = requests.get(url=consumers.json()['base_uri'] + "/records", headers=header)
            click.echo(record.json())
            if record.json():
                click.echo(base64.b64decode(record.json()[-1]['value']).decode())
                break
            time.sleep(1)
        click.echo('OperationSucceeded')
    else:
        click.echo('OperationFailed')


@delete.command('subscriptions')
@click.argument('notification_id', required=True)
def delete_subscriptions(notification_id):
    import requests
    uri = settings.NM_URL + "subscriptions/{}/".format(notification_id)
    response = requests.delete(uri)
    if response.status_code == 201:
        click.echo('OperationSucceeded')
    else:
        click.echo('OperationFailed')