#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import path
from functools import wraps

from flask_jsglue import JSGlue
from flask import Flask, request, json, send_from_directory, render_template, redirect, url_for

from ontology.account.account import Account
from ontology.exception.exception import SDKException
from ontology.ont_sdk import OntologySdk

ontology = OntologySdk()
wallet_path = path.join(path.dirname(path.dirname(path.abspath(__file__))), 'wallet', 'wallet.json')
wallet_manager = ontology.wallet_manager
wallet_manager.open_wallet(wallet_path)
wallet_manager.save()

base_path = path.dirname(path.abspath(__file__))
static_folder = path.join(base_path, 'static')
template_folder = path.join(base_path, 'templates')

app = Flask('caviar', static_folder=static_folder, template_folder=template_folder)
jsglue = JSGlue()
jsglue.init_app(app)
default_ctrl_acct = None
default_wallet_account = None


def ensure_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not isinstance(default_ctrl_acct, Account):
            return redirect('login')
        return func(*args, **kwargs)

    return wrapper


@app.route('/get_contract_address', methods=['GET'])
def get_contract_address():
    contract_address = app.config['CONTRACT_ADDRESS_HEX']
    return json.jsonify({'result': contract_address}), 200


@app.route('/get_accounts', methods=['GET'])
def get_accounts():
    acct_data_list = ontology.wallet_manager.get_acct_data_list()
    address_list = list()
    for acct_data in acct_data_list:
        acct_item = {'b58_address': acct_data.b58_address, 'label': acct_data.label}
        address_list.append(acct_item)
    return json.jsonify({'result': address_list}), 200


@app.route('/is_default_wallet_account_unlock', methods=['GET'])
def is_default_wallet_account_unlock():
    global default_wallet_account
    if isinstance(default_wallet_account, Account):
        return json.jsonify({'result': True}), 200
    else:
        return json.jsonify({'result': False}), 200


@app.route('/create_account', methods=['POST'])
def create_account():
    password = request.json.get('password')
    label = request.json.get('label')
    acct_data = ontology.wallet_manager.create_account(label, password)
    acct = ontology.wallet_manager.get_account_by_b58_address(acct_data.b58_address, password)
    ontology.wallet_manager.save()
    return json.jsonify({'hex_private_key': acct.get_private_key_hex()})


@app.route('/import_account', methods=['POST'])
def import_account():
    label = request.json.get('label')
    password = request.json.get('password')
    hex_private_key = request.json.get('hex_private_key')
    try:
        acct = ontology.wallet_manager.create_account_from_private_key(label, password, hex_private_key)
    except ValueError as e:
        return json.jsonify({'msg': 'account exists.'}), 500
    ontology.wallet_manager.save()
    return json.jsonify({'result': acct.b58_address}), 200


@app.route('/remove_account', methods=['POST'])
def remove_account():
    b58_address_remove = request.json.get('b58_address_remove')
    password = request.json.get('password')
    try:
        acct = ontology.wallet_manager.get_account(b58_address_remove, password)
        if acct is None:
            return json.jsonify({'result': ''.join(['remove ', b58_address_remove, ' failed!'])}), 500
        ontology.wallet_manager.get_wallet().remove_account(b58_address_remove)
    except SDKException or RuntimeError:
        return json.jsonify({'result': ''.join(['remove ', b58_address_remove, ' failed!'])}), 500
    ontology.wallet_manager.save()
    return json.jsonify({'result': ''.join(['remove ', b58_address_remove, ' successful!'])}), 200


@app.route('/account_change', methods=['POST'])
def account_change():
    b58_address_selected = request.json.get('b58_address_selected')
    password = request.json.get('password')
    global default_wallet_account
    old_wallet_account = default_wallet_account
    try:
        default_wallet_account = ontology.wallet_manager.get_account(b58_address_selected, password)
    except SDKException:
        default_wallet_account = old_wallet_account
        return json.jsonify({'result': 'invalid password'}), 400
    try:
        ontology.wallet_manager.get_wallet().set_default_account_by_address(b58_address_selected)
    except SDKException:
        return json.jsonify({'result': 'invalid base58 address'})
    ontology.wallet_manager.save()
    return json.jsonify({'result': 'Change successful'}), 200


@app.route('/get_identities', methods=['GET'])
def get_identities():
    identities = ontology.wallet_manager.get_wallet().get_identities()
    ont_id_list = list()
    for item in identities:
        ont_id_item = {'ont_id': item.ont_id, 'label': item.label}
        ont_id_list.append(ont_id_item)
    return json.jsonify({'result': ont_id_list}), 200


@app.route('/create_identity', methods=['POST'])
def create_identity():
    label = request.json.get('label')
    password = request.json.get('password')
    try:
        new_identity = ontology.wallet_manager.create_identity(label, password)
    except SDKException as e:
        return json.jsonify({'result': e}), 500
    try:
        acct = ontology.wallet_manager.get_control_account_by_index(new_identity.ont_id, 0, password)
    except SDKException as e:
        return json.jsonify({'result': e}), 501
    ontology.wallet_manager.save()
    return json.jsonify({'hex_private_key': acct.get_private_key_hex(), 'ont_id': new_identity.ont_id}), 200


@app.route('/import_identity', methods=['POST'])
def import_identity():
    label = request.json.get('label')
    password = request.json.get('password')
    hex_private_key = request.json.get('hex_private_key')
    try:
        new_identity = ontology.wallet_manager.create_identity_from_private_key(label, password,
                                                                                hex_private_key)
    except SDKException as e:
        return json.jsonify({'result': e}), 500
    ontology.wallet_manager.save()
    return json.jsonify({'hex_private_key': hex_private_key, 'ont_id': new_identity.ont_id}), 200


