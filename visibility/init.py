import requests
import os
# PyACI requires to have the MetaData present locally. Since the metada changes depending on the APIC version I use an init container to pull it. 
# No you can't put it in the same container as the moment you try to import pyaci it crashed is the metadata is not there. Plus init containers are cool!
# Get the APIC Model. s.environ.get("APIC_IPS").split(',')[0] gets me the first APIC here I don't care about RR
print("Loading ACI Metadata")
url = "https://" + os.environ.get("APIC_IPS").split(',')[0] + '/acimeta/aci-meta.json'
r = requests.get(url, verify=False, allow_redirects=True)
open('/root/.aci-meta/aci-meta.json','wb').write(r.content)
print("ACI Metadata Loaded")

