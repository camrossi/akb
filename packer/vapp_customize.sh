#!/bin/bash -x

if [ -e /root/ran_customization ]; then
    exit
else
    NETPLAN_CONFIG_FILE="/etc/netplan/01-netcfg.yaml"

    IP_ADDRESS_PROPERTY=$(vmtoolsd --cmd "info-get guestinfo.ovfEnv" | grep "guestinfo.ipaddress")
    GATEWAY_PROPERTY=$(vmtoolsd --cmd "info-get guestinfo.ovfEnv" | grep "guestinfo.gateway")
    DNS_SERVER_PROPERTY=$(vmtoolsd --cmd "info-get guestinfo.ovfEnv" | grep "guestinfo.dns")
    DNS_DOMAIN_PROPERTY=$(vmtoolsd --cmd "info-get guestinfo.ovfEnv" | grep "guestinfo.domain")

    ##################################
    ### No User Input, assume DHCP ###
    ##################################
    if [ -z "${IP_ADDRESS_PROPERTY}" ]; then
        cat > ${NETPLAN_CONFIG_FILE} << __CUSTOMIZE_NETPLAN__
network:
    version: 2
    renderer: networkd
    ethernets:
        ens160:
            dhcp4: true
__CUSTOMIZE_NETPLAN__
    #########################
    ### Static IP Address ###
    #########################
    else
        HOSTNAME=$(echo "${HOSTNAME_PROPERTY}" | awk -F 'oe:value="' '{print $2}' | awk -F '"' '{print $1}')
        IP_ADDRESS=$(echo "${IP_ADDRESS_PROPERTY}" | awk -F 'oe:value="' '{print $2}' | awk -F '"' '{print $1}')
        GATEWAY=$(echo "${GATEWAY_PROPERTY}" | awk -F 'oe:value="' '{print $2}' | awk -F '"' '{print $1}')
        DNS_SERVER=$(echo "${DNS_SERVER_PROPERTY}" | awk -F 'oe:value="' '{print $2}' | awk -F '"' '{print $1}')
        DNS_DOMAIN=$(echo "${DNS_DOMAIN_PROPERTY}" | awk -F 'oe:value="' '{print $2}' | awk -F '"' '{print $1}')

        cat > ${NETPLAN_CONFIG_FILE} << __CUSTOMIZE_NETPLAN__
network:
    version: 2
    renderer: networkd
    ethernets:
        ens160:
            addresses:
                - ${IP_ADDRESS}
            nameservers:
                search: [${DNS_DOMAIN}]
                addresses: [${DNS_SERVER}]
            routes:
                - to: default
                  via: ${GATEWAY}
__CUSTOMIZE_NETPLAN__
    netplan apply
    touch /root/ran_customization
    fi
fi