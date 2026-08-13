## Debugging a Flask + MongoDB App on Kubeadm (OCI): Root Cause Chain & Takeaways
#### NOTE:   

Bug: Pod DNS resolution timeout (cross-node) on OCI kubeadm cluster

**Symptom:** App pod on `wor-2` failed to resolve `mongo-service` — `Temporary failure in name resolution` — despite CoreDNS being healthy and resolv.conf correctly pointing to `10.96.0.10`.

**Root cause:** CoreDNS pods were scheduled on `MASTER`, app pod on `WORKER`. Calico VXLAN tunnel interfaces were up on both nodes, but the encapsulated traffic (UDP/4789) was being silently dropped by the OCI Security List — no rule explicitly allowed UDP/4789 between worker node subnets. Same-node traffic worked fine, masking the issue as DNS-specific until cross-node `ping` between pod IPs also failed.

**Fix:** Add ingress + egress rules to the OCI Security List (or NSG) for the worker subnet: `UDP port 4789`, source/destination = worker subnet CIDR (Security Lists are stateless — both directions required).

**Diagnostic path:** resolv.conf ✅ → Service/Endpoints ✅ → CoreDNS pod health ✅ → cross-node pod-to-pod ping ❌ → confirmed overlay/network issue, not DNS.

**Lesson:** On OCI, always explicitly allow VXLAN (UDP/4789) between worker nodes — same class of gotcha as OCI's default-reject INPUT chain and Security Lists silently dropping Calico IP-in-IP.

## Summary

A Flask + MongoDB app deployed on a 2-node kubeadm cluster (Oracle Cloud Infrastructure)
was failing with Gunicorn worker timeouts, then `503 database unavailable`, then DNS
resolution failures. The failure had **three independent, stacked causes** across three
different layers — application, host OS, and cloud network. Fixing only one layer at a
time still left the app broken, which is why this took so long to fully resolve.

---

## The Three Root Causes (in the order they were uncovered)

### 1. Application layer — pymongo's default timeout collided with Gunicorn's watchdog
- pymongo's default `serverSelectionTimeoutMS` is 30s.
- Gunicorn sync workers only send a "heartbeat" between requests. A request blocked
  for ~30s looks the same as a dead worker to Gunicorn's own default `--timeout` (30s).
- Result: worker gets SIGKILLed *before* it can log or return an error. Looks like
  silence in `kubectl logs`, or misleading "Perhaps out of memory?" messages.
- **Fix:** set explicit short pymongo timeouts (`serverSelectionTimeoutMS=5000`,
  `connectTimeoutMS=5000`), wrap all DB calls in `try/except PyMongoError` and return
  a proper `503` instead of hanging, and point K8s liveness/readiness probes at a
  Mongo-independent `/health` endpoint — never at a route that queries the DB.

### 2. Host OS layer — Oracle's default iptables rules blocked pod overlay traffic
- Oracle-provided Ubuntu images ship with a default-deny `iptables` ruleset
  (`INPUT`/`FORWARD` chains end in `REJECT --reject-with icmp-host-prohibited`).
- This rejected pod-to-pod traffic between nodes at the OS level, before it ever
  reached the network — symptom was `ping` to a pod IP on another node returning
  `Destination Host Prohibited` immediately (not a timeout).
- Loaded/reloaded via `netfilter-persistent` from `/etc/iptables/rules.v4`, which
  survives reboots unless explicitly disabled.
- **Fix:** disable the loader, flush the live rules, re-save so the on-disk file
  matches, then verify with an actual reboot on both nodes. Run on `master` and
  `worker-node`:

  ```bash
  # 1. Locate what's loading Oracle's default rules (diagnostic only)
  sudo find / -name "iptables_fromoracle*" 2>/dev/null
  systemctl list-units --type=service | grep -i iptables
  systemctl list-unit-files | grep -i netfilter

  # 2. Disable the loader so it stops restoring rules on boot
  sudo systemctl disable netfilter-persistent
  sudo systemctl stop netfilter-persistent

  # 3. Flush the live rules AND overwrite the saved rules file
  #    (disabling the service alone isn't enough - the saved file on disk
  #    still has the REJECT rules until you re-save over it)
  sudo iptables -F
  sudo iptables -X
  sudo iptables -P INPUT ACCEPT
  sudo iptables -P FORWARD ACCEPT
  sudo iptables -P OUTPUT ACCEPT
  sudo netfilter-persistent save

  # 4. Confirm the saved file now reflects the open state
  sudo cat /etc/iptables/rules.v4

  # 5. Reboot-test to confirm it actually holds
  sudo reboot
  # after it comes back up:
  sudo iptables -L -n -v
  ```

