with open('TEMPLATES/K8s_Packages', 'r') as f:
    lines = f.read()

packages = lines.split("\n\n")

for package in packages:
    if "Package: kubelet" in package:
        print(package.split('\n')[0:2][0].split(':')[1].strip())
        print(package.split('\n')[0:2][1].split(':')[1].strip())