# Building an HA kubeadm cluster on OCI (from zero, mapped from AWS)

## 0. Concept mapping (AWS -> OCI)

| AWS | OCI | Notes |
|---|---|---|
| AWS Account | Tenancy | Your root OCI account |
| Organizational Unit | Compartment | Logical grouping, like a folder for resources |
| VPC | VCN (Virtual Cloud Network) | Same idea, same CIDR planning |
| Subnet | Subnet | Same idea |
| Internet Gateway | Internet Gateway | Same |
| NAT Gateway | NAT Gateway | Same |
| Route Table | Route Table | Same |
| Security Group (stateful, per-ENI) | Network Security Group (NSG) | Closest match, attach to VNIC |
| Network ACL (stateless, per-subnet) | Security List | OCI Security Lists are stateful by default (unlike AWS NACLs) - this trips people up |
| EC2 Instance | Compute Instance | Same |
| Elastic IP | Reserved Public IP | Same |
| Key Pair | SSH Key (paste public key at launch) | Same |
| ALB / NLB | Load Balancer (L7) / Network Load Balancer (L4) | For kubeadm you want the **Network Load Balancer** - TCP passthrough |
| Auto Scaling Group | Instance Pool | Not needed for this project |
| Free tier t2.micro | Always Free Ampere A1 Flex (ARM) | 4 OCPU + 24GB RAM total, split across up to 4 instances - genuinely useful here |

You already understand VPC/subnet/SG design from your AWS project, so this will mostly feel like vocabulary translation, not new concepts.

## 1. Plan your topology

- 1 Compartment (or use root - fine for a portfolio project)
- 1 VCN, e.g. `10.0.0.0/16`
- 1 public subnet for everything, e.g. `10.0.1.0/24` (simplest path - masters, workers, and LB all here). If you want to mirror your AWS project's private-subnet pattern later, that's a good v2 iteration, but adds a bastion host requirement for SSH.
- 3 master instances: `master-1`, `master-2`, `master-3`
- 2+ worker instances: `worker-1`, `worker-2`
- 1 Network Load Balancer in front of the 3 masters on port 6443

## 2. Create the VCN

Console: **Networking -> Virtual Cloud Networks -> Start VCN Wizard -> "Create VCN with Internet Connectivity"**

This wizard auto-creates, in one step, the equivalent of what you'd build manually in AWS:
- VCN with your CIDR
- A public subnet + a private subnet
- Internet Gateway + NAT Gateway
- Route tables wired correctly
- Default Security Lists

For this project, delete or ignore the private subnet - use the public subnet for all 5 nodes. Note the public subnet's OCID and CIDR, you'll need them.

## 3. Configure the Security List (equivalent of your ALB -> app tier -> DB tier layered SG design)

Go to **Networking -> Virtual Cloud Networks -> your VCN -> Security Lists -> Default Security List**, add these **ingress** rules:

| Source | Protocol | Port range | Purpose |
|---|---|---|---|
| Your IP `/32` | TCP | 22 | SSH |
| `10.0.1.0/24` (subnet CIDR) | TCP | 6443 | apiserver - masters talk to each other + LB health checks |
| `10.0.1.0/24` | TCP | 2379-2380 | etcd client + peer traffic between masters |
| `10.0.1.0/24` | TCP | 10250-10252 | kubelet, scheduler, controller-manager |
| `10.0.1.0/24` | UDP | 4789 | Calico VXLAN (this is the rule you learned the hard way last time) |
| `0.0.0.0/0` | TCP | 6443 | Only if you want `kubectl` access from your laptop over the internet - otherwise restrict to your IP |

Egress: the default "allow all" rule from the wizard is fine.

This is the same layered-security-group thinking as your ALB/app/DB tiers in AWS - you're just scoping it by subnet CIDR here instead of separate SGs per tier, since everything sits in one subnet.

## 4. Launch the 3 master instances

**Compute -> Instances -> Create Instance**, repeat 3 times (`master-1`, `master-2`, `master-3`):

