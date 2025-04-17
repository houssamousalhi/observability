import boto3
import logging
import os
import requests
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
iam = boto3.client('iam')
secretsmanager = boto3.client('secretsmanager')

def get_grafana_api_key():
    """Get Grafana API key from Secrets Manager"""
    try:
        api_key_path = os.environ.get('GRAFANA_API_KEY_PATH')
        logger.info(f"Retrieving Grafana API key from path: {api_key_path}")
        
        response = secretsmanager.get_secret_value(
            SecretId=api_key_path
        )
        api_key = json.loads(response['SecretString'])['apikey']
        logger.info("Successfully retrieved Grafana API key")
        return api_key
    except Exception as e:
        logger.error(f"Error getting Grafana API key: {str(e)}")
        raise

def update_grafana_datasource(access_key, secret_key, datasource_name):
    """Update Grafana CloudWatch datasource with new credentials"""
    try:
        grafana_url = os.environ.get('GRAFANA_URL')
        logger.info(f"Updating Grafana datasource '{datasource_name}' at URL: {grafana_url}")
        
        api_key = get_grafana_api_key()
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Get all datasources
        logger.info("Fetching all Grafana datasources")
        response = requests.get(f'{grafana_url}/api/datasources', headers=headers)
        response.raise_for_status()
        
        # Find CloudWatch datasource with matching name
        datasources = response.json()
        logger.info(f"Found {len(datasources)} datasources in Grafana")
        
        cloudwatch_ds = next((ds for ds in datasources if ds['type'] == 'cloudwatch' and ds['name'] == datasource_name), None)
        
        if not cloudwatch_ds:
            logger.error(f"CloudWatch datasource with name '{datasource_name}' not found in Grafana")
            return
            
        logger.info(f"Found CloudWatch datasource with ID: {cloudwatch_ds['id']}")
            
        # Update datasource with new credentials
        update_data = {
            'name': cloudwatch_ds['name'],
            'type': 'cloudwatch',
            'access': 'proxy',
            'jsonData': {
                'defaultRegion': os.environ.get('AWS_REGION'),
                'authType': 'keys'
            },
            "secureJsonData": {
                'accessKey': access_key,
                'secretKey': secret_key
            }
        }
        
        logger.info(f"Updating datasource {cloudwatch_ds['id']} with new credentials")
        response = requests.put(
            f'{grafana_url}/api/datasources/{cloudwatch_ds["id"]}',
            headers=headers,
            json=update_data
        )
        logger.info(f"Grafana API response: status={response.status_code}, content={response.text}");
        response.raise_for_status()
        
        logger.info(f"Successfully updated Grafana CloudWatch datasource '{datasource_name}'")
        
    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP error while updating Grafana datasource: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error updating Grafana datasource: {str(e)}")
        raise

def rotate_access_key(target_username, rotation_period, datasource_name):
    """Rotate access keys for a specific user"""
    try:
        # Get access keys for the target user
        try:
            access_keys = iam.list_access_keys(UserName=target_username)
        except iam.exceptions.NoSuchEntityException:
            logger.error(f"User {target_username} does not exist")
            return {
                'statusCode': 404,
                'body': f'User {target_username} does not exist'
            }
            
        # If no access keys exist, create one
        if not access_keys['AccessKeyMetadata']:
            logger.info(f"No access keys found for user {target_username}, creating new key")
            new_key_response = iam.create_access_key(UserName=target_username)
            new_key = new_key_response['AccessKey']
            
            # Update Grafana datasource with new credentials
            update_grafana_datasource(new_key['AccessKeyId'], new_key['SecretAccessKey'], datasource_name)
            
            logger.info(f"Created initial access key for user {target_username}")
            return {
                'statusCode': 200,
                'body': f'Created initial access key for user {target_username}'
            }
            
        for key in access_keys['AccessKeyMetadata']:
            key_id = key['AccessKeyId']
            create_date = key['CreateDate']
            status = key['Status']
            
            # Calculate key age
            key_age = (datetime.now(create_date.tzinfo) - create_date).days
            
            # Log key status
            logger.info(f"Key {key_id}: {status}, age: {key_age} days")
            
            # If key is older than rotation period and active, rotate it
            if key_age > rotation_period and status == 'Active':
                logger.info(f"Key {key_id} needs rotation (older than {rotation_period} days)")
                
                # First deactivate the old key
                iam.update_access_key(
                    UserName=target_username,
                    AccessKeyId=key_id,
                    Status='Inactive'
                )
                logger.info(f"Key {key_id} deactivated")
                
                # Delete the old key
                iam.delete_access_key(
                    UserName=target_username,
                    AccessKeyId=key_id
                )
                logger.info(f"Key {key_id} deleted")
                
                # Now create the new key
                new_key_response = iam.create_access_key(UserName=target_username)
                new_key = new_key_response['AccessKey']
                logger.info(f"New key created for {target_username}")
                
                # Update Grafana datasource with new credentials
                update_grafana_datasource(new_key['AccessKeyId'], new_key['SecretAccessKey'], datasource_name)
                
                logger.info(f"Rotation completed for key {key_id}")
            else:
                logger.info(f"Key {key_id} does not need rotation")
                
        return {
            'statusCode': 200,
            'body': f'IAM key rotation completed successfully for user {target_username}'
        }
        
    except Exception as e:
        logger.error(f"Error rotating IAM keys: {str(e)}")
        raise

def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
    """
    Lambda function to rotate IAM access keys for a specific user.
    """
    try:
        # Get configuration from environment variables
        rotation_period = int(os.environ.get('ROTATION_PERIOD', 30))
        target_username = os.environ.get('IAM_USERNAME')
        datasource_name = os.environ.get('GRAFANA_DATASOURCE_NAME')
        
        logger.info("Starting with configuration: rotation_period=%d days, target_username=%s, target_datasource=%s", 
                   rotation_period, target_username, datasource_name)
        
        # Validate required environment variables
        if not target_username:
            logger.error("IAM_USERNAME environment variable is not set")
            return {
                'statusCode': 400,
                'body': 'IAM_USERNAME environment variable is required'
            }
            
        if not datasource_name:
            logger.error("GRAFANA_DATASOURCE_NAME environment variable is not set")
            return {
                'statusCode': 400,
                'body': 'GRAFANA_DATASOURCE_NAME environment variable is required'
            }
        
        # Perform the key rotation
        return rotate_access_key(target_username, rotation_period, datasource_name)
        
    except Exception as e:
        logger.error(f"Unexpected error in Lambda handler: {str(e)}")
        raise 