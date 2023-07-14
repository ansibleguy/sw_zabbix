[![Zabbix](https://assets.zabbix.com/img/logo/zabbix_logo_313x82.png)](https://www.zabbix.com)

# Ansible Role - Zabbix deployment
Ansible Role to deploy Zabbix Server/Proxy/Agent components on a linux server.

The roles target is it to **configure the Zabbix components foundational**.

You will need to manage the zabbix-agent integration(s) into your systems on your own! (_per example: adding MySQL users and client-config to monitor its status_)

[![Molecule Test Status](https://badges.ansibleguy.net/sw_zabbix.molecule.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/molecule.sh.j2)
[![YamlLint Test Status](https://badges.ansibleguy.net/sw_zabbix.yamllint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/yamllint.sh.j2)
[![PyLint Test Status](https://badges.ansibleguy.net/sw_zabbix.pylint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/pylint.sh.j2)
[![Ansible-Lint Test Status](https://badges.ansibleguy.net/sw_zabbix.ansiblelint.svg)](https://github.com/ansibleguy/_meta_cicd/blob/latest/templates/usr/local/bin/cicd/ansiblelint.sh.j2)
[![Ansible Galaxy](https://img.shields.io/ansible/role/62784)](https://galaxy.ansible.com/ansibleguy/sw_zabbix)
[![Ansible Galaxy Downloads](https://img.shields.io/badge/dynamic/json?color=blueviolet&label=Galaxy%20Downloads&query=%24.download_count&url=https%3A%2F%2Fgalaxy.ansible.com%2Fapi%2Fv1%2Froles%2F62784%2F%3Fformat%3Djson)](https://galaxy.ansible.com/ansibleguy/sw_zabbix)

**Tested:**
* Debian 11

## Install

```bash
ansible-galaxy install ansibleguy.sw_zabbix

# or to custom role-path
ansible-galaxy install ansibleguy.sw_zabbix --roles-path ./roles

# install dependencies
ansible-galaxy install -r requirements.yml
```

## Functionality

* **Package installation**
  * Zabbix server
    * Dependencies (_php, ..._)
    * Apache2 => configured by Zabbix-Server package
    * Nginx => using [THIS Role](https://github.com/ansibleguy/infra_nginx)
    * MariaDB => using [THIS Role](https://github.com/ansibleguy/infra_mariadb)

  * Zabbix proxy
    * MariaDB => using [THIS Role](https://github.com/ansibleguy/infra_mariadb)

  * Zabbix agent


* **Configuration**
  * **Features**:
    * Copying your..
      * scripts (_agent scripts, externalscripts, alertscripts_)
      * userparameters
      * certificates

    * .. to the target system; just put them in the prepared 'files' directory of this role!
   
  * **Default config**:
    * Using ansible-hostnames as Zabbix hostnames
    * Traffic encryption using PSK
    * Using a Self-Signed certificate for the Zabbix server
    * not running as root
    * Webserver best-practices => see: [THIS Role](https://github.com/ansibleguy/infra_nginx)
    * Agent/Proxy/Server listening on all interfaces

  * **Default opt-ins**:
    * Logging to syslog
    * Zabbix agent installation
    * MariaDB setup for Zabbix proxy and server
    * Nginx setup for Zabbix server

  * **Default opt-outs**:
    * Zabbix proxy and server installation
    * Settings: UnsafeUserParameters, EnableRemoteCommands

  * **Security**:
    * Traffic encryption per PSK or Certificate is **ENFORCED**

## Info

* **Note:** The lowest version supported is 6.0!


* **Warning:** The target server/os for the Zabbix server-component should host only this service! Else you might possibly run into configuration/compatibility issues!


* **Note:** this role currently only supports debian-based systems


* **Info:** We chose to use Nginx and Apache2 so that the configuration managed by Zabbix (_Apache2_) and the one we manage using this role (_Nginx_) can co-exist safely.
This may be important in the future.
Else incompatibilities would break future setups if Zabbix changes their config-handling.


* **Info:** Zabbix-Server apache2 config is stored at: /etc/zabbix/apache.conf (_default_)


* **Info:** The default login for the Zabbix server is: **User = Admin | Password = zabbix**


* **Info:** If the server installation fails for some reason you might want to uninstall the 'zabbix-server-mysql' package before re-running this role!


* **Warning:** Not every setting/variable you provide will be checked for validity. Bad config might break the role!


* **Info:** If you use PSKs to encrypt your traffic - it must be at least 32 hex-digits long!


## Usage

### Config

Define the zabbix dictionary as needed.

Example for a zabbix server:
```yaml
zabbix:
  manage:
    agent2: true  # activated by default
    server: true
 
  server:
    nginx:  # configure the webserver settings => see: https://github.com/ansibleguy/infra_nginx
      domain: 'zabbix.template.ansibleguy.net'
      aliases: ['zbx.template.ansibleguy.net']
 
      ssl:
        mode: 'letsencrypt'  # or selfsigned/ca
        #  if you use 'selfsigned' or 'ca':
        #    cert:
        #      cn: 'Zabbix Server'
        #      org: 'AnsibleGuy'
        #      email: 'zabbix@template.ansibleguy.net'
      letsencrypt:
        email: 'zabbix@template.ansibleguy.net'

    tls_cert_copy: 'server.crt'  # will be copied from the roles 'files/certs' directory to the target system
    tls_key_copy: 'server.key'  # must be configured for server-authentication
    tls_ca_copy: 'ca.crt'
    settings:
      ListenIP: '172.16.0.54'
      ProxyDataFrequency: 10
      ProxyConfigFrequency: 600
      SSHKeyLocation: '/etc/zabbix/private/id_rsa'

  agent2:
    tls_psk: !vault ...

    settings:
      Server: '172.16.0.54'
      TLSPSKIdentity: 'RandomIdentity_O(73odfs23'
```

Example for a zabbix proxy:
```yaml
zabbix:
  manage:
    agent2: true
    proxy: true
 
  proxy:
    tls_cert_copy: 'proxy01.crt'  # will be copied from the roles 'files/certs' directory to the target system
    tls_key_copy: 'proxy01.key'  # must be configured for client-authentication
    tls_ca_copy: 'ca.crt'

    settings:
      Server: '172.16.0.54'
      TLSConnect: 'cert'
      TLSAccept: 'cert'
      ConfigFrequency: 600
      ListenIP: '172.18.15.7'
 
  agent2:
    tls_psk: !vault ...  # plain key may only contain hexdigits (0-9 & a-f)

    settings:
      Server: '172.18.15.7'
      ListenIP: '172.18.15.7'
```

Example for zabbix agent V2:
```yaml
zabbix:
  # agent version 2 is enabled by default
  #  manage:
  #    agent2: true
  
  agent2:
    tls_psk: !vault ...  # plain key may only contain hexdigits (0-9 & a-f)

    settings:
      Server: '172.16.0.54'
      TLSPSKIdentity: 'RandomIdentity_lUF(o3s4kjh3o'
      ListenIP: '172.16.0.80'
```

Example for the older zabbix agent:
```yaml
zabbix:
  manage:
    agent1: true

  agent1:
    tls_psk: !vault ...  # plain key may only contain hexdigits (0-9 & a-f)

    settings:
      Server: '172.16.0.54'
      TLSPSKIdentity: 'RandomIdentity_lUF(o3s4kjh3o'
      ListenIP: '172.16.0.80'
```

Example - if you don't want to use the ansible-managed nginx web-proxy:
```yaml
zabbix:
  manage:
    server: true
    webserver: false  # <=
 
  server:
    ...
    settings:
      ...
```

You might want to use 'ansible-vault' to encrypt your passwords:
```bash
ansible-vault encrypt_string
```

### Execution

Run the playbook:
```bash
ansible-playbook -K -D -i inventory/hosts.yml playbook.yml --ask-vault-pass
```

There are also some useful **tags** available:
* config
* install
* uninstall
* agent
* proxy
* server
