#!/bin/bash
docker build -t quay.io/camillo/vkaci-init --target=vkaci-init  . &&  docker build -t quay.io/camillo/vkaci --target=vkaci .  &&  docker push quay.io/camillo/vkaci:latest &&  docker push quay.io/camillo/vkaci-init:latest
