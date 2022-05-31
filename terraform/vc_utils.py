from pyVmomi import vim, vmodl
from pyVim import connect as vc_connect
import os
import tarfile
import time
from threading import Timer
import ssl
from urllib.request import Request, urlopen
import sys

def connect(url, username, vc_pass, port):
    return vc_connect.SmartConnectNoSSL(host=url,  user=username, pwd=vc_pass, port=port)

def disconnect(si):
    vc_connect.Disconnect(si)
    return

def get_all_dcs(si):
    content = si.RetrieveContent()
    obj = {}
    container = content.viewManager.CreateContainerView(
        content.rootFolder, [vim.Datacenter], True)
    for managed_object_ref in container.view:
        obj.update({managed_object_ref: managed_object_ref.name})
    return obj

def get_dc(si, name):
    for datacenter in si.content.rootFolder.childEntity:
        if datacenter.name == name:
            return datacenter
    raise Exception('Failed to find datacenter named %s' % name)


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

def find_vms(obj, vms, note = ""):
    ''' Find VMs optionally filtering by note'''
    if isinstance(obj, vim.Datacenter):
        for child in obj.vmFolder.childEntity:
            if (isinstance(child, vim.VirtualMachine)):
                if note == "":
                    vms.append(child)
                elif (child.config) and child.config.annotation == note:
                    vms.append(child)
            elif(isinstance(child, vim.Folder)):
                find_vms(child, vms, note)
    elif isinstance(obj, vim.Folder):
        for child in obj.childEntity:
            if (isinstance(child, vim.VirtualMachine)):
                if note == "":
                    vms.append(child)
                elif (child.config) and child.config.annotation == note:
                    vms.append(child)
            elif(isinstance(child, vim.Folder)):
                find_vms(child, vms, note)
    
def find_by_name(si, folder,vm_name):
    return si.content.searchIndex.FindChild(folder, vm_name)

def find_compute_cluster(obj):
    if (isinstance(obj, vim.ClusterComputeResource)):
        return obj
    else: 
        return None

def find_folders(obj):
    if (isinstance(obj, vim.Folder)):
        return obj
    else: 
        return None

def wait_for_tasks(service_instance, tasks):
    """Given the service instance si and tasks, it returns after all the
   tasks are complete
   """
    property_collector = service_instance.content.propertyCollector
    task_list = [str(task) for task in tasks]
    # Create filter
    obj_specs = [vmodl.query.PropertyCollector.ObjectSpec(obj=task)
                 for task in tasks]
    property_spec = vmodl.query.PropertyCollector.PropertySpec(type=vim.Task,
                                                               pathSet=[],
                                                               all=True)
    filter_spec = vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = obj_specs
    filter_spec.propSet = [property_spec]
    pcfilter = property_collector.CreateFilter(filter_spec, True)
    try:
        version, state = None, None
        # Loop looking for updates till the state moves to a completed state.
        while len(task_list):
            update = property_collector.WaitForUpdates(version)
            for filter_set in update.filterSet:
                for obj_set in filter_set.objectSet:
                    task = obj_set.obj
                    for change in obj_set.changeSet:
                        if change.name == 'info':
                            state = change.val.state
                        elif change.name == 'info.state':
                            state = change.val
                        else:
                            continue

                        if not str(task) in task_list:
                            continue

                        if state == vim.TaskInfo.State.success:
                            # Remove task from taskList
                            task_list.remove(str(task))
                        elif state == vim.TaskInfo.State.error:
                            raise task.info.error
            # Move to next version
            version = update.version
    finally:
        if pcfilter:
            pcfilter.Destroy()

def import_spec_params(entityName,diskProvisioning, hostSystem):
    return vim.OvfManager.CreateImportSpecParams(entityName=entityName, diskProvisioning=diskProvisioning, hostSystem=hostSystem)

def get_largest_free_rp(si, datacenter):
    """
    Get the resource pool with the largest unreserved memory for VMs.
    """
    view_manager = si.content.viewManager
    container_view = view_manager.CreateContainerView(datacenter, [vim.ResourcePool], True)
    largest_rp = None
    unreserved_for_vm = 0
    try:
        for resource_pool in container_view.view:
            if resource_pool.runtime.memory.unreservedForVm > unreserved_for_vm:
                largest_rp = resource_pool
                unreserved_for_vm = resource_pool.runtime.memory.unreservedForVm
    finally:
        container_view.Destroy()
    if largest_rp is None:
        raise Exception("Failed to find a resource pool in datacenter %s" % datacenter.name)
    return largest_rp

def start_upload(url, resource_pool,cisr, folder, ovf_handle, host):
    lease = resource_pool.ImportVApp(cisr.importSpec, folder, host)
    while lease.state == vim.HttpNfcLease.State.initializing:
        print("Waiting for lease to be ready...")
        time.sleep(1)

    if lease.state == vim.HttpNfcLease.State.error:
        print("Lease error: %s" % lease.error)
        return 1
    if lease.state == vim.HttpNfcLease.State.done:
        return 0

    print("Starting deploy...")
    return ovf_handle.upload_disks(lease, url)

