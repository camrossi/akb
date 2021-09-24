# Calico ACI Integration Visibility

This Utility container will help locate the end to end connectivity for a POD.
You pass the POD name and you get infos on:

- The K8s node where the pod is running on.
- To which interface profile is the Node IP learned on ACI
- The LLDP neighbors discovered from the Physical interfaces member of the interface profile

## Installation

- apply the `list-permission.yaml` this will allow the `ServiceAccount` `default` to list pod.
- apply the `vkaci.yaml` this spin up the container that will run our tasks

## How to use

Once the pod is running you can just run this:

- `kubectl exec -it vkaci -- visibility.py <pod_name>`

## Example

```bash
  kubectl exec -it vkaci -- visibility.py vkaci
  Looking for pod vkaci with IP 10.1.203.0 on node 192.168.2.8
  The K8s Node is physically connected to: topology/pod-1/protpaths-203-204/pathep-[esxi4_vpc_vmnic2-3_PolGrp]
  LLDP Infos:
    topology/pod-1/node-203 eth1/1
      esxi4.cam.ciscolabs.com
    topology/pod-1/node-204 eth1/1
      esxi4.cam.ciscolabs.com
  BGP Peer:
    node-201
    node-202
```

## Tip

Make an alias, just use set the namespace to what you need.

```bash
 alias vkaci='kubectl -n default exec -it vkaci -- visibility.py"
 ```

 now you can simply do `vkaci <pod_name>`
