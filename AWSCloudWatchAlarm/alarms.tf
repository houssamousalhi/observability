# # SQS Queue Alarms
# resource "aws_cloudwatch_metric_alarm" "sqs_age_alarm" {
#   alarm_name          = "sqs-message-age-high"
#   comparison_operator = "GreaterThanThreshold"
#   evaluation_periods  = "2"
#   metric_name         = "ApproximateAgeOfOldestMessage"
#   namespace           = "AWS/SQS"
#   period              = "300"
#   statistic           = "Maximum"
#   threshold           = "3600" # 1 hour in seconds
#   alarm_description   = "This metric monitors the age of the oldest message in the queue"
#   treat_missing_data  = "notBreaching"

#   dimensions = {
#     QueueName = "your-queue-name" # Replace with your queue name
#   }
# }

# resource "aws_cloudwatch_metric_alarm" "sqs_dlq_messages" {
#   alarm_name          = "sqs-dlq-messages-present"
#   comparison_operator = "GreaterThanThreshold"
#   evaluation_periods  = "1"
#   metric_name         = "ApproximateNumberOfMessagesVisible"
#   namespace           = "AWS/SQS"
#   period              = "300"
#   statistic           = "Maximum"
#   threshold           = "0"
#   alarm_description   = "This metric monitors the number of messages in DLQ"
#   treat_missing_data  = "notBreaching"

#   dimensions = {
#     QueueName = "your-dlq-name" # Replace with your DLQ name
#   }
# }

# # Lambda Function Alarm
# resource "aws_cloudwatch_metric_alarm" "lambda_errors" {
#   alarm_name          = "lambda-error-rate-high"
#   comparison_operator = "GreaterThanThreshold"
#   evaluation_periods  = "2"
#   metric_name         = "Errors"
#   namespace           = "AWS/Lambda"
#   period              = "300"
#   statistic           = "Sum"
#   threshold           = "1"
#   alarm_description   = "This metric monitors lambda function errors"
#   treat_missing_data  = "notBreaching"

#   dimensions = {
#     FunctionName = "your-function-name" # Replace with your Lambda function name
#   }
# }

# # API Gateway Alarm
# resource "aws_cloudwatch_metric_alarm" "api_latency" {
#   alarm_name          = "api-latency-high"
#   comparison_operator = "GreaterThanThreshold"
#   evaluation_periods  = "3"
#   metric_name         = "Latency"
#   namespace           = "AWS/ApiGateway"
#   period              = "300"
#   statistic           = "Average"
#   threshold           = "1000" # 1 second in milliseconds
#   alarm_description   = "This metric monitors API Gateway latency"
#   treat_missing_data  = "notBreaching"

#   dimensions = {
#     ApiName = "your-api-name" # Replace with your API name
#     Stage   = "prod"          # Replace with your stage name
#   }
# } 