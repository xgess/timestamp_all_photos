# BTC Apple Photos Timestamper

### WHAT
Pull all of your photos out of the Apple Photos app, hash them into a merkle tree, and put the root into Bitcoin.

### WHY
Ostensibly so you can prove later that you have an undoctored photo that's been provably timestamped before someone else's version of the same. Actually, it's for funzies. I was expecting to do some (but hopefully not all) of the bitcoin-y side of the work, but then I found `btctxstore`. So I gave that a little bit of love and used it instead. Its underlying dependency, PyCoin, does not appear to support segwit addresses, and I didn't want to open up that can of worms just yet. So, thank goodness for Bitcoin's culture of backwards compatibility. Also, I wanted to play around with Click and Pipfile, both of which I'm totally loving.

### RUN IT
First things first, you need to install this into a local Python3.6 environment. I'm loving on pipenv right now, so use that! Or whatever you want.

There's a bunch of shell commands under `timestamper`. If you're feeling really brave (and I don't think I'd recommend that), you can do the whole shebang in a single go:

```shell
timestamper end_to_end \
    --library=/Users/<yourname>/Pictures/Photos Library.photoslibrary \
    --change_address=<an address you control> \
    --live \
    --mainnet
```
You'll be prompted for your private key in Wallet-Import-Format (with your typing hidden) to lookup your UTXOs and to sign the transaction.

You can also do it in a few steps to watch the process and inspect the temporary files (saved in ./tmp).
1. Inspect your photos library to get a list of all of the photo files to include in the merkle tree.
```shell
timestamper import_photos --library=/Users/<yourname>/Pictures/Photos Library.photoslibrary
```
2. Get the Sha256 hash of each of those photos. This is the longest running step. I thought I'd have to parallelize it, but it really wasn't slow enough to warrant it for my library.
```shell
timestamper hashify
```
3. Build the merkle tree and run through a merkle proof to verify that it's working as expected.
```shell
timestamper build_and_verify_merkle
```
4. Send the merkle root to Bitcoin. If you're doing it the slow way, let's do this in a few steps.
4a. For starters, a dryrun to the testnet. And again, you'll be prompted for your private key.
```shell
timestamper send_merkle_root_to_bitcoin --change_address=<an address you control> \
    --dryrun \
    --testnet
```
4b. Now let's do a live run to the testnet
```shell
timestamper send_merkle_root_to_bitcoin --change_address=<an address you control> \
    --live \
    --testnet
```
4c. Dry run to mainnet. Don't forget to use mainnet addresses
```shell
timestamper send_merkle_root_to_bitcoin --change_address=<an address you control> \
    --dryrun \
    --mainnet
```
4d. Do it live!
```shell
timestamper send_merkle_root_to_bitcoin --change_address=<an address you control> \
    --live \
    --mainnet
```


check your work in a python shell
```python
from app.transmit import get_from_bitcoin

expected_merkle_root = 'f19a3f9912ac3f8572e4bff1a2476e47a5a751b74ac2acda11c702f6fc3997ca'
btc_transaction_id = 'b801e656beec4e2b057334068661bd7a503ad4bf8e8b635e52c73971ec55f58d'
actual_merkle_root = get_from_bitcoin(btc_transaction_id, is_testnet=False)
assert actual_merkle_root == expected_merkle_root
```

### CONTRIBUTE
I'm not sure why you would, but thanks!

run the tests:
```shell
make test
```
