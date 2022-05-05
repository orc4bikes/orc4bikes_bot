import logging

import boto3
from botocore.exceptions import ClientError

from admin import (
    DB_ACCESS_KEY,
    DB_SECRET_KEY,
    DB_REGION_NAME,
)

logger = logging.getLogger()

def create_users_table(dynamodb=None):
    """Creates users table if it doesn't exist"""
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    try:
        table = dynamodb.create_table(
            TableName='users',
            AttributeDefinitions=[
                {
                    'AttributeName': 'chat_id',
                    'AttributeType': 'N'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'chat_id',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return table
    except ClientError:
        return None
    finally:
        return None

def get_user_data(chat_id=None, dynamodb=None):
    """Getting user data as a dictionary"""
    if not chat_id:
        return None
    # create_users_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    table = dynamodb.Table('users')
    response = None
    try:
        response = table.get_item(Key={'chat_id': chat_id})['Item']
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    except KeyError as e:
        logger.warning('Key Error! Item not found')
    finally:
        return response

def set_user_data(chat_id=None, user_data={}, dynamodb=None):
    """Updating single user's data"""
    # Only json dump if importing data
    # user_data = json.loads(json.dumps(user_data), parse_float=Decimal)
    if not chat_id:
        return None
    # create_users_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    table = dynamodb.Table('users')
    response = None

    def keywords(k, a=""):
        if k == "status":
            k = a + "s"
        elif k == "username":
            k = a + "u"
        elif k == "bike_name":
            k = a + "bn"
        elif k == "first_name":
            k = a + "fn"
        elif k == "last_name":
            k = a + "ln"
        elif k == "log":
            k = a + "l"
        return k

    exp_attr_val = {f':{keywords(k)}': v for k, v in user_data.items() if k != "chat_id"}
    update_exp = 'set ' + ', '.join(
        [f'{keywords(k, "#")}=:{keywords(k)}' for k in user_data.keys() if k != "chat_id"])
    exp_attr_name = {
        '#s': 'status',
        '#u': 'username',
        '#fn': 'first_name',
        '#ln': 'last_name',
    }
    if 'bike_name' in user_data.keys():
        exp_attr_name['#bn'] = 'bike_name'
    if 'log' in user_data.keys():
        exp_attr_name['#l'] = 'log'

    try:
        response = table.update_item(
            Key={
                'chat_id': chat_id,
            },
            UpdateExpression=update_exp,
            ExpressionAttributeValues=exp_attr_val,
            ExpressionAttributeNames=exp_attr_name,
            ReturnValues="UPDATED_NEW")
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    except KeyError as e:
        logger.warning('Key Error! Item not found')
    return response

def create_bikes_table(dynamodb=None):
    """Creates bikes table if it doesn't exist"""
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    try:
        table = dynamodb.create_table(
            TableName='bikes',
            AttributeDefinitions=[
                {
                    'AttributeName': 'name',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'name',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return table
    except ClientError:
        return None
    return None

def get_bike_data(bike_name=None, dynamodb=None):
    """Getting bikes data as a dictionary"""
    if not bike_name:
        return None
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    table = dynamodb.Table('bikes')
    response = None
    try:
        response = table.get_item(Key={'name': bike_name})['Item']
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    except KeyError as e:
        logger.warning('Key Error! Item not found')
    return response

def get_all_bikes(dynamodb=None):
    """Getting all bikes data to show"""
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    table = dynamodb.Table('bikes')
    data = None
    try:
        response = table.scan()
        data = response['Items']
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            data.extend(response['Items'])
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    except KeyError as e:
        logger.warning('Key Error! Item not found')
    return data

def set_bike_data(bike_name=None, bike_data={}, dynamodb=None):
    """Updating single bike's data"""
    if not bike_name:
        return None
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    table = dynamodb.Table('bikes')
    response = None

    def keywords(k, a=""):
        if k == "status":
            k = a + "s"
        elif k == "username":
            k = a + "u"
        elif k == "type":
            k = a + "t"
        return k
    exp_attr_val = {f':{keywords(k)}':v for k, v in bike_data.items() if k != 'name'}
    update_exp = 'set ' + ', '.join(
        [f'{keywords(k, "#")}=:{keywords(k)}' for k in bike_data.keys() if k != 'name'])
    try:
        response = table.update_item(
            Key={
                'name': bike_name,
            },
            UpdateExpression=update_exp,
            ExpressionAttributeValues=exp_attr_val,
            ExpressionAttributeNames={
                '#s': 'status',
                '#u': 'username',
                '#t': 'type',
            },
            ReturnValues="UPDATED_NEW"
        )
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    except KeyError as e:
        logger.warning('Key Error! Item not found')
    return response

def create_usernames_table(dynamodb=None):
    """Creates usernames table if it doesn't exist"""
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    try:
        table = dynamodb.create_table(
            TableName='usernames',
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S'
                },
            ],
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType': 'HASH'
                },
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return table
    except ClientError:
        return None
    return None

def get_username(username="", dynamodb=None):
    """Getting username to chat_id mapping"""
    if not username:
        return None
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    table = dynamodb.Table('usernames')
    response = None
    chat_id = None
    try:
        response = table.get_item(Key={'username': username})['Item']
        chat_id = int(response['chat_id'])
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    except KeyError as e:
        logger.warning('Key Error! Item not found')
    return chat_id

def set_username(username="", chat_id=0, dynamodb=None):
    """Updating single bike's data"""
    if not username:
        return None
    # create_bikes_table()
    if not dynamodb:
        dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=DB_ACCESS_KEY,
            aws_secret_access_key=DB_SECRET_KEY,
            region_name=DB_REGION_NAME)
    table = dynamodb.Table('usernames')
    response = None

    try:
        response = table.update_item(
            Key={
                'username': username,
            },
            UpdateExpression='set chat_id=:chat_id',
            ExpressionAttributeValues={':chat_id': chat_id},
            ReturnValues="UPDATED_NEW")
    except ClientError as e:
        logger.exception(e.response['Error']['Message'])
    except KeyError as e:
        logger.warning('Key Error! Item not found')
    return response


if __name__ == '__main__':
    print('Set up DB OK.')
