job_template = """
apiVersion: batch/v1
kind: Job
metadata:
  name: {{ name }}
  namespace: {{ namespace }}
  labels:
    app: {{ name }}
spec:
  ttlSecondsAfterFinished: 10
  template:
    spec:
      nodeSelector:
        nodes: workers
      containers:
      - name: support
        image: busybox
        imagePullPolicy: Always
        command:
        - sleep
        - infinity
        resources:
          requests:
            cpu: "1"
            memory: {{ size }}
          limits:
            cpu: "1"
            memory: {{ size }}
      restartPolicy: Never
"""
