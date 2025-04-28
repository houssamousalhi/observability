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
      "id": "stat",
      "name": "Stat",
      "version": ""
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
            "mode": "fixed"
          },
          "fieldMinMax": false,
          "mappings": [],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              },
              {
                "color": "dark-red",
                "value": 1
              }
            ]
          }
        },
        "overrides": [
          {
            "matcher": {
              "id": "byName",
              "options": "In alarm"
            },
            "properties": [
              {
                "id": "color"
              }
            ]
          },
          {
            "matcher": {
              "id": "byName",
              "options": "OK"
            },
            "properties": [
              {
                "id": "color",
                "value": {
                  "fixedColor": "green",
                  "mode": "fixed"
                }
              }
            ]
          }
        ]
      },
      "gridPos": {
        "h": 4,
        "w": 24,
        "x": 0,
        "y": 0
      },
      "id": 3,
      "maxPerRow": 6,
      "options": {
        "colorMode": "background",
        "graphMode": "area",
        "justifyMode": "center",
        "orientation": "vertical",
        "percentChangeColorMode": "standard",
        "reduceOptions": {
          "calcs": [
            "lastNotNull"
          ],
          "fields": "",
          "values": false
        },
        "showPercentChange": false,
        "textMode": "value_and_name",
        "wideLayout": false
      },
      "pluginVersion": "12.0.0-86517.patch1-86795",
      "repeat": "resourceType",
      "repeatDirection": "h",
      "targets": [
        {
          "datasource": {
            "type": "cloudwatch",
            "uid": "$${datasource}"
          },
          "dimensions": {
            "ResourceType": "$resourceType"
          },
          "expression": "",
          "filters": [
            {
              "key": "AlarmState",
              "operator": "=",
              "value": "$status"
            }
          ],
          "hide": false,
          "id": "",
          "label": "In alarm",
          "logGroups": [],
          "matchExact": false,
          "metricEditorMode": 0,
          "metricName": "ResourceTypeAlarmsInAlarmState",
          "metricQueryType": 0,
          "namespace": "${cloudwatch_namespace}",
          "period": "",
          "queryLanguage": "CWLI",
          "queryMode": "Metrics",
          "refId": "C",
          "region": "default",
          "sqlExpression": "",
          "statistic": "Maximum"
        },
        {
          "datasource": {
            "uid": "$${datasource}"
          },
          "dimensions": {
            "ResourceType": "$resourceType"
          },
          "expression": "",
          "filters": [
            {
              "key": "AlarmState",
              "operator": "=",
              "value": "$status"
            }
          ],
          "id": "",
          "label": "OK",
          "logGroups": [],
          "matchExact": false,
          "metricEditorMode": 0,
          "metricName": "ResourceTypeAlarmsInOkState",
          "metricQueryType": 0,
          "namespace": "${cloudwatch_namespace}",
          "period": "",
          "queryLanguage": "CWLI",
          "queryMode": "Metrics",
          "refId": "A",
          "region": "default",
          "sqlExpression": "",
          "statistic": "Maximum"
        },
        {
          "datasource": {
            "type": "cloudwatch",
            "uid": "$${datasource}"
          },
          "dimensions": {
            "ResourceType": "$resourceType"
          },
          "expression": "",
          "filters": [
            {
              "key": "AlarmState",
              "operator": "=",
              "value": "$status"
            }
          ],
          "hide": false,
          "id": "",
          "label": "Insufficient data",
          "logGroups": [],
          "matchExact": false,
          "metricEditorMode": 0,
          "metricName": "ResourceTypeAlarmsInInsufficientState",
          "metricQueryType": 0,
          "namespace": "${cloudwatch_namespace}",
          "period": "",
          "queryLanguage": "CWLI",
          "queryMode": "Metrics",
          "refId": "B",
          "region": "default",
          "sqlExpression": "",
          "statistic": "Maximum"
        }
      ],
      "title": "$resourceType Alarms",
      "type": "stat"
    },
    {
      "datasource": {
            "uid": "$${datasource}"
      },
      "fieldConfig": {
        "defaults": {
          "color": {
            "fixedColor": "text",
            "mode": "fixed"
          },
          "custom": {
            "axisPlacement": "auto",
            "fillOpacity": 82,
            "hideFrom": {
              "legend": false,
              "tooltip": false,
              "viz": false
            },
            "insertNulls": 300000,
            "lineWidth": 0,
            "spanNulls": false
          },
          "fieldMinMax": false,
          "mappings": [
            {
              "options": {
                "1": {
                  "color": "dark-red",
                  "index": 0,
                  "text": "ALARM"
                }
              },
              "type": "value"
            },
            {
              "options": {
                "match": "null",
                "result": {
                  "color": "green",
                  "index": 1,
                  "text": "OK"
                }
              },
              "type": "special"
            }
          ],
          "thresholds": {
            "mode": "absolute",
            "steps": [
              {
                "color": "green"
              }
            ]
          }
        },
        "overrides": []
      },
      "gridPos": {
        "h": 11,
        "w": 24,
        "x": 0,
        "y": 4
      },
      "id": 2,
      "options": {
        "alignValue": "left",
        "legend": {
          "displayMode": "list",
          "placement": "bottom",
          "showLegend": true
        },
        "mergeValues": true,
        "rowHeight": 0.44,
        "showValue": "never",
        "tooltip": {
          "hideZeros": false,
          "mode": "single",
          "sort": "none"
        }
      },
      "pluginVersion": "12.0.0-86517.patch1-86795",
      "targets": [
        {
          "datasource": {
            "type": "cloudwatch",
            "uid": "$${datasource}"
          },
          "dimensions": {
            "ResourceType": "$resourceType"
          },
          "expression": "",
          "filters": [
            {
              "key": "AlarmState",
              "operator": "=",
              "value": "$status"
            }
          ],
          "id": "",
          "label": "$${PROP(\"Dim.AlarmName\")}",
          "logGroups": [],
          "matchExact": false,
          "metricEditorMode": 0,
          "metricName": "ActiveAlarm",
          "metricQueryType": 0,
          "namespace": "${cloudwatch_namespace}",
          "period": "",
          "queryLanguage": "CWLI",
          "queryMode": "Metrics",
          "refId": "A",
          "region": "default",
          "sqlExpression": "",
          "statistic": "Maximum"
        }
      ],
      "title": "Fired Alarm",
      "type": "state-timeline"
    }
  ],
  "refresh": "",
  "schemaVersion": 41,
  "tags": [
    "AWS",
    "cloudwatch",
    "alarms"
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
        "includeAll": true,
        "label": "ResourceType",
        "multi": true,
        "name": "resourceType",
        "options": [],
        "query": {
          "dimensionFilters": {},
          "dimensionKey": "ResourceType",
          "metricName": "ResourceTypeAlarmsInAlarmState",
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
  "title": "CloudWatch Alarms",
  "uid": "aws-cloudwatch-alarms",
  "version": 1,
  "weekStart": ""
}
