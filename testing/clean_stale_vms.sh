export VALIDATE_CERTS="no"
export GOVC_INSECURE="1"
while read -r line; 
do
    export GOVC_URL=$line
    echo -n "Ensure nkt VMs are not present on: " 
    echo $GOVC_URL | cut -d"@" -f3
    for VM in `govc find / -type m -name "gitaction-nkt-*"`
    do
        govc vm.destroy $VM
    done
done < /home/cisco/Coding/akb/testing/virtual_centers.inv