### 3. Cloud network layer — Calico's IPIP mode wasn't allowed by OCI Security Lists
- Calico defaults to `ipipMode: Always` — cross-node pod traffic gets encapsulated
  in **IP protocol 4** (IP-in-IP), which is *not* TCP or UDP.
- OCI Security Lists/NSGs are port-centric by default and silently drop protocol 4
  traffic unless an explicit rule is added — this is easy to miss because most cloud
  firewall UIs assume TCP/UDP.
- Symptom after fixing layer 2: `Destination Host Prohibited` became a plain
  `timed out` — packet left the host but got no reply, pointing to a network-layer
  (not host-layer) block.
- **Fix (chosen approach):** reinstalled Calico with `vxlanMode: Always`,
  `ipipMode: Never` instead of patching around IPIP. VXLAN uses standard UDP port
  4789, which is much easier to reason about and allow in OCI's Security List UI.
  Added an ingress rule for UDP 4789 (and TCP 179 for Calico's BGP route exchange)
  between the node subnet CIDRs, in both Security Lists *and* NSGs (OCI can have both
  attached — check both).

---

## Diagnostic Method That Worked (reusable playbook)

When a pod-to-service or pod-to-pod connection fails in Kubernetes, work outward in
this order — each layer rules out or confirms the next:

1. **App logs first.** Do they show a clean error, a hang, or nothing at all?
   Nothing at all + Gunicorn "WORKER TIMEOUT" = something is blocking below the
   app layer, not an app bug.
2. **DNS resolution inside the pod.**
   `kubectl exec -it <pod> -- getent hosts kubernetes.default`
   Always exists in every cluster — if *this* fails, DNS is broken cluster-wide,
   not specific to your service.
3. **Raw TCP to the target, bypassing DNS.**
   `python3 -c "import socket; socket.create_connection(('<ip>', <port>), timeout=5)"`
   Confirms whether it's name resolution or actual connectivity.
4. **Ping the actual pod IP** (not the Service ClusterIP) of something on another
   node, e.g. a CoreDNS pod. Same-node ping working + cross-node ping failing =
   isolates the problem to node-to-node networking, not Kubernetes Services/kube-proxy.
5. **Check `iptables -L -n -v --line-numbers` on the actual host** (SSH in directly,
   not `kubectl exec`) for `REJECT`/`DROP` rules in `INPUT`/`FORWARD`. An immediate
   `Destination Host Prohibited` on ping = host firewall. A silent `timed out` =
   more likely a cloud-network-level drop.
6. **Check the CNI's encapsulation mode** (`kubectl get ippool <name> -o yaml` for
   Calico) and confirm the cloud provider's Security Lists/NSGs actually allow that
   specific protocol/port between node IPs — this is the layer most tutorials skip
   entirely because AWS/most managed K8s handles it transparently.

---

## Config Decisions Worth Keeping for Future Clusters (especially on OCI)

- **Use Calico VXLAN mode, not IPIP, on OCI from the start.** Patch this at
  `kubeadm init` time, before joining any worker node — saves rediscovering this.
- **Probe `/health`, never `/`** (or any DB-touching route) for liveness/readiness.
- **Set pymongo timeouts explicitly** — never rely on the 30s default in a
  container/K8s environment where Gunicorn or similar has its own watchdog timeout
  in the same range.
- **Disable `netfilter-persistent` (or equivalent) on OCI-provided base images**
  before deploying a CNI, or explicitly allow pod CIDR traffic in the default
  ruleset — don't discover this reactively.
- **Check both Security Lists and NSGs in OCI** — an instance can have both attached,
  and a rule in only one won't help if the other is still filtering.
- **`docker build` DNS failures are separate from cluster DNS failures.** If
  `apt-get update` fails inside a build with "temporary failure resolving," check
  `/etc/resolv.conf` on the host for `127.0.0.53` (systemd-resolved stub, not
  reachable from build containers) — fix with `docker build --dns=8.8.8.8` or a
  `daemon.json` entry, unrelated to any in-cluster networking issue.
