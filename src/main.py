from uuid import uuid4
import argparse

from flask import Flask, jsonify, request

import block

app = Flask(__name__)

node_identifier = str(uuid4()).replace('-', '')

blockchain = block.Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # reward to PoW
    blockchain.new_transaction(
        sender=0,
        recipient=node_identifier,
        amount=1,
    )

    new_block = blockchain.new_block(proof)
    response = {
        'message': "New Block Forged",
        'index': new_block['index'],
        'transactions': new_block['transactions'],
        'proof': new_block['proof'],
        'previous_hash': new_block['previous_hash'],
    }
    return jsonify(response), 200


@app.route('/transaction/new', methods=['POST'])
def new_trans():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': 'Transaction will be added to Block %s' % index}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/nodes/', methods=['GET'])
def show_all_nodes():
    return jsonify({'nodes': blockchain.nodes}), 200


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()
    nodes = values.get('nodes')
    if not nodes:
        return 'Error: invalid list of nodes', 400

    response = {
        'message': 'New node added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def resolve_conflicts():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {
            'message': 'block chain has been replaced',
            'chain': blockchain.chain,
        }
    else:
        response = {
            'message': 'current block chain is up to date',
            'chain': blockchain.chain,
        }
    return jsonify(response), 200


if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-p', '--port', default=5000, type=int, help='specify the port number')
    args = arg_parser.parse_args()
    port = args.port

    app.run(host='0.0.0.0', port=port)
