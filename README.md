# free5gmano CLI
## Dependencies
The following packages are required:

* git
* python3
* pip3
* service-mapping-plugin-framework
### Install service-mapping-plugin-framework
Please refer to [service-mapping-plugin-framework](https://github.com/free5gmano/service-mapping-plugin-framework) Installation Guide to install service-mapping-plugin-framework.
## Installation Guide
```
git clone https://github.com/free5gmano/free5gmano-cli.git
cd free5gmano-cli
git checkout v2.0.0
pip3 install -e .
```
## User Guide
Setup free5gmano host and port
```
cd free5gmano-cli/nm
vim setting.py
```
1. register plugin
```
nmctl register plugin <plugin_name> -f <your plugin folder>
```

2. create template
```
nmctl create template -n <plugin_name> -t <VNF or NSD or NRM>
```

3. onboard template
```
nmctl onboard template <template_id> -f <your template folder>
```

4. create NSST
```
nmctl create nsst -n <plugin_name> <VNF template_id> <NSD template_id> <NRM template_id>
```

5. Allocate NSSI
```
nmctl allocate nssi <NSST template_id>
```

Other Operation
1. get plugin
```
nmctl get plugin
nmctl get plugin <plugin_name>
```

2. update plugin
```
nmctl update plugin <plugin_name> -f <your plugin folder>
```

3. delete plugin
```
nmctl delete plugin <plugin_name>
```

4. get template
```
nmctl get template
nmctl get template <template_id>
```

5. delete template
```
nmctl delete template <template_id>
```

6. get NSST
```
nmctl get nsst
nmctl get nsst <NSST template_id>
```

7. delete NSST
```
nmctl delete nsst <NSST template_id>
```

8. subscribe NSSI (Fault Management)
```
nmctl create subscriptions <NSS_INSTANCE_ID>
```

8. unsubscribe NSSI (Fault Management)
```
nmctl delete subscriptions <NSS_INSTANCE_ID>
```
