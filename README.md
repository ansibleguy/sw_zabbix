# Ansible Role - Zabbix deployment
Ansible Role to setup and manage Zabbix Servers, Proxies and Agents.

This roles target is it to **configure the Zabbix components foundational**.

You will need to manage the zabbix-agent integration(s) into your systems on your own! (_per example: adding MySQL users and client-config to monitor its status_)


**Tested:**
* Debian 11


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

* **Warning:** The target server/os for the Zabbix server-component should host only this service! Else you might possibly run into configuration/compatibility issues! 


* **Note:** this role currently only supports debian-based systems


* **Info:** We chose to use Nginx and Apache2 so that the configuration managed by Zabbix (_Apache2_) and the one we manage using this role (_Nginx_) can co-exist safely. 
This may be important in the future.
Else incompatibilities would break future setups if Zabbix changes their config-handling.


* **Info:** Zabbix-Server apache2 config is stored at: /etc/zabbix/apache.conf (_default_)


* **Info:** The default login for the Zabbix server is: Admin/zabbix


* **Info:** If the server installation fails for some reason you might want to uninstall the 'zabbix-server-mysql' package before re-running this role!


## Setup
For this role to work - you must install its dependencies first:

```
ansible-galaxy install -r requirements.yml
```

## Usage

### Config

Define the zabbix dictionary as needed.

Example for a zabbix server:
```yaml
zabbix: 
  manage:
    agent: true
    server: true
  
  server:
    nginx:  # configure the webserver settings => see: https://github.com/ansibleguy/infra_nginx
      domain: 'zabbix.template.ansibleguy.net'
      aliases: ['zbx.template.ansibleguy.net']
  
      ssl:
        mode: 'letsencrypt'  # or selfsigned
        #  if you use 'selfsigned':
        #    cert:
        #      cn: 'Zabbix Server'
        #      org: 'AnsibleGuy'
        #      email: 'zabbix@template.ansibleguy.net'


    tls_cert_copy: 'server.crt'  # will be copied from the roles 'files/certs' directory to the target system
    tls_key_copy: 'server.key'  # must be configured for server-authentication
    tls_ca_copy: 'ca.crt'
    settings:
      ListenIP: '172.16.0.54'
      ProxyDataFrequency: 10
      ProxyConfigFrequency: 600
      SSHKeyLocation: '/etc/zabbix/private/id_rsa'

  agent:
    tls_psk: !vault ...

    settings:
      Server: '172.16.0.54'
      TLSPSKIdentity: 'RandomIdentity_O(73odfs23'
```

Example for a zabbix proxy:
```yaml
zabbix:
  manage:
    agent: true
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
  
  agent:
    tls_psk: !vault ...  # plain key may only contain hexdigits (0-9 & a-f)

    settings:
      Server: '172.18.15.7'
      ListenIP: '172.18.15.7'
```

Example for a zabbix agent:
```yaml
zabbix:
  agent:
    tls_psk: !vault ...  # plain key may only contain hexdigits (0-9 & a-f)

    settings:
      Server: '172.16.0.54'
      TLSPSKIdentity: 'RandomIdentity_lUF(o3s4kjh3o'
      ListenIP: '172.16.0.80'
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
