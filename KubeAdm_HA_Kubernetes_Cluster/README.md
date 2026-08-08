# HA Kubernetes on OCI with kubeadm

A production-realistic, self-managed 3-master / N-worker high-availability Kubernetes cluster built from scratch on Oracle Cloud Infrastructure using `kubeadm`, `containerd`, and Calico (VXLAN mode) — no managed control plane, no cloud controller manager, everything provisioned and bootstrapped by hand to understand exactly how each piece works.

## Why this exists

Most tutorials stop at a single control-plane node. This repo goes further: 3 stacked-etcd masters behind a load balancer, with the actual production reasoning behind each decision — why VXLAN over IP-in-IP, why NodePort instead of `type: LoadBalancer`, why an odd number of masters, and the specific OCI networking gotchas that don't show up on AWS.

## Architecture

```
                    ┌────────────────────┐
                    │  kubectl / workers  │   (external clients)
                    └──────────┬─────────┘
                               │  :6443 (TCP)
                    ┌──────────▼─────────┐
                    │  OCI Load Balancer  │   (Network LB, L4 passthrough)
                    │   backend: 3 masters │
                    └───┬──────────┬─────┘
              ┌─────────┘          └─────────┐
        ┌─────▼─────┐   ┌───────────┐  ┌─────▼─────┐
        │ Master 1  │◄─►│ Master 2  │◄─►│ Master 3  │   etcd peer traffic
        │ apiserver │   │ apiserver │   │ apiserver │   :2380 - direct,
        │ + etcd    │   │ + etcd    │   │ + etcd    │   bypasses the LB
        └───────────┘   └───────────┘   └───────────┘
                               │
                    ┌──────────┴─────────┐
                    │  Worker nodes (2+)  │
                    │  NodePort :3xxxx    │
                    └─────────────────────┘
```

**Key design decisions:**

| Decision | Choice | Why |
|---|---|---|
| etcd topology | Stacked (co-located with control plane) | Simpler, fewer nodes than external etcd; fine for this scale |
| Master count | 3 (odd) | etcd/Raft needs a majority quorum - odd numbers avoid wasting a node |
| CNI | Calico, **VXLAN** mode (not IP-in-IP) | OCI Security Lists block protocol-4 (IP-in-IP) by default; VXLAN uses standard UDP 4789 |
| Control-plane exposure | OCI Network Load Balancer (L4 TCP passthrough), not L7 | apiserver's TLS must reach the client intact - no termination/inspection needed |
| App exposure | `Service type: NodePort` + manually-configured OCI LB | No OCI cloud controller manager is installed on a self-managed cluster, so `type: LoadBalancer` would sit on `<pending>` forever |
| Master placement | Spread across Availability Domains if available, otherwise Fault Domains | OCI subnets are regional by default (unlike AWS AZ-pinned subnets) - AD/FD is chosen per-instance, not per-subnet |

## Repo structure

```
.
├── versions.sh          # pins K8S_VERSION and PACKAGE_VERSION, sourced by common.sh
├── common.sh             # runs on every node (masters + workers): containerd, kernel modules,
│                          # sysctl, kubelet/kubeadm/kubectl install. Identical regardless of HA.
├── master-init.sh        # run ONCE, on the first master only. Bootstraps the HA control plane,
│                          # installs Calico, prints the join commands for the other two masters
│                          # and for workers.
├── master-join.sh        # run on master-2 and master-3. Joins an additional control-plane node
│                          # using the command printed by master-init.sh.
└── worker-join.sh         # run on every worker node. Joins as a worker using the command
                            # printed by master-init.sh.
```

## Prerequisites

- An OCI tenancy with quota for 5 compute instances (3 masters + 2+ workers) and 1 load balancer
- A VCN with at least one subnet the instances can reach each other on, and outbound internet access (via Internet Gateway if public, NAT Gateway if private)
- An SSH key pair
- Familiarity with `kubectl` locally is optional - it's fully usable from any master

## 1. Provision the infrastructure (OCI)

1. **VCN**: use the "Create VCN with Internet Connectivity" wizard, or bring your own. Note the subnet CIDR.
2. **Security List / NSG** — allow, scoped to your subnet CIDR (not `0.0.0.0/0`, except where noted):
   - `22/tcp` - SSH, from your IP only
   - `6443/tcp` - apiserver
   - `2379-2380/tcp` - etcd client + peer (direct between masters, never touches the LB)
   - `10250-10252/tcp` - kubelet, scheduler, controller-manager
   - `4789/udp` - Calico VXLAN
   - `30000-32767/tcp` - NodePort range, for exposing apps later
3. **Compute instances**: `master-1`, `master-2`, `master-3`, `worker-1`, `worker-2` (add more workers as needed). Ubuntu 22.04/24.04, same subnet, SSH key attached.
4. **Load Balancer**: create a **Network Load Balancer** (not the L7 Load Balancer) with:
   - Listener: TCP, port 6443
   - Backend set: all 3 masters, port 6443
   - Health check: **TCP** on port 6443 (not HTTP — the apiserver only speaks HTTPS, so an HTTP health check will always fail, with every backend showing critical regardless of actual health)
5. Note the load balancer's public/private IP — this is your control-plane endpoint for the next step.

## 2. Bootstrap the cluster

