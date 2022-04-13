import json

with open("tmp.json", "r", encoding='utf8') as f:
    data=json.load(f)

for change in data['resource_changes']:
    if "module.k8s_node.vsphere_virtual_machine.vm" in change['address']:
        if "create" in change['change']['actions']:
            print(change['index'])
