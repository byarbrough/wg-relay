[![Build badge](https://gitlab.com/byarbrough/wg-relay/badges/master/pipeline.svg)](https://gitlab.com/byarbrough/wg-relay)
# wg-relay
Relay wireguard traffic between peers using a cloud server in the middle.
Fully automated with Terraform and Ansible.
Current implementation is on AWS using Alpine Linux Docker Clients.

Medium Series: _[WireGuard Relay Infrastructure as Code](https://medium.com/@yarbrough.b/wireguard-relay-infrastructure-as-code-b337b77af9d5)_

## Wireguard
The tricky thing to realize about wg is that all it does is make an encrypted route for UDP traffic between two devices. These interfaces (typically called `wg0`) have their own IP address, which should be part of a subnet _different than the subnet of any physical interfaces._ Otherwise you will have issues with routing.

# Install
Clone this repo, and then `cd` into it.
Then, make sure your host sytem (this was developed and tested on Ubuntu 18.04) has Terraform and Ansible.

Install Terraform
```
cd infrastructure
wget https://releases.hashicorp.com/terraform/0.12.24/terraform_0.12.24_linux_amd64.zip
unzip terraform_0.12.24_linux_amd64.zip
```
You can leave the binary in that directory, or add it to your path, such as `~/.local/bin`

Ansible is best installed with pip (and inside a venv if you use those).
```
pip install ansible
```

Next, export `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` or use `aws configure` to place them in `.aws/credentials`. Terraform checks that file by default; however the profile name must match what you give terraform.

Create `terraform.tfvars` following the example of `terraform.tfvars.example`.
This will require the generation of an ssh key, example here named `wg-id_rsa`
```
ssh-keygen -t rsa -b 4096 -N '' -C "wireguard ssh key" -f wg-id_rsa
```

To see if things are ready to go use
```
cd infrastructure
terraform init
terraform plan
```

# Run
If `terraform plan` executed successfully, then you should be ready to stand up your server
```
cd infrastructure
terraform apply
```
It is as easy as that!

Feel free to ssh into your new EC2 instance
```
ssh -i <path to wg-id_rsa> ubuntu@<wg_server_ip>
```

## Docker Peer
To test the connection, build the included Docker image
```
cd peer
sudo docker build -t wg-peer-img .
```
Then run the image. This requires NET_ADMIN capabilities because we are modifying the interfaces.
```
sudo docker run -it --name=wg-peer --cap-add=NET_ADMIN wg-peer-img
```
That will drop you in to a shell in the container. The last step is to bring up the wireguard interface.
```
wg-quick up wg0
```
Finally, see the results
```
wg
```
This should show you something like the following
```
/ # wg
interface: wg0
  public key: ...
  private key: (hidden)
  listening port: 39300

peer: ...
  endpoint: 3.26.105.37:51820
  allowed ips: 10.37.0.0/24
  latest handshake: 2 seconds ago
  transfer: 92 B received, 180 B sent
  persistent keepalive: every 23 seconds
```
If you see a handshake, congratulations, your container is talking to the cloud wireguard relay!


_Working repository is https://gitlab.com/byarbrough/wg-relay_

_Mirrored at https://github.com/byarbrough/wg-relay/_
