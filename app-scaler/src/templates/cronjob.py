cronjob_template = """
apiVersion: batch/v1
kind: CronJob
metadata:
  name: dev-scaler
  namespace: {{ namespace }}
  labels:
    app: dev-scaler
spec:
  schedule: "0 17 * * 1-5"
  concurrencyPolicy: Forbid
  failedJobsHistoryLimit: 1
  successfulJobsHistoryLimit: 0
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - image: curlimages/curl:7.85.0 
            args: 
            - /bin/sh
            - -c
            - "curl -XPOST http://app-scaler.default.svc.cluster.local/api/v1/stop -H 'Content-Type: application/json' -d '{\\\"namespaces\\\": [\\\"{{ namespace }}\\\"], \\\"replicas\\\": \\\"0\\\"}'"
            name: curl
          restartPolicy: OnFailure
"""
