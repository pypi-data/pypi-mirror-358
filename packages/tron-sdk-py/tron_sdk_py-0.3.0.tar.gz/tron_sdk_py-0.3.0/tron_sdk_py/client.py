from typing import Union
import grpc

from tron_sdk_py.proto.api.api_pb2_grpc import WalletStub, WalletSolidityStub
from tron_sdk_py.proto.api.api_pb2 import EmptyMessage

from tron_sdk_py.proto.core.Tron_pb2 import Transaction
from tron_sdk_py.proto.api.api_pb2 import TransactionExtention

from tron_sdk_py.types import ADDR, HEX
from tron_sdk_py.keys import private_key_to_address, sign_message


class TronClient(object):
    def __init__(self, private_key=None, endpoint="grpc.trongrid.io:50051", solidity_endpoint="grpc.trongrid.io:50061"):
        channel = grpc.insecure_channel(endpoint)
        self.wallet_stub = WalletStub(channel)

        channel = grpc.insecure_channel(solidity_endpoint)
        self.solidity_stub = WalletSolidityStub(channel)

        self.private_key = private_key
        self.address = None

        if self.private_key:
            self.address = private_key_to_address(self.private_key)

    @classmethod
    def mainnet(cls, private_key=None):
        return cls(private_key)

    @classmethod
    def shasta(cls, private_key=None):
        return cls(
            private_key, endpoint="grpc.shasta.trongrid.io:50051", solidity_endpoint="grpc.shasta.trongrid.io:50061"
        )

    @classmethod
    def nile(cls, private_key=None):
        return cls(private_key, endpoint="grpc.nile.trongrid.io:50051", solidity_endpoint="grpc.nile.trongrid.io:50061")

    def sign(self, txn: Union[Transaction, TransactionExtention]) -> Transaction:
        if not self.private_key:
            raise ValueError("private key is not set")
        if isinstance(txn, TransactionExtention):
            txn = txn.transaction

        msg = txn.raw_data.SerializeToString()
        signature = sign_message(self.private_key, msg)
        txn.signature.append(signature)

        return txn


if __name__ == "__main__":
    from tron_sdk_py.proto.core.contract.balance_contract_pb2 import TransferContract

    client = TronClient.nile(private_key=HEX('3333333333333333333333333333333333333333333333333333333333333333'))
    req = TransferContract()
    req.owner_address = ADDR("TJRabPrwbZy45sbavfcjinPJC18kjpRTv8")
    req.to_address = ADDR("TRsbuxREXKJKonexpejWhacE4sYHt1BSHV")
    req.amount = 1_100_000
    txn = client.wallet_stub.CreateTransaction2(req)

    print("TXID:", HEX(txn.txid))

    signed_txn = client.sign(txn)

    print(signed_txn)

    resp = client.wallet_stub.BroadcastTransaction(signed_txn)

    print(resp)
