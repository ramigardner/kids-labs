import hashlib
import time
import json

class MiniBlockchain:
    def __init__(self):
        self.chain = []
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis = {
            "index": 0,
            "timestamp": time.time(),
            "data": "🌱 Jardín ASPR Kids - Bloque Génesis",
            "prev_hash": "0" * 64,
            "hash": ""
        }
        genesis["hash"] = self.calculate_hash(genesis)
        self.chain.append(genesis)

    def calculate_hash(self, block):
        block_copy = block.copy()
        block_copy.pop("hash", None)
        block_string = json.dumps(block_copy, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    def add_block(self, data):
        prev_block = self.chain[-1]
        new_block = {
            "index": len(self.chain),
            "timestamp": time.time(),
            "data": data,
            "prev_hash": prev_block["hash"],
            "hash": ""
        }
        new_block["hash"] = self.calculate_hash(new_block)
        self.chain.append(new_block)
        return new_block

    def get_latest_block(self):
        return self.chain[-1]

    def get_latest_hash(self):
        return self.chain[-1]["hash"]

    def get_all_blocks(self):
        # Devolver versión simplificada para el frontend
        return [{
            "index": b["index"],
            "data": b["data"],
            "hash": b["hash"][:8] + "...",
            "prev_hash": b["prev_hash"][:8] + "..."
        } for b in self.chain]