Copy `versions.sh`, `common.sh`, and the relevant join script to each node (`scp` works the same as EC2). Run `common.sh` on **every** node first.

**On master-1 only:**
```bash
chmod +x common.sh master-init.sh
./common.sh
./master-init.sh <LOAD_BALANCER_IP>
```
This prints two join commands at the end — save both. One is for additional masters (`--control-plane --certificate-key ...`), the other is for workers.

**On master-2 and master-3:**
```bash
chmod +x common.sh master-join.sh
./common.sh
./master-join.sh kubeadm join <LB_IP>:6443 --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash> \
  --control-plane --certificate-key <key>
```
> The certificate key is valid for **2 hours**. If it expires, regenerate on master-1 with:
> `sudo kubeadm init phase upload-certs --upload-certs` then `kubeadm token create --print-join-command`.

Quoting the join command is recommended but not required — `master-join.sh` reassembles all arguments you pass it either way.

**On every worker:**
```bash
chmod +x common.sh worker-join.sh
./common.sh
./worker-join.sh kubeadm join <LB_IP>:6443 --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```

## 3. Verify

```bash
kubectl get nodes -o wide
# expect 3 control-plane nodes, N worker nodes, all Ready

kubectl get pods -n kube-system -o wide | grep -E 'etcd|apiserver'
# expect one etcd- and one kube-apiserver- pod per master, all Running

kubectl get pods -n kube-system -o wide | grep calico-node
# expect one calico-node pod per node, all Running
```

## 4. Prove the HA actually works

1. Stop the `master-1` instance from the OCI console.
2. `kubectl get nodes` should still work — it's now being served by `master-2` or `master-3` through the load balancer.
3. `kubectl get pods -n kube-system | grep etcd` should show the remaining 2 etcd members still healthy (2-of-3 quorum maintained).
4. Deploy a test pod - scheduling should still succeed.
5. Restart `master-1` - it should rejoin etcd and the apiserver should come back automatically, no `kubeadm join` needed for a simple reboot.

## Troubleshooting

**LB shows all backends critical, but the apiserver is definitely running.**
Check the backend set's **health check protocol** first — if it's set to HTTP instead of TCP, every backend will show critical regardless of actual health, since the apiserver only serves HTTPS on 6443. If the health check is correctly TCP and it's still critical, suspect the OCI base-image host firewall next (see below) before assuming a Kubernetes-level problem.

**`curl -k https://localhost:6443/healthz` from the node itself returns nothing, or the LB times out reaching a node that's clearly listening (`ss -tlnp | grep 6443` shows it bound).**
Check the host-level iptables, not just the OCI Security List — Ubuntu images on OCI ship with a default-reject INPUT chain policy independent of whatever your Security List allows:
```bash
sudo iptables -L INPUT -n -v | grep REJECT
```
If you see a catch-all `REJECT ... icmp-host-prohibited` rule, insert explicit ACCEPT rules above it for 6443, 2379-2380, 10250-10252, and 4789/udp, then persist with `sudo netfilter-persistent save` (install `iptables-persistent` if missing) so it survives a reboot.

**`kubeadm join` output shows kubeadm's top-level help text instead of actually joining, followed by `cp: cannot stat '/etc/kubernetes/admin.conf'`.**
This means the join command wasn't passed to the script as expected — usually from not quoting a multi-word command, causing only the first word (`kubeadm`) to register. `master-join.sh`/`worker-join.sh` in this repo reassemble all passed arguments (`"$*"`) specifically to avoid this, and will refuse to proceed and print a clear error if `admin.conf` still doesn't exist afterward.

**Calico pods stuck in `CrashLoopBackOff` or nodes can't reach each other's pods.**
Confirm you're on VXLAN, not IP-in-IP — check `calico.yaml` for `CALICO_IPV4POOL_VXLAN: "Always"` and `CALICO_IPV4POOL_IPIP: "Never"`. OCI Security Lists block IP-in-IP (protocol 4) by default; VXLAN uses standard UDP 4789, which is what this repo's manifest is patched for.

**Re-running `master-init.sh` after a partial failure throws `Port 6443 is in use` / `file already exists`.**
`kubeadm init` already succeeded on a prior run — you're not starting from clean. Reset before retrying:
```bash
sudo kubeadm reset -f
sudo rm -rf /etc/cni/net.d /var/lib/etcd $HOME/.kube/config
```

## Teardown

On each node:
```bash
sudo kubeadm reset -f
sudo rm -rf /etc/cni/net.d /var/lib/etcd $HOME/.kube/config /etc/kubernetes
```
Then terminate the OCI compute instances and delete the load balancer from the console.

## Notes for future extension

- **NodePort → app exposure**: define an explicit `nodePort` (30000-32767) in your Service manifest rather than letting Kubernetes assign one at random, and point a second OCI Load Balancer's backend set at your workers on that port — this is a separate LB from the control-plane one, serving a different purpose.
- **Private-subnet production hardening**: this setup can be moved to masters/workers in a private subnet with the load balancer as the only internet-facing component, using an OCI Bastion (or a small jump host) for SSH and a NAT Gateway for outbound package/image pulls.
- **MetalLB** is worth knowing about if you ever want `type: LoadBalancer` to work natively on a self-managed cluster instead of manually wiring NodePort + an external LB.
