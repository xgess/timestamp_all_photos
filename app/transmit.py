from binascii import hexlify

from btctxstore import BtcTxStore


def send_to_bitcoin(wif, change_address, payload: bytes, is_testnet=True, is_dryrun=True, fee=10000):
    if is_dryrun:
        print("*** DRY RUN ***")
    else:
        print("*** LIVE ***")
    if is_testnet:
        print("*** TEST NET ***")
    else:
        print("*** MAIN NET ***")

    api = BtcTxStore(testnet=is_testnet, dryrun=is_dryrun)
    data = hexlify(payload)
    transaction_id = api.store_nulldata(
        hexdata=data,
        wifs=[wif],
        change_address=change_address,
        fee=fee
    )
    return transaction_id


def get_from_bitcoin(transaction_id, is_testnet=True):
    api = BtcTxStore(testnet=is_testnet, dryrun=False)
    return api.retrieve_nulldata(transaction_id)