@app.route('/remove_identity', methods=['POST'])
def remove_identity():
    ont_id_remove = request.json.get('ont_id_remove')
    password = request.json.get('password')
    try:
        acct = ontology.wallet_manager.get_account(ont_id_remove, password)
        if acct is None:
            return json.jsonify({'result': ''.join(['remove ', ont_id_remove, ' failed!'])}), 500
        ontology.wallet_manager.get_wallet().remove_identity(ont_id_remove)
    except SDKException or RuntimeError:
        return json.jsonify({'result': ''.join(['remove ', ont_id_remove, ' failed!'])}), 500
    ontology.wallet_manager.save()
    return json.jsonify({'result': ''.join(['remove ', ont_id_remove, ' successful!'])}), 200


@app.route('/identity_change', methods=['POST'])
def identity_change():
    ont_id_selected = request.json.get('ont_id_selected')
    password = request.json.get('password')
    global default_ctrl_acct
    old_identity_account = default_ctrl_acct
    try:
        default_ctrl_acct = ontology.wallet_manager.get_account(ont_id_selected, password)
    except SDKException:
        default_ctrl_acct = old_identity_account
        return json.jsonify({'result': 'Invalid Password'}), 501
    try:
        ontology.wallet_manager.get_wallet().set_default_identity_by_ont_id(ont_id_selected)
    except SDKException:
        return json.jsonify({'result': 'Invalid OntId'}), 500
    ontology.wallet_manager.save()
    return json.jsonify({'result': 'Change Successful'}), 200


@app.route('/change_net', methods=['POST'])
def change_net():
    network_selected = request.json.get('network_selected')
    if network_selected == 'MainNet':
        ontology.rpc.connect_to_main_net()
        sdk_rpc_address = ontology.rpc.get_address()
        if 'dappnode' not in sdk_rpc_address:
            result = ''.join(['remote rpc address set failed. the rpc address now used is ', sdk_rpc_address])
            return json.jsonify({'result': result}), 409
    elif network_selected == 'TestNet':
        ontology.rpc.connect_to_test_net()
        sdk_rpc_address = ontology.rpc.get_address()
        if 'polaris' not in sdk_rpc_address:
            result = ''.join(['remote rpc address set failed. the rpc address now used is ', sdk_rpc_address])
            return json.jsonify({'result': result}), 409
    elif network_selected == 'Localhost':
        ontology.rpc.connect_to_localhost()
        old_remote_rpc_address = ontology.rpc.get_address()
        sdk_rpc_address = ontology.rpc.get_address()
        if 'localhost' not in sdk_rpc_address:
            result = ''.join(['remote rpc address set failed. the rpc address now used is ', sdk_rpc_address])
            return json.jsonify({'result': result}), 409
        try:
            ontology.rpc.get_version()
        except SDKException as e:
            ontology.rpc.set_address(old_remote_rpc_address)
            error_msg = 'Other Error, ConnectionError'
            if error_msg in e.args[1]:
                return json.jsonify({'result': 'Connection to localhost node failed.'}), 400
            else:
                return json.jsonify({'result': e.args[1]}), 500
    else:
        return json.jsonify({'result': 'unsupported network.'}), 501
    return json.jsonify({'result': 'succeed'}), 200


@app.route('/unlock_account', methods=['POST'])
def unlock_account():
    try:
        b58_address_selected = request.json.get('b58_address_selected')
        acct_password = request.json.get('acct_password')
    except AttributeError as e:
        redirect_url = request.url.replace('unlock_account', '')
        return json.jsonify({'result': e.args, 'redirect_url': redirect_url}), 500
    global default_wallet_account
    try:
        default_wallet_account = app.config['WALLET_MANAGER'].get_account(b58_address_selected, acct_password)
    except SDKException as e:
        redirect_url = request.url.replace('unlock_account', 'login')
        return json.jsonify({'result': e.args[1], 'redirect_url': redirect_url}), 501
    if isinstance(default_wallet_account, Account):
        msg = ''.join(['unlock ', b58_address_selected, ' successful!'])
        redirect_url = request.url.replace('unlock_account', '')
        return json.jsonify({'result': msg, 'redirect_url': redirect_url}), 200
    else:
        redirect_url = request.url.replace('unlock_account', 'login')
        return json.jsonify({'result': 'unlock failed!', 'redirect_url': redirect_url}), 502


@app.route('/unlock_identity', methods=['POST'])
def unlock_identity():
    try:
        ont_id = request.json.get('ont_id')
        pwd = request.json.get('pwd')
    except AttributeError as e:
        redirect_url = request.url.replace('unlock_identity', '')
        return json.jsonify({'result': e.args, 'redirect_url': redirect_url}), 500
    global default_ctrl_acct
    try:
        default_ctrl_acct = ontology.wallet_manager.get_control_account_by_index(ont_id, 0, pwd)
    except SDKException as e:
        redirect_url = request.url.replace('unlock_identity', 'login')
        return json.jsonify({'result': e.args[1], 'redirect_url': redirect_url}), 501
    if isinstance(default_ctrl_acct, Account):
        msg = f'unlock {ont_id} successful!'
        redirect_url = request.url.replace('unlock_identity', '')
        return json.jsonify({'result': msg, 'redirect_url': redirect_url}), 200
    else:
        redirect_url = request.url.replace('unlock_identity', 'login')
        return json.jsonify({'result': 'unlock failed!', 'redirect_url': redirect_url}), 502


@app.route('/', methods=['GET'])
@ensure_login
def index():
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(static_folder, 'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/login')
def login():
    if isinstance(default_wallet_account, Account):
        return redirect('')
    else:
        return render_template('login.html')



if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
