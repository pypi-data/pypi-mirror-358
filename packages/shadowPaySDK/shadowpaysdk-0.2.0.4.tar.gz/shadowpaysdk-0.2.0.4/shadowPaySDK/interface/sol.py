import asyncio
from solana.rpc.async_api import AsyncClient, GetTokenAccountsByOwnerResp
import spl
import spl.token
import spl.token.constants
from spl.token.instructions import get_associated_token_address, create_associated_token_account, transfer, close_account
from spl.token.constants import TOKEN_PROGRAM_ID, ASSOCIATED_TOKEN_PROGRAM_ID
from solana.constants import *
from solana.rpc.types import TxOpts, TokenAccountOpts
from solana.rpc.types import TxOpts
import solders
from solders.pubkey import Pubkey
from solders.keypair import Keypair
from solders.signature import Signature
import anchorpy
from anchorpy import Provider, Wallet, Idl
from typing import Optional, Union
import pprint
import httpx
import base64
import re

class SolTokens:    
    def __init__(self, rpc_url: str = "https://api.mainnet-beta.solana.com"):
        self.rpc_url = rpc_url
        self.client = AsyncClient(rpc_url)
        self.PROGRAM_ID = TOKEN_PROGRAM_ID # Default to the SPL Token Program ID
        self.WRAPED_SOL_ID = spl.token.constants.WRAPPED_SOL_MINT
    def set_params(self, rpc_url: Optional[str] = None, PROGRAM_ID: Optional[str] = None):
        if rpc_url:
            self.rpc_url = rpc_url
            self.client = AsyncClient(rpc_url)

class SOL:
    
    def __init__(self, rpc_url = "https://api.mainnet-beta.solana.com", KEYPAIR: Optional[Union[str, Keypair]] = None):
            self.rpc_url = rpc_url
            self.client = AsyncClient(rpc_url)
            self.KEYPAIR = None

            if KEYPAIR:
                self.set_keypair(KEYPAIR)

    def set_keypair(self, KEYPAIR: Union[str, Keypair]):
        if isinstance(KEYPAIR, str):
            try:
                self.KEYPAIR = Keypair.from_base58_string(KEYPAIR)
            except Exception as e:
                raise ValueError(f"Invalid Keypair string: {e}")
        elif isinstance(KEYPAIR, Keypair):
            self.KEYPAIR = KEYPAIR
        else:
            raise ValueError("KEYPAIR must be a Keypair instance or a base58 encoded string.")

    def set_params(self, rpc_url: Optional[str] = None, KEYPAIR: Optional[Union[str, Keypair]] = None):
        if rpc_url:
            self.rpc_url = rpc_url
            self.client = AsyncClient(rpc_url)
        if KEYPAIR:
            self.set_keypair(KEYPAIR)            

    def get_pubkey(self, returnString: Optional[bool] = None):

        
        if self.KEYPAIR:
            pubkey = self.KEYPAIR.pubkey()
            pubkey_str = str(pubkey)
            if returnString:
                return pubkey_str
            return pubkey
        
        raise ValueError("Keypair not set")

    def gen_wallet(self):
        return Keypair()
    async def get_balance(self):
        resp = await self.client.get_balance(self.get_pubkey())
        lamports = resp.value
        sol_balance = lamports / LAMPORTS_PER_SOL
        return sol_balance  
    async def get_token_accounts_by_owner(self,owner_pubkey: Optional[str] = None):
        if not owner_pubkey:
            print("No owner pubkey provided, using the wallet's pubkey.")
            owner_pubkey = self.get_pubkey(returnString=True)
        headers = {
            "Content-Type": "application/json",
        }
        body = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getTokenAccountsByOwner",
            "params": [
                str(owner_pubkey),
                {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                {"encoding": "jsonParsed"}
            ]
        }
        async with httpx.AsyncClient() as client:
            response = await client.post(self.rpc_url, headers=headers, json=body)
            result = response.json()
            accounts = result["result"]["value"]

            token_data = {}
            for acc in accounts:
                parsed = acc["account"]["data"]["parsed"]["info"]
                mint = parsed["mint"]
                ui_amount = parsed["tokenAmount"]["uiAmount"]
                token_data[mint] = {"amount": ui_amount}

            filtered = {mint: data for mint, data in token_data.items() if data["amount"] > 0.001}

            return filtered
    async def is_connected(self):
        return await self.client.is_connected()

    async def close(self):
        await self.client.close()
    
    async def fetch_metadata_raw(self,mint_address: str):
        METADATA_PROGRAM_ID = Pubkey.from_string("metaqbxxUerdq28cj1RbAWkYQm3ybzjb6a8bt518x1s")
        mint = Pubkey.from_string(mint_address)
        seeds = [
            b"metadata",
            bytes(METADATA_PROGRAM_ID),
            bytes(mint),
        ]
        pda, _ = Pubkey.find_program_address(seeds, METADATA_PROGRAM_ID)

        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [
                str(pda),
                {"encoding": "base64"}
            ]
        }

        async with httpx.AsyncClient() as client:
            r = await client.post("https://api.mainnet-beta.solana.com", json=payload)
            data = r.json()

        if not data["result"]["value"]:
            return None

        b64_data = data["result"]["value"]["data"][0]
        raw_bytes = base64.b64decode(b64_data)

        name = raw_bytes[1+32+32 : 1+32+32+32].decode("utf-8").rstrip("\x00")
        name = re.sub(r'[^\x20-\x7E]', '', name)     
        return {
            "mint": mint_address,
            "name": name,
        }





if __name__ == "__main__":
    newKeypair = Keypair()
    print("New Keypair:", newKeypair)