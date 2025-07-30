import shadowPaySDK
from shadowPaySDK.const import __SHADOWPAY_ABI__ERC20__, __ALLOW_CHAINS__, __SHADOWPAY_CONTRACT_ADDRESS__ERC20__
from shadowPaySDK.api import  __CREATE__CHEQUE__
from web3 import Web3
from typing import Optional
import httpx


class Cheque:
    def __init__(self, w3:Optional[Web3] = None,private_key:Optional[str] = None, ABI = __SHADOWPAY_ABI__ERC20__, allowed_chains = __ALLOW_CHAINS__):
        self.w3 = w3

        self.amount = None
        self.token = None
        self.private_key = private_key
        self.ABI = ABI

        self.allowed_chains = allowed_chains
        if self.w3 != None:
            self.__allow__()

    def __get__id(self, tx):
        try:
            logs = self.contract.events.ChequeCreated().process_receipt(tx)
            cheque_id = logs[0]["args"]["id"]
            return cheque_id.hex()
        except Exception as e:
            print(f"Failed to get cheque ID from transaction receipt: {str(e)}")
            return False
    def __allow__(self):
        for chain in self.allowed_chains:

            if chain == self.w3.eth.chain_id:
                self.get_contract_for_chain(chain_id=self.w3.eth.chain_id)

                return True
            
        raise ValueError(f"Chain {str(self.w3.eth.chain_id)} is not allowed. Allowed chains are: {self.allowed_chains}")
    def get_contract_for_chain(self,chain_id: str):
        c = None
        for chain in __SHADOWPAY_CONTRACT_ADDRESS__ERC20__  :
            if str(chain) == str(chain_id):
                c = __SHADOWPAY_CONTRACT_ADDRESS__ERC20__[chain_id]
            contract_address = Web3.to_checksum_address(c)
            contract = self.w3.eth.contract(address=contract_address, abi=__SHADOWPAY_ABI__ERC20__)
            self.contract = contract
            return contract
        raise ValueError(f"Chain {chain_id} is not supported. Supported chains are: {list(__SHADOWPAY_CONTRACT_ADDRESS__ERC20__.keys())}")    
        
    def set_parameters(self,chain_id: Optional[str] = None, w3:Optional[Web3] = None, amount:Optional[int]  = None, private_key:Optional[str] = None, token:Optional[str] = None):
        if  w3:
            self.w3 = w3
            self.get_contract_for_chain(chain_id=chain_id or self.w3.eth.chain_id)
        if amount:
            self.amount = amount
        if private_key:
            self.private_key = private_key
        if token:
            self.token = token
    def __convert__(self):
        return self.w3.to_wei(self.amount, 'ether')

    async def InitCheque(self, amount,  receiver:list, private_key:Optional[str] = None):
        if  not isinstance(receiver,list):
            raise ValueError("Receiver must be a list of addresses, [""0x1234...5678", "0x2345...6789""]")
        
        receiver = [Web3.to_checksum_address(addr) for addr in receiver]
        estimated_gas = self.contract.functions.InitCheque(receiver).estimate_gas({
            'from': self.w3.eth.account.from_key(private_key or self.private_key).address,
            'value': self.w3.to_wei(amount, 'ether'),
            'gasPrice': self.w3.eth.gas_price
        })
        txn = self.contract.functions.InitCheque(receiver).build_transaction({
            'from': self.w3.eth.account.from_key(private_key or self.private_key).address,
            'value': self.w3.to_wei(amount, 'ether'),
            'nonce': self.w3.eth.get_transaction_count(
                self.w3.eth.account.from_key(private_key or self.private_key).address
            ),
            'gas': estimated_gas,
            'gasPrice': self.w3.eth.gas_price,
            'chainId': self.w3.eth.chain_id
        })
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key or self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        txn_receipt = self.w3.eth.wait_for_transaction_receipt(txn_hash)
        insert_to_dn = None
        logs = self.__get__id(txn_receipt)
        if logs:
            cheque_id = logs
        else:
            cheque_id = None
        if txn_receipt.status != 1:
            return False
        return {
            "hash": txn_hash.hex(),
            "chequeId": cheque_id,
        }

 


    async def CashOutCheque(
        self,
        private_key: str,
        cheque_id: str  # hex-строка типа "0xabc..."
    ):
        if not private_key:
            private_key = self.private_key

            
        account = self.w3.eth.account.from_key(private_key)
        sender_address = account.address


        # подготовка транзакции
        nonce = self.eth.get_transaction_count(sender_address)

        txn = self.contract.functions.CashOutCheque(
            Web3.to_bytes(hexstr=cheque_id)).build_transaction({
            'from': sender_address,
            'nonce': nonce,
            'gas': 300_000,  # пример
            'gasPrice': self.w3.to_wei('5', 'gwei'),
        })

        # подписываем
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=private_key)

        # отправляем
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        print(f"⏳ Transaction sent: {tx_hash.hex()}")
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        print(f"✅ Transaction confirmed in block {receipt.blockNumber}")
        if receipt.status != 1:
            return False
        return receipt    

    async def InitTokenCheque(self, token_address:str, amount, reciver:str, private_key:Optional[str] = None):
        
        
        erc20 = shadowPaySDK.ERC20Token(w3=self.w3)
        erc20.set_params(token_address=token_address)
        ensure_allowance = erc20.ensure_allowance(
            private_key=self.private_key, 
            spender=self.contract.address, 
            amount=amount
        )
        print(f"Ensure allowance: {ensure_allowance}")
        decimals = erc20.get_decimals()
        estimated_gas = self.contract.functions.InitTokenCheque(
            Web3.to_checksum_address(token_address),
            int(amount * (10 ** decimals)),
            Web3.to_checksum_address(reciver)
        ).estimate_gas({
            'from': self.w3.eth.account.from_key(self.private_key).address,
            'gasPrice': self.w3.eth.gas_price
        })
        txn = self.contract.functions.InitTokenCheque(
            Web3.to_checksum_address(token_address),
            int(amount * (10 ** decimals)),
            Web3.to_checksum_address(reciver)
        ).build_transaction({
            'from': self.w3.eth.account.from_key(self.private_key).address,
            'nonce': self.w3.eth.get_transaction_count(self.w3.eth.account.from_key(self.private_key).address),
            'gas': estimated_gas,
            'gasPrice': self.w3.eth.gas_price
        })
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        txn_receipt = self.w3.eth.wait_for_transaction_receipt(txn_hash)
        
        logs = self.__get__id(txn_receipt)
        if logs:
            cheque_id = logs
        else:
            cheque_id = None
        if txn_receipt.status != 1:
            return False
        return {
            "hash": txn_hash.hex(),
            "chequeId": cheque_id,
        }

    async def CashOutTokenCheque(self, cheque_id: str, private_key: Optional[str] = None):
        if private_key is None:
            private_key = self.private_key
        
        account = self.w3.eth.account.from_key(private_key)
        

        
        # Строим транзакцию
        estimated_gas = self.contract.functions.CashOutTokenCheque(
            Web3.to_bytes(hexstr=cheque_id)  # Преобразуем строку в bytes32
        ).estimate_gas({
            'from': account.address,
            'gasPrice': self.w3.eth.gas_price
        })
        txn = self.contract.functions.CashOutTokenCheque(
            Web3.to_bytes(hexstr=cheque_id)  
        ).build_transaction({
            'from': account.address,
            'nonce': self.w3.eth.get_transaction_count(account.address),
            'gas': estimated_gas,
            'gasPrice': self.w3.eth.gas_price,
        })

        # Подписываем и отправляем транзакцию
        signed_txn = self.w3.eth.account.sign_transaction(txn, private_key=private_key)
        tx_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)

        # Получаем подтверждение
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)

        if receipt.status != 1:
            return False
        return {
            "hash": tx_hash.hex(),
            "status": receipt.status  # 1 = success, 0 = fail
        }
    async def InitTokenChequeSwap(self, token_in:str, amount_in,token_out:str, amount_out, reciver:str, private_key:Optional[str] = None):
        
        erc20 = shadowPaySDK.ERC20Token(w3=self.w3)
        erc20.set_params(token_address=token_in)
        ensure_allowance = erc20.approve(
            private_key=self.private_key, 
            spender=self.contract.address, 
            amount=amount_in,
            token=token_in
        )
        print(f"Ensure allowance: {ensure_allowance}")
        decimals = erc20.get_decimals(token_in)
        token_out_decinals = erc20.get_decimals(token_out)
        estimated_gas = self.contract.functions.InitSwapCheque(
            Web3.to_checksum_address(reciver),
            Web3.to_checksum_address(token_in),
            int(amount_in * (10 ** decimals)),
            Web3.to_checksum_address(token_out),
            int(amount_out * (10 ** token_out_decinals)),
        ).estimate_gas({
            'from': self.w3.eth.account.from_key(self.private_key).address,
            'gasPrice': self.w3.eth.gas_price
        })
        txn = self.contract.functions.InitSwapCheque(
            Web3.to_checksum_address(reciver),
            Web3.to_checksum_address(token_in),
            int(amount_in * (10 ** decimals)),
            Web3.to_checksum_address(token_out),
            int(amount_out * (10 ** token_out_decinals))
        ).build_transaction({
            'from': self.w3.eth.account.from_key(self.private_key).address,
            'nonce': self.w3.eth.get_transaction_count(self.w3.eth.account.from_key(self.private_key).address),
            'gas': estimated_gas,
            'gasPrice': self.w3.eth.gas_price
        })
        signed_txn = self.w3.eth.account.sign_transaction(txn, self.private_key)
        txn_hash = self.w3.eth.send_raw_transaction(signed_txn.raw_transaction)
        txn_receipt = self.w3.eth.wait_for_transaction_receipt(txn_hash)
        
        logs = self.__get__id(txn_receipt)
        if logs:
            cheque_id = logs
        else:
            cheque_id = None
        if txn_receipt.status != 1:
            return False
        return {
            "hash": txn_hash.hex(),
            "chequeId": cheque_id
        }
    async def getComunityPool(self):
        # fee = self.contract.functions.getCollectedFee().call()
        fee = 50000000000000
        half_fee_eth = self.w3.from_wei(fee // 2, 'ether')
        return half_fee_eth
    async def getOwner(self):
        return self.contract.functions.getOwner().call()
    async def getTreasery(self):
        return self.contract.functions.getTreasery().call()
    async def getSwaoDetail(self, cheque_id: str):
        cheque_id_bytes = Web3.to_bytes(hexstr=cheque_id)
        return self.contract.functions.getSwapDetail(cheque_id_bytes).call()
class NFTcheque:
    def __init__(self, w3:Web3, token:str, amount:int, spender:str):
        self.w3 = w3
        self.token = token
        self.amount = amount
        self.spender = spender

    def InitNFTCheque(self):
        pass

    def CashOutNFTCheque(self):
        pass



















async def create_cheque(id, type, chain_id, receiver, sender):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            __CREATE__CHEQUE__,
            json={
                "cheque_id": id,
                "chain_id":chain_id, 
                "receiver": receiver,
                "type": type,
                "sender":sender
            }
        )
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Failed to create cheque: {response.text}")
            return False