- Image: Ubuntu 22.04 or 24.04
- Shape: click "Change shape" -> **Ampere -> VM.Standard.A1.Flex** (Always Free eligible) -> allocate 2 OCPU / 12GB RAM per master (you have 4 OCPU/24GB total to split across up to 4 free instances, so plan accordingly - see note below)
- Networking: your VCN, your public subnet, "Assign a public IPv4 address" = yes
- SSH key: paste your public key (same as an AWS key pair, just pasted instead of downloaded)

**Free tier math note:** the Always Free Ampere allowance is 4 OCPU + 24GB total, not per instance. Three masters + two workers = 5 instances, more than the 4-instance free cap. Realistic options:
- Use free Ampere A1 for the 3 masters (e.g. 1 OCPU/6GB each) and pair with the separate Always Free **x86 micro shapes** (`VM.Standard.E2.1.Micro`, 1GB RAM, 2 instances included free) for the 2 workers.
- Or accept a small paid cost for workers if 1GB RAM is too tight for your Flask+MongoDB app - E2.1.Micro is genuinely small.

## 5. Launch the worker instances

Same process, `worker-1` and `worker-2`, same VCN/subnet/SSH key.

## 6. Create the Network Load Balancer

**Networking -> Load Balancers -> Create Load Balancer -> choose "Network Load Balancer"** (not the L7 "Load Balancer" - you want L4 TCP passthrough for the apiserver, this is the OCI equivalent of an AWS NLB, not an ALB).

- Visibility: Public (or private if you're only accessing via VPN/bastion)
- Subnet: your public subnet
- Listener: TCP, port 6443
- Backend set: TCP health check on port 6443, add `master-1`, `master-2`, `master-3` as backends on port 6443

Once created, note the **Load Balancer's public IP** - this is your `--control-plane-endpoint` value. In AWS terms this is exactly the DNS name of an NLB you'd put in front of a set of instances - except here you'll likely just use the IP directly rather than creating a Route 53-equivalent (OCI DNS) record, unless you want a clean domain name.

## 7. Bootstrap the cluster

Copy `common.sh`, `master-init.sh`, `master-join.sh`, and your existing `versions.sh` to all 5 nodes (`scp` works the same as with AWS EC2).

**On master-1:**
```bash
chmod +x common.sh master-init.sh
./common.sh
./master-init.sh <LOAD_BALANCER_PUBLIC_IP>
```
Copy the two join commands it prints at the end - save them somewhere.

**On master-2 and master-3:**
```bash
chmod +x common.sh master-join.sh
./common.sh
./master-join.sh "<the control-plane join command from master-1's output>"
```

**On worker-1 and worker-2:**
```bash
chmod +x common.sh
./common.sh
sudo <the worker join command from master-1's output>
```
(same as your current single-master flow, unchanged)

## 8. Verify

From any master:
```bash
kubectl get nodes -o wide
# expect: 3 masters with role control-plane, 2 workers with role <none>

kubectl get pods -n kube-system -o wide | grep -E 'etcd|apiserver'
# expect: 3 etcd- pods and 3 kube-apiserver- pods, one per master, all Running

kubectl get pods -n kube-system -o wide | grep calico-node
# expect: one calico-node pod per node (5 total), all Running
```

## 9. Prove the HA actually works (great portfolio evidence)

1. Stop the `master-1` instance from the OCI console (simulates an AZ/node failure).
2. From your laptop, `kubectl get nodes` should still work - it's now hitting `master-2` or `master-3` via the load balancer.
3. `kubectl get pods -n kube-system | grep etcd` should show `master-1`'s etcd member missing but the cluster still healthy (2 of 3 = quorum maintained).
4. Deploy a test pod, confirm scheduling still works.
5. Restart `master-1`, confirm it rejoins etcd and the apiserver comes back automatically - no `kubeadm join` needed again, since it's just a reboot, not a rebuild.

This before/after failover test is the single most convincing thing to show in an interview or on a portfolio page - it directly proves you understand quorum, not just that you copy-pasted commands.
