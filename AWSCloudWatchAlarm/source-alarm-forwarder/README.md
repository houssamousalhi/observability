# AWS CloudWatch Alarm Forwarder

This Lambda function monitors CloudWatch alarms and forwards their states to CloudWatch metrics, providing detailed insights into alarm states across different AWS resources.

## Features

- Tracks alarms in three states: ALARM, OK, and INSUFFICIENT_DATA
- Groups alarms by resource type (SQS, Lambda, etc.)
- Provides detailed metrics for each resource type
- Extracts resource information from both dimensions and metrics
- Supports JSON-formatted alarm descriptions

## Running Tests

### Prerequisites
- Python 3.13 (recommended)
- pip (Python package manager)
- pytest
- Homebrew (for macOS users)

### Setup

1. Install Python 3.13 (if not already installed):
```bash
# For macOS users
brew install python@3.13
```

2. Create and activate a virtual environment:
```bash
# Navigate to the project directory
cd AWSCloudWatchAlarm/source-alarm-forwarder

# Create virtual environment
python3.13 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running Tests

To run the tests, use pytest:

```bash
python -m pytest tests/test_lambda_function.py -v
```

This will run all tests with verbose output.

### Environment Management

To work with the project:

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Deactivate when done:
```bash
deactivate
```

### CloudWatch Metrics

The function publishes the following metrics to CloudWatch:

1. Resource Type Level Metrics:
   - `ResourceTypeAlarmsInAlarmState`: Number of alarms in ALARM state
   - `ResourceTypeAlarmsInOkState`: Number of alarms in OK state
   - `ResourceTypeAlarmsInInsufficientState`: Number of alarms in INSUFFICIENT_DATA state

2. Individual Alarm Metrics:
   - `ActiveAlarm`: Individual alarm metrics with detailed dimensions

### Requirements

The project dependencies are listed in `requirements.txt`:
- boto3>=1.26.79
- pytest>=8.3.5

### Troubleshooting

If you encounter any issues:

1. Ensure you're using the correct Python environment:
```bash
which python
```

2. Verify pytest is installed:
```bash
pip list | grep pytest
```

3. Check the test output for specific error messages 