import boto3
import os

CLOUDWATCH_NAMESPACE = os.environ.get('CLOUDWATCH_NAMESPACE')

def lambda_handler(event, context):
    lambda_client = boto3.client('lambda')
    cloudwatch_client = boto3.client('cloudwatch')
    paginator = lambda_client.get_paginator('list_functions')
    services = set()
    
    for page in paginator.paginate():
        for function in page['Functions']:
            function_name = function['FunctionName'] 
            try:
                tags = lambda_client.list_tags(Resource=function['FunctionArn']).get('Tags', {})
                if 'AppVersion' in tags:
                    app_version = tags['AppVersion']
                    stack = tags.get('Stack', 'Unknown')
                    service = tags.get('Stack', 'Unknown') + '-' + tags.get('Service', 'Unknown')
                    env = tags.get('Environment', 'Unknown')
                    terraform = tags.get('TerraformVersion', 'Unknown')    
                    services.add((env, service, stack, terraform))
                    
                    dimensions = [
                        {'Name': 'Env', 'Value': str(env)},
                        {'Name': 'Service', 'Value': str(service)},
                        {'Name': 'Stack', 'Value': str(stack)},
                        {'Name': 'FunctionName', 'Value': function_name}
                    ] 
                    cloudwatch_client.put_metric_data(
                        Namespace=CLOUDWATCH_NAMESPACE,
                        MetricData=[
                            {
                                'MetricName': 'lambdaTag',
                                'Dimensions': dimensions + [{'Name': 'AppVersion', 'Value': str(app_version)}],
                                'Value': 1,
                                'Unit': 'Count'
                            }
                        ]
                    )
                    print(f"Published metric for {function_name} AppVersion {app_version}, Stack {stack}")
            except Exception as e:
                print(f"Error processing function {function_name}: {e}")
    

    for env, service, stack, terraform in services:
        dimensions = [
            {'Name': 'Env', 'Value': str(env)},
            {'Name': 'Service', 'Value': str(service)},
            {'Name': 'Stack', 'Value': str(stack)},
            {'Name': 'TerraformVersion', 'Value': str(terraform)}
        ]
        
        cloudwatch_client.put_metric_data(
            Namespace=CLOUDWATCH_NAMESPACE,
            MetricData=[
                {
                    'MetricName': 'terraformTag',
                    'Dimensions': dimensions,
                    'Value': 1,
                    'Unit': 'Count'
                }
            ]
        )
        print(f"Published terraformTag metric for Service {service}, Stack {stack} , Env {env} , TerraformVersion {terraform}")
    
    return {
        'statusCode': 200,
        'body': 'Metrics updated successfully'
    }
