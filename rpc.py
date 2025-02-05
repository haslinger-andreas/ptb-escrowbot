import base64
import logging
import json
from decimal import Decimal
import urllib.parse as urlparse
from aiohttp import ClientSession
from aiohttp_socks import ProxyConnector
from config import PROXY_IP, PROXY_PORT

log = logging.getLogger("BitcoinCoreClient")

proxy_url = f"socks5://{PROXY_IP}:{PROXY_PORT}"

class JSONRPCException(Exception):
    def __init__(self, rpc_error):
        parent_args = []
        try:
            parent_args.append(rpc_error['message'])
        except:
            pass
        Exception.__init__(self, *parent_args)
        self.error = rpc_error
        self.code = rpc_error['code'] if 'code' in rpc_error else None
        self.message = rpc_error['message'] if 'message' in rpc_error else None

class BitcoinCoreClient(object):
    def __init__(self, rpc_url: str, service_name=None, wallet_name=None):
        if wallet_name:
            self.__service_url = f"{rpc_url}/wallet/{wallet_name}"
        else:
            self.__service_url = rpc_url
        self.__service_name = service_name
        self.__url = urlparse.urlparse(rpc_url)
        self.__id_count = 0

        self.__proxy_connector = ProxyConnector.from_url(proxy_url)

        (user, passwd) = (self.__url.username, self.__url.password)
        try:
            user = user.encode('utf8')
        except AttributeError:
            pass
        try:
            passwd = passwd.encode('utf8')
        except AttributeError:
            pass
        authpair = user + b':' + passwd
        self.__auth_header = b'Basic ' + base64.b64encode(authpair)

    def __getattr__(self, name):
        if name.startswith('__') and name.endswith('__'):
            raise AttributeError
        if self.__service_name is not None:
            name = f"{self.__service_name}.{name}"
        return BitcoinCoreClient(self.__service_url, name)

    async def __call__(self, *args):
        self.__id_count += 1
        postdata = json.dumps({'method': self.__service_name,
                               'params': args,
                               'id': self.__id_count}, ensure_ascii=False, default=str)

        try:
            async with ClientSession(connector=self.__proxy_connector) as session:
                resp = await session.post(url=self.__service_url, data=postdata,)
                json_data = await resp.read()
                json_resp = json.loads(json_data, parse_float=Decimal)
                if json_resp['error']:
                    log.debug(json_resp)
                    raise JSONRPCException(json_resp['error'])

                return json_resp['result']
        except Exception as e:
            log.error("Error during RPC call", exc_info=True)
            logging.error("RPC call failed: %s", e)
            return None
