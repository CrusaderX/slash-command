#!/bin/bash

openssl genrsa -out ca.key 2048
openssl req -new -x509 -days 365 -key ca.key -subj "/C=BY/ST=Minsk/L=Minsk/O=default/CN=app-scaler.default.sv.cluster.localc" -out ca.crt
openssl req -newkey rsa:2048 -nodes -keyout server.key -subj "/C=BY/ST=Minsk/L=Minsk/O=default/CN=app-scaler.default.sv.cluster.localc" -out server.csr
openssl x509 -req -extfile <(printf "subjectAltName=DNS:app-scaler.default.svc.cluster.local") -days 365 -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt

kubectl create secret generic scaler -n default --from-file=key.pem=server.key --from-file=cert.pem=server.crt 