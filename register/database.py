import boto3
import uuid
import os
import hashlib
import binascii

dynamodb = boto3.resource('dynamodb', region_name='us-west-2')
table = dynamodb.Table('Users')


def register_user(username, password, companyName, email):
    hashedPassword = hash_password(password)
    try:
        table.put_item(
            Item={
                "userId": str(uuid.uuid4()),
                "username": username,
                "email": email,
                "password": hashedPassword,
                "company_name": companyName
            }
        )
    except Exception as e:
        print(e)


def hash_password(password):
    """Hash a password for storing."""
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'), salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def verify_password(stored_password, provided_password):
    """Verify a stored password against one provided by user"""
    salt = stored_password[:64]
    stored_password = stored_password[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512', provided_password.encode('utf-8'), salt.encode('ascii'), 100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_password
