{
  "__inputs": [],
  "__elements": {},
  "__requires": [
    {
      "type": "datasource",
      "id": "cloudwatch",
      "name": "CloudWatch",
      "version": "1.0.0"
    },
    {
      "type": "grafana",
      "id": "grafana",
      "name": "Grafana",
      "version": "12.0.0-85518.patch7-85777"
    },
    {
      "type": "datasource",
      "id": "prometheus",
      "name": "Prometheus",
      "version": "1.0.0"
    },
    {
      "type": "panel",
      "id": "state-timeline",
      "name": "State timeline",
      "version": ""
    }
  ],
  "annotations": {
    "list": [
      {
        "builtIn": 1,
        "datasource": {
          "type": "grafana",
          "uid": "-- Grafana --"
        },
        "enable": true,
        "hide": true,
        "iconColor": "rgba(0, 211, 255, 1)",
        "name": "Annotations & Alerts",
        "type": "dashboard"
      }
    ]
  },
  "editable": true,
  "fiscalYearStartMonth": 0,
  "graphTooltip": 1,
  "id": null,
  "links": [],
  "panels": [
    {
      "datasource": {
        "type": "cloudwatch",
        "uid": "$${datasource}"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "dark-green",
            "mode": "palette-classic-by-name"
          },
          "custom": {
            "axisPlacement": "auto",
            "fillOpacity": 43,
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": 300000,
            "lineWidth": 1,
            "spanNulls": true
          },
          "fieldMinMax": false,
          "mappings": [],
          "max": 1,
          "min": 0,
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "Value"
            },
            "properties": [
              {
                "id": "custom.hideFrom",
                "value": {
                  "legend": true,
                  "tooltip": true,
                  "viz": true
                }
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 9,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 2,
      "options": {
        "alignValue": "center",
        "legend": {
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": false
        },
        "mergeValues": true,
        "rowHeight": 0.66,
        "showValue": "always",
        "tooltip": {
          "hideZeros": false,
          "mode": "single",
          "sort": "none"
        }
      },
      "pluginVersion": "12.0.0-85518.patch7-85777",
      "repeat": "service",
      "repeatDirection": "v",
      "targets": [
        {
          "datasource": {
            "type": "cloudwatch",
            "uid": "$${datasource}"
          },
          "dimensions": {
            "Env": "$${env}",
            "Service": "$${service}",
            "TerraformVersion": "*"
          },
          "hide": false,
          "id": "",
          "label": " ",
          "logGroups": [],
          "matchExact": false,
          "metricEditorMode": 0,
          "metricName": "terraformTag",
          "metricQueryType": 0,
          "namespace": "${cloudwatch_namespace}",
          "period": "",
          "queryLanguage": "CWLI",
          "queryMode": "Metrics",
          "refId": "A",
          "region": "default",
          "sql": {
            "from": {
              "name": "SCHEMA",
              "parameters": [
                {
                  "name": "AppVersion",
                  "type": "functionParameter"
                },
                {
                  "name": "Stack",
                  "type": "functionParameter"
                }
              ],
              "type": "function"
            },
            "select": {
              "name": "COUNT",
              "parameters": [
                {
                  "name": "*",
                  "type": "functionParameter"
                }
              ],
              "type": "function"
            }
          },
          "sqlExpression": "SELECT COUNT(*) FROM SCHEMA(AppVersion, Stack)",
          "statistic": "SampleCount"
        },
        {
          "datasource": {
            "type": "cloudwatch",
            "uid": "$${datasource}"
          },
          "dimensions": {
            "AppVersion": "*",
            "Env": "$${env}",
            "FunctionName": "*",
            "Service": "$${service}"
          },
          "hide": false,
          "id": "service",
          "label": "$${PROP(\"Dim.FunctionName\")}",
          "logGroups": [],
          "matchExact": false,
          "metricEditorMode": 0,
          "metricName": "lambdaTag",
          "metricQueryType": 0,
          "namespace": "${cloudwatch_namespace}",
          "period": "",
          "queryLanguage": "CWLI",
          "queryMode": "Metrics",
          "refId": "B",
          "region": "default",
          "sql": {
            "from": {
              "name": "SCHEMA",
              "parameters": [
                {
                  "name": "AppVersion",
                  "type": "functionParameter"
                },
                {
                  "name": "Stack",
                  "type": "functionParameter"
                }
              ],
              "type": "function"
            },
            "select": {
              "name": "COUNT",
              "parameters": [
                {
                  "name": "*",
                  "type": "functionParameter"
                }
              ],
              "type": "function"
            }
          },
          "sqlExpression": "SELECT COUNT(*) FROM SCHEMA(AppVersion, Stack)",
          "statistic": "SampleCount"
        }
      ],
      "title": "Timeline $${service}",
      "transformations": [
        {
          "filter": {
            "id": "byRefId",
            "options": ""
          },
          "id": "labelsToFields",
          "options": {
            "keepLabels": [
              "TerraformVersion",
              "AppVersion"
            ],
            "mode": "columns",
            "valueLabel": "FunctionName"
          },
          "topic": "series"
        },
        {
          "filter": {
            "id": "byRefId",
            "options": "/^(?:A)$/"
          },
          "id": "merge",
          "options": {
            "groupBy": [
              "FunctionName"
            ],
            "reducers": []
          },
          "topic": "series"
        }
      ],
      "type": "state-timeline"
    }
  ],
  "refresh": "",
  "schemaVersion": 41,
  "tags": [
    "AWS",
    "lambda",
    "cloudwatch"
  ],
  "templating": {
    "list": [
      {
        "current": {},
        "includeAll": false,
        "name": "datasource",
        "options": [],
        "query": "cloudwatch",
        "refresh": 1,
        "type": "datasource"
      },
      {
        "current": {},
        "datasource": {
          "type": "cloudwatch",
          "uid": "$${datasource}"
        },
        "definition": "",
        "label": "Env",
        "name": "env",
        "options": [],
        "query": {
          "dimensionFilters": {},
          "dimensionKey": "Env",
          "metricName": "terraformTag",
          "namespace": "${cloudwatch_namespace}",
          "queryType": "dimensionValues",
          "refId": "CloudWatchVariableQueryEditor-VariableQuery",
          "region": "default"
        },
        "refresh": 1,
        "regex": "",
        "type": "query"
      },
      {
        "current": {},
        "datasource": {
          "type": "cloudwatch",
          "uid": "$${datasource}"
        },
        "definition": "",
        "includeAll": true,
        "label": "Application",
        "multi": true,
        "name": "service",
        "options": [],
        "query": {
          "dimensionFilters": {
            "Env": "$${env}"
          },
          "dimensionKey": "Service",
          "metricName": "terraformTag",
          "namespace": "${cloudwatch_namespace}",
          "queryType": "dimensionValues",
          "refId": "CloudWatchVariableQueryEditor-VariableQuery",
          "region": "default"
        },
        "refresh": 1,
        "regex": "",
        "type": "query"
      }
    ]
  },
  "time": {
    "from": "now-7d",
    "to": "now"
  },
  "timepicker": {},
  "timezone": "browser",
  "title": "Lambda Inspector",
  "uid": "aws-lambda-inspector-cloudwatch",
  "version": 1,
  "weekStart": ""
}
