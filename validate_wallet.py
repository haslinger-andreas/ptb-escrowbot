import re
from rpcHandler import getLtc_Rpc, getBtc_Rpc

BTC_PATTERN = r'^([13][a-km-zA-HJ-NP-Z1-9]{25,34}|bc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{39,87})$'
LTC_PATTERN = r'^(ltc1[qpzry9x8gf2tvdw0s3jn54khce6mua7l]{38,}$|[LM][1-9A-HJ-NP-Za-km-z]{26,33}$)'
REGTEST_PATTERN_BTC = r'^(bcrt1[ac-hj-np-z02-9]{25,39}|[mn][1-9A-HJ-NP-Za-km-z]{26,35}|2[1-9A-HJ-NP-Za-km-z]{25,34})$'
REGTEST_PATTERN_LTC = r'^(rltc1[ac-hj-np-z02-9]{25,39}|[mn][1-9A-HJ-NP-Za-km-z]{26,35}|2[1-9A-HJ-NP-Za-km-z]{25,34})$'

async def check_wallet_address_fast(address):
    if re.match(BTC_PATTERN, address) or re.match(REGTEST_PATTERN_BTC, address):
        return 'BTC'
    elif re.match(LTC_PATTERN, address) or re.match(REGTEST_PATTERN_LTC, address):
       return 'LTC'
    else:
        return 'INVALID'

async def check_wallet_address_slow(address):
    if re.match(BTC_PATTERN, address) or re.match(REGTEST_PATTERN_BTC, address):
        rpc = await getBtc_Rpc()
        check = await rpc.validateaddress(address)
        if check['isvalid']:
            return 'BTC'
    elif re.match(LTC_PATTERN, address) or re.match(REGTEST_PATTERN_LTC, address):
        rpc = await getLtc_Rpc()
        check = await rpc.validateaddress(address)
        if check['isvalid']:
            return 'LTC'
    else:
        return 'INVALID'
