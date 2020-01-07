# free5gmano CLI
## Dependencies
The following packages are required:

* git
* python3
* pip3
## Installation Guide
```
git clone https://github.com/free5gmano/free5gmano-cli.git
cd free5gmano-cli
pip3 install -e .
```
## User Guide
Setup free5gmano host and port
```
cd free5gmano-cli
vim setting.py
```
1. create NSST
```
nmctl create nsst -n <nfvo_name> <VNF template_id> <NSD template_id>
```
2. get NSST
```
nmctl get nsst
nmctl get nsst <NSST template_id>
```
3. delete NSST list
```
nmctl delete nsst <NSST template_id>
```
4. create template
```
nmctl create template -n <nfvo_name> -t <VNF or NSD>
```
5. onboard template
```
nmctl onboard template <template_id> -f <your template folder>
```
6. get template
```
nmctl get template
nmctl get template <template_id>
```
7. delete template
```
nmctl delete template <template_id>
```
8. register plugin
```
nmctl register plugin <plugin_name> -f <your plugin folder>
```
9. get plugin
```
nmctl get plugin
nmctl get plugin <plugin_name>
```
10. update_plugin
```
nmctl update plugin <plugin_name> -f <your plugin folder>
```
11. delete_plugin
```
nmctl delete plugin <plugin_name>
```
12. Allocate NSSI
```
nmctl allocate nssi <NSST template_id>
```