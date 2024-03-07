#!/bin/bash

kubectl apply -f k8s/volume/
kubectl apply -f k8s/redis/
kubectl apply -f k8s/ingestor/
kubectl apply -f k8s/analyzer/
kubectl apply -f k8s/webapp/
