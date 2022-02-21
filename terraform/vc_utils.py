from pyVmomi import vim
from pyVim import connect as vc_connect

def connect(url, username, vc_pass, port):
    
    return vc_connect.SmartConnectNoSSL(host=url,  user=username, pwd=vc_pass, port=port)

def disconnect(si):
    vc_connect.Disconnect(si)
    return

def get_all_objs(si):
    content = si.RetrieveContent()
    obj = {}
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.Datacenter], True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj


def find_pgs(obj, pgs):
    if isinstance(obj, vim.Datacenter):
        for child in obj.networkFolder.childEntity:
            if (isinstance(child, vim.DistributedVirtualSwitch)):
                pg_dvs = child.summary.name + "/"
                for pg in child.portgroup:
                    # Only accept access ports
                    if isinstance(pg.config.defaultPortConfig.vlan, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec):
                        vlan = "vlan-" + \
                            str(pg.config.defaultPortConfig.vlan.vlanId)
                        pgs.append(pg_dvs + pg.summary.name + "/" + vlan)
            elif(isinstance(child, vim.Folder)):
                find_pgs(child, pgs)
    elif isinstance(obj, vim.Folder):
        for child in obj.childEntity:
            if (isinstance(child, vim.DistributedVirtualSwitch)):
                pg_dvs = child.summary.name + "/"
                for pg in child.portgroup:
                    # Only accept access ports
                    if isinstance(pg.config.defaultPortConfig.vlan, vim.dvs.VmwareDistributedVirtualSwitch.VlanIdSpec):
                        vlan = "vlan-" + \
                            str(pg.config.defaultPortConfig.vlan.vlanId)
                        pgs.append(pg_dvs + pg.summary.name + "/" + vlan)
            elif(isinstance(child, vim.Folder)):
                find_pgs(child, pgs)


def find_vms(obj, vms):
    if isinstance(obj, vim.Datacenter):
        for child in obj.vmFolder.childEntity:
            if (isinstance(child, vim.VirtualMachine)):
                vms.append(child.name)
            elif(isinstance(child, vim.Folder)):
                find_vms(child, vms)
    elif isinstance(obj, vim.Folder):
        for child in obj.childEntity:
            if (isinstance(child, vim.VirtualMachine)):
                vms.append(child.name)
            elif(isinstance(child, vim.Folder)):
                find_vms(child, vms)

def find_compute_cluster(obj):
    if (isinstance(obj, vim.ClusterComputeResource)):
        return obj
    else: 
        return None


def find_folder(obj):
    if (isinstance(obj, vim.ClusterComputeResource)):
        return obj
    else: 
        return None