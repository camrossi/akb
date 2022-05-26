export VALIDATE_CERTS="no"
export GOVC_INSECURE="1"
echo "Ensure nkt VMs are not present" 
while read -r line; 
do
    export GOVC_URL=$line
    for VM in `govc find / -type m -name "gitaction-nkt-*"`
    do
        echo -n "Deleting VM:"
        echo $VM
        govc vm.destroy $VM
    done
done < /home/cisco/Coding/akb/testing/virtual_centers.inv
### The last line in virtual_centers.inv MUST be an empty line or we won't read the last vCenter!!!!