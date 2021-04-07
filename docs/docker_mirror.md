# Docker Mirror how to:

Use this command to start a mirror on a server:
```bash
sudo docker run \
  -d \
  -p 5000:5000 \
  --restart=always \
  --name=through-cache \
  -e REGISTRY_PROXY_REMOTEURL="https://registry-1.docker.io" \
  -e REGISTRY_PROXY_USERNAME=XXXXXX \
  -e REGISTRY_PROXY_PASSWORD=XXXXXX \
registry
```

* REGISTRY_PROXY_USERNAME: Is your docker hub username
* REGISTRY_PROXY_PASSWORD: Is the Docekr hub access Token that you can generate from [here](https://hub.docker.com/settings/security?ref=login)

Then you need to tell CRIO or Docker to use it by setting this in the registries.conf file. Check the [registries.conf template](../ansible/roles/k8s_nodes/templates/registries.conf) for and example.