# This comes from https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/deploy_ova.py
def get_ds(datacenter, name):
    """
    Pick a datastore by its name.
    """
    for datastore in datacenter.datastore:
        try:
            if datastore.name == name:
                return datastore
        except Exception:  # Ignore datastores that have issues
            pass
    raise Exception("Failed to find %s on datacenter %s" % (name, datacenter.name))

def get_tarfile_size(tarfile):
    """
    Determine the size of a file inside the tarball.
    If the object has a size attribute, use that. Otherwise seek to the end
    and report that.
    """
    if hasattr(tarfile, 'size'):
        return tarfile.size
    size = tarfile.seek(0, 2)
    tarfile.seek(0, 0)
    return size

class OvfHandler(object):
    """
    OvfHandler handles most of the OVA operations.
    It processes the tarfile, matches disk keys to files and
    uploads the disks, while keeping the progress up to date for the lease.
    """

    # class variables
    upload_progress = 0

    # class functions

    def __init__(self, ovafile):
        """
        Performs necessary initialization, opening the OVA file,
        processing the files and reading the embedded ovf file.
        """
        self.handle = self._create_file_handle(ovafile)
        self.tarfile = tarfile.open(fileobj=self.handle)
        ovffilename = list(filter(lambda x: x.endswith(".ovf"),
                                  self.tarfile.getnames()))[0]
        ovffile = self.tarfile.extractfile(ovffilename)
        self.descriptor = ovffile.read().decode()

    def _create_file_handle(self, entry):
        """
        A simple mechanism to pick whether the file is local or not.
        This is not very robust.
        """
        if os.path.exists(entry):
            return FileHandle(entry)

    def get_descriptor(self):
        return self.descriptor

    def set_spec(self, spec):
        """
        The import spec is needed for later matching disks keys with
        file names.
        """
        self.spec = spec

    def get_disk(self, file_item):
        """
        Does translation for disk key to file name, returning a file handle.
        """
        ovffilename = list(filter(lambda x: x == file_item.path,
                                  self.tarfile.getnames()))[0]
        return self.tarfile.extractfile(ovffilename)

    def get_device_url(self, file_item, lease):
        for device_url in lease.info.deviceUrl:
            if device_url.importKey == file_item.deviceId:
                return device_url
        raise Exception("Failed to find deviceUrl for file %s" % file_item.path)

    def upload_disks(self, lease, host):
        """
        Uploads all the disks, with a progress keep-alive.
        """
        self.lease = lease
        try:
            self.start_timer()
            for fileItem in self.spec.fileItem:
                #print(fileItem)
                # Do not upload nvram files that makes OVA Upload fail on ESXi 6.7
                if "nvram" not in fileItem.path:
                    self.upload_disk(fileItem, lease, host)
            lease.Complete()
            print("Finished deploy successfully.")
            return 0
        except vmodl.MethodFault as ex:
            print("Hit an error in upload: %s" % ex)
            lease.Abort(ex)
        except Exception as ex:
            print("Lease: %s" % lease.info)
            print("Hit an error in upload: %s" % ex)
            lease.Abort(vmodl.fault.SystemError(reason=str(ex)))
        return 1

    def upload_disk(self, file_item, lease, host):
        """
        Upload an individual disk. Passes the file handle of the
        disk directly to the urlopen request.
        """
        ovffile = self.get_disk(file_item)
        if ovffile is None:
            return
        device_url = self.get_device_url(file_item, lease)
        url = device_url.url.replace('*', host)
        headers = {'Content-length': get_tarfile_size(ovffile)}
        if hasattr(ssl, '_create_unverified_context'):
            ssl_context = ssl._create_unverified_context()
        else:
            ssl_context = None
        req = Request(url, ovffile, headers)
        urlopen(req, context=ssl_context)

    def start_timer(self):
        """
        A simple way to keep updating progress while the disks are transferred.
        """
        Timer(5, self.timer).start()

    def timer(self):
        """
        Update the progress and reschedule the timer if not complete.
        """
        try:
            prog = self.handle.progress()
            self.lease.Progress(prog)
            if self.lease.state not in [vim.HttpNfcLease.State.done,
                                        vim.HttpNfcLease.State.error]:
                self.start_timer()
            sys.stderr.write("Progress: %d%%\r" % prog)
            self.upload_progress = prog
            return prog
        except Exception:  # Any exception means we should stop updating progress.
            pass
    
    def get_upload_progress(self):
        """
        Return the value of the upload_progress member variable.
        """
        return self.upload_progress


class FileHandle(object):
    def __init__(self, filename):
        self.filename = filename
        self.fh = open(filename, 'rb')

        self.st_size = os.stat(filename).st_size
        self.offset = 0

    def __del__(self):
        self.fh.close()

    def tell(self):
        return self.fh.tell()

    def seek(self, offset, whence=0):
        if whence == 0:
            self.offset = offset
        elif whence == 1:
            self.offset += offset
        elif whence == 2:
            self.offset = self.st_size - offset

        return self.fh.seek(offset, whence)

    def seekable(self):
        return True

    def read(self, amount):
        self.offset += amount
        result = self.fh.read(amount)
        return result

    # A slightly more accurate percentage
    def progress(self):
        return int(100.0 * self.offset / self.st_size)