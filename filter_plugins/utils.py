class FilterModule(object):

    def filters(self):
        return {
            "zabbix_psk_hex": self.zabbix_psk_hex,
        }

    @staticmethod
    def zabbix_psk_hex(key: str) -> str:
        try:
            # checking if is in hex-fomat
            _ = int(key, 16)
            return key

        except ValueError:
            return key.encode().hex()
