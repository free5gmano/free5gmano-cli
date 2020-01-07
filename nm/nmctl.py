import json
import os
import socket
import urllib.request
import zipfile

import click
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
@click.argument('template_id', nargs=2)
@click.option('-n', '--nfvo', required=True)
def create_nss_template(template_id, nfvo):
    request_data = {'reference': list(template_id), 'nfvo': nfvo}
    response = api.create_nss_template(json.dumps(request_data))

    if response.status_code == 200:
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

    if response.status_code == 200:
        output = str

        for template in response.json():
            data['templateId'].append(template['templateId'])
            data['description'].append(template['description'])
            data['nfvo'].append(template['nfvo'])
            data['VNF'].append(template['reference']['VNF'][0])
            data['NSD'].append(template['reference']['NSD'][0])
            output = pd.DataFrame(data=data)
        click.echo(output.to_string(index=False,
                                    columns=['templateId', 'description', 'nfvo', 'VNF', 'NSD']))
    else:
        click.echo('OperationFailed')


@delete.command('nsst')
@click.argument('nss_template_id', required=True)
def delete_nss_template(nss_template_id):
    response = api.delete_nss_template(nss_template_id)
    if response.status_code == 200:
        click.echo("OperationSucceeded")
    else:
        click.echo('OperationFailed')


@create.command('template')
@click.option('-t', '--template-type', required=True,
              type=click.Choice(['VNF', 'NSD'], case_sensitive=False))
@click.option('-n', '--nfvo', required=True)
def create_template(template_type, nfvo):
    if os.path.exists(os.path.join(os.getcwd(), nfvo)):
        click.echo('example_template directory is existed.')
        return

    request_data = {'type': template_type, 'nfvo': nfvo}
    response = api.create_template(json.dumps(request_data))

    if response.status_code == 200:
        download = click.confirm('Do you want to download example?')
        if download:
            click.echo('Downloading...')
            urllib.request.urlretrieve(response.json()['download_link'],
                                       filename=os.path.join(os.getcwd(), template_type + '.zip'))
            with zipfile.ZipFile(os.path.join(os.getcwd(), template_type + '.zip')) as zf:
                zf.extractall(path=os.path.join(os.getcwd(), template_type))
                os.remove(os.path.join(os.getcwd(), template_type + '.zip'))
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
        files = {'file': (file_name, open(zipfile_path, 'rb').read(),
                          'application/zip', {'Expires': '0'})}
        response = api.on_board_template(template_id, files)

        if response.status_code == 200:
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
        output = str

        for template in response.json():
            data['templateId'].append(template['templateId'])
            data['nfvo'].append(template['nfvo'])
            data['status'].append(template['status'])
            data['type'].append(template['type'])
            output = pd.DataFrame(data=data)
        click.echo(output.to_string(index=False,
                                    columns=['templateId', 'nfvo', 'status', 'type']))
    else:
        click.echo('OperationFailed')


@delete.command('template')
@click.argument('template_id', required=False)
def delete_template(template_id):
    response = api.delete_template(template_id)
    if response.status_code == 200:
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
        files = {'file': (file_name, open(zipfile_path, 'rb').read(),
                          'application/zip', {'Expires': '0'})}
        response = api.register_service_mapping_plugin(data, files)

        if response.status_code == 200:
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

    if response.json()['status'] == 'Succeed':
        for plugin in response.json()['plugin_list']:
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
        files = {'file': (file_name, open(zipfile_path, 'rb').read(),
                          'application/zip', {'Expires': '0'})}
        response = api.update_service_mapping_plugin(name, files)

        click.echo(response.json()['status'])

        os.remove(zipfile_path)


@delete.command('plugin')
@click.argument('plugin_name')
def delete_plugin(plugin_name):
    response = api.delete_service_mapping_plugin(plugin_name)
    click.echo(response.json()['status'])


@allocate.command('nssi')
@click.argument('nsst_template_id')
def allocate_nssi(nsst_template_id):
    data = {
        'attributeListIn': {
            'template_id': nsst_template_id
        }
    }

    response = api.allocate_nssi(json.dumps(data))
    click.echo()

    if response.status_code == 200:
        click.echo(response.json()['status'])
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect((settings.NM_HOST, 8888))

            while True:
                response = client.recv(4096)
                if response.decode() == '':
                    break
                else:
                    click.echo(response.decode().strip('\n'))
            client.close()
        except TimeoutError:
            click.echo('Request Timeout')
        except ConnectionResetError:
            click.echo()
    elif response.status_code == 400:
        click.echo('OperationFailed (request data error)')
    elif response.status_code == 500:
        click.echo('Internal Server error')
    else:
        click.echo('OperationFailed')
