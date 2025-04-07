{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
				"lambda:ListFunctions",
				"lambda:ListLayers",
				"lambda:ListLayerVersions",
				"lambda:ListAliases",
				"lambda:ListVersionsByFunction",
				"lambda:ListProvisionedConcurrencyConfigs",
				"lambda:ListEventSourceMappings",
				"lambda:ListFunctionEventInvokeConfigs",
				"lambda:ListFunctionsByCodeSigningConfig",
				"lambda:ListTags",
				"cloudwatch:PutMetricData"
            ],
            "Resource": "*"
        }
    ]
}