from argparse import ArgumentParser
from uuid import uuid4

from flask import Flask, jsonify, request

from myBlockChain import BlockChain

app = Flask(__name__)
blockchain = BlockChain()
node_identifier = str(uuid4()).replace('-', '')


@app.route('/index', methods=['GET'])
def index():
    return "Hello BlockChain"


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    print(values)
    require = ["sender", "recipient", "amount"]
    if values is None:
        return "Missing values", 400
    if not all(k in values for k in require):
        return "Missing values", 400
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response = {"message": f'Transaction added to Block {index}'}
    return jsonify(response), 201


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    blockchain.new_transaction(sender="0", recipient=node_identifier, amount=1)
    block = blockchain.new_block(proof, None)

    response = {
        "message": "new block forged",
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }
    print(response)
    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get("nodes")
    if nodes is None:
        return "error: not a valid nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        "message": "new nodes have been added",
        "total_node": list(blockchain.nodes)
    }

    return jsonify(response), 200


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    response = {
        'new_chain': blockchain.chain,
        'replaced': replaced
    }
    return jsonify(response), 200


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host='127.0.0.1', port=port, debug=True)
