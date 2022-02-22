import vc_utils
from datetime import datetime

url = "vc1.cam.ciscolabs.com"
username = "administrator@vsphere.local"
pwd = "123Cisco123!"

si = vc_utils.connect(url,username,pwd,"443")
datacenter = vc_utils.get_dc(si, "STLD")
datastore = vc_utils.get_ds(datacenter, "ESX1i-RAID5_1")
resource_pool = vc_utils.get_largest_free_rp(si, datacenter)
ovf_handle = vc_utils.OvfHandler("/nfs-share/www/akb/test.ova")
ovf_manager = si.content.ovfManager
cisp = vc_utils.import_spec_params()

cisr = ovf_manager.CreateImportSpec(ovf_handle.get_descriptor(), resource_pool, datastore, cisp)
if cisr.error:
    print("The following errors will prevent import of this OVA:")
    for error in cisr.error:
        print("%s" % error)

ovf_handle.set_spec(cisr)

#print(vc_utils.start_upload(url, resource_pool,cisr, datacenter, ovf_handle))
print(datacenter.vmFolder.childEntity)
vm = vc_utils.find_by_name(si,datacenter.vmFolder,"test_deploy")
print(vm)
task = vm.CreateSnapshot_Task(name=str(datetime.now()),
                              description="Snapshot",
                              memory=False,
                              quiesce=False)