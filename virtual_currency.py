from digital_signiture import sign, verificate, generate_key
from time import time
import hashlib
import json
import os
import sys

from flask import Flask, jsonify, request
from urllib.parse import urlparse
import requests


class VC(object):  # Virtual Currency
    """
    ブロックが生成される流れは
    transactionsに取引がたまる
    mineしてtransactionsを含むブロックを生成し、ブロックチェーンにつなげる
    transaciton_reset()でtransactionsを空にする
    """

    def __init__(self):
        self.transactions = []
        self.chain = []
        self.nodes = set()
        self.sercret_key, self.public_key = self.genesis_block()

    def gold_vein(self):  # マイニングコインの送信者のための金脈
        key = generate_key()
        transaction = {
            "sender": None,
            "recipient": key[1],
            "amount": int(sys.maxsize),
            "digital_signiture": None,
        }
        self.transactions.append(transaction)
        return key

    def genesis_block(self):  # ジェネシスブロックを生成
        key = self.gold_vein()
        block = {
            "index": len(self.chain)+1,
            "timestamp": time(),
            "transactions": self.transactions,
            "proof": 0,
            "previous_hash": 0
        }
        self.transaction_reset()
        self.chain.append(block)
        return key

    def new_block(self, proof):  # 新しいブロックを生成
        """
        ブロックの中身は
        index:ブロックの索引番号
        timestamp:生成日時
        transactions:取引内容
        proof:ナンス
        previous_hash:前のブロックのハッシュ
        """
        block = {
            "index": len(self.chain)+1,
            "timestamp": time(),
            "transactions": self.transactions,
            "proof": proof,
            "previous_hash": self.hash(self.last_block)
        }
        self.transaction_reset()
        self.chain.append(block)

    def transaction_reset(self):  # トランザクションをリセット
        self.transactions = []

    def new_transaction(self, message, signiture):  # トランザクションを生成
        """
        トランザクションの中身
        sender:送信者
        recipient:受診者
        amount:コインの量
        digital_signiture:電子署名
        """
        sender, recipient, amount = message
        # 電子署名が検証されかつ送りたいコインの量が送信者の所持数未満かつ0より大きい場合
        if verificate(str(message), sender, signiture) and amount < self.owned(sender) and amount > 0:
            transaction = {
                "sender": sender,
                "recipient": recipient,
                "amount": amount,
                "digital_signiture": signiture,
            }
            self.transactions.append(transaction)
            return True
        return False

    def owned(self, owner):  # ownerのコイン所持枚を返す
        amount = 0
        for block in self.chain:
            for transaction in block["transactions"]:
                # Chain書き換えたらタプルじゃなくなる
                if tuple(owner) == tuple(transaction["recipient"]):
                    amount += transaction["amount"]
                if(transaction["sender"] == None):  # ジェネシスブロック対策
                    continue
                if tuple(owner) == tuple(transaction["sender"]):
                    amount -= transaction["amount"]
        return amount

    def mine(self, proof, pub_k):  # マイニング
        if self.valid_proof(self.last_block, proof):
            message = (self.public_key, pub_k, 10)
            signiture = sign(str(message), self.sercret_key)
            self.new_transaction(message, signiture)
            self.new_block(proof)
            return True
        return False

    @property
    def last_block(self):  # 最新のブロックを返す
        return self.chain[-1]

    @staticmethod
    def hash(block):  # ハッシュ関数
        return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()

    def proof_of_work(self):  # マイニング
        proof = 0
        last_block = self.last_block
        while self.valid_proof(last_block, proof) is False:
            proof += 1
        return proof

    @staticmethod
    def valid_proof(last_block, proof):  # 正しいproofか検証
        return hashlib.sha256(f"{int(json.dumps(last_block, sort_keys=True).encode().hex(),16)*proof}".encode()).hexdigest()[:4] == "0000"

    def check(self, chain):  # ブロックチェーンが連続性を持つか検証する
        for i in range(1, len(chain)):
            if chain[i]["previous_hash"] != self.hash(chain[i-1]):
                return False
            if not self.valid_proof(chain[i-1], chain[i]["proof"]):
                return False
        return True

    def consensus(self):  # 登録された他のノードのブロックチェーンが自分のものよりながければ置き換える
        swap_f = False
        max_length = len(self.chain)
        for node in self.nodes:
            response = requests.get(f"http://{node}/chain")
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.check(chain):
                    max_length = length
                    self.chain = chain
                    swap_f = True
        return swap_f

    def register_node(self, address):  # ノードを登録する
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)


app = Flask(__name__)

vc = VC()

# 以下はFlaskを用いたAPI化


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """
    message=(sender:(int,int),recipient:(int,int),amount:int)
    signiture=(r:int,s:int)<-sign(str(message),sec_k)
    """
    values = request.get_json()
    m = tuple(map(int, values["message"].replace(
        "(", "").replace(")", "").split(',')))
    message = ((m[0], m[1]), (m[2], m[3]), m[4])
    signiture = tuple(map(int, values["signiture"].strip('()').split(',')))
    if vc.new_transaction(message, signiture):
        response = {'message': "True"}
        return jsonify(response), 201
    response = {'message': "False"}
    return jsonify(response), 400


@ app.route('/mine', methods=['POST'])
def mine():
    """
    public_key:(int,int)
    """
    values = request.get_json()
    proof = vc.proof_of_work()
    key = tuple(map(int, values["public_key"].strip('()').split(',')))
    if vc.mine(proof, key):
        response = {
            'message': "You Gain 10 Coin !!",
        }
        return jsonify(response), 201
    response = {'message': "Fail to Mine"}
    return jsonify(response), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': vc.chain,
        'length': len(vc.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/consensus', methods=['GET'])
def consensus():
    if vc.consensus():
        response = {
            'message': "Chain Replaced",
            'new_chain': vc.chain
        }
    else:
        response = {
            'message': "Constant Chain",
            'new_chain': vc.chain
        }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_node():
    """
    nodes:[str]
    """
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Node", 400

    for node in nodes:
        vc.register_node(node)

    response = {
        'message': 'Add New Node',
        'total_nodes': list(vc.nodes),
    }
    return jsonify(response), 201


@app.route('/owned', methods=['POST'])
def owned():
    """
    owner:(int,int)
    """
    values = request.get_json()

    owner = tuple(map(int, values["owner"].strip('()').split(',')))
    num = vc.owned(owner)

    response = {
        'num': num,
    }
    return jsonify(response), 201


if __name__ == '__main__':  # Test
    pid = os.fork()
    if pid == 0:  # Child Process
        app.run(host='0.0.0.0', port=5001)
    else:
        app.run(host='0.0.0.0', port=5000)

    print('Ended process (PID: %s)' % os.getpid())
