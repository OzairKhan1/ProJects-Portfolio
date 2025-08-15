# Cross-Platform Automated System Information Collection on AWS (Windows & Linux)

**An end-to-end automation framework for provisioning AWS EC2 instances and collecting detailed system insights from both Windows and Linux servers — all fully automated, scheduled, and alert-enabled.**

---

## 🚀 Key Features

- **Cross-Platform Support:** Designed for heterogeneous environments with both Windows Server and Linux instances.  
- **AWS EC2 Instance Creation:** Spin up your cloud environment quickly via the AWS Console.  
- **Dynamic Hostname Renaming:** Python scripts enforce standardized, meaningful hostnames across all instances.  
- **Passwordless SSH Authentication:** Bash scripts configure secure and seamless passwordless access for remote management.  
- **Dynamic Ansible Inventory:** Automatically generate and update your Ansible inventory with a Bash script reflecting live infrastructure.  
- **Comprehensive System Data Collection:** Ansible playbooks gather detailed hardware, software, and configuration info from all nodes.  
- **HTML Reporting:** Data is formatted into clean, accessible HTML reports for quick analysis and sharing.  
- **Scheduled Automation with Cronjobs:** Automate data collection and reporting at desired intervals — hands-free and reliable.  
- **Real-Time Notifications:** Integration with Email and Amazon SNS to alert you instantly on status updates or anomalies.  

---

## 🎯 Why Use This Project?

Managing multiple cloud servers, especially across different OS platforms, can quickly become overwhelming. Manual monitoring is inefficient and error-prone.

This solution offers a **scalable, automated, and alert-driven approach** that saves time, reduces human error, and provides actionable insights in a readable format — making infrastructure monitoring proactive, not reactive.

---

## ⚙️ How It Works

1. **Create AWS EC2 Instances** via AWS Console.  
2. **Rename Instances Dynamically** using a Python script for consistent naming conventions.  
3. **Set Up Passwordless SSH** with Bash scripts for smooth remote management.  
4. **Generate Dynamic Ansible Inventory** that reflects your current environment automatically.  
5. **Run Ansible Playbooks** to collect system facts and metrics from Windows and Linux nodes.  
6. **Schedule Cronjobs** to automate the entire data collection and reporting process.  
7. **Receive Notifications** via Email or Amazon SNS when jobs complete or anomalies are detected.  
8. **View Formatted HTML Reports** summarizing the collected system information.  

---

## 📥 Getting Started

Follow the usage instructions below to deploy and customize the automation for your environment.

*(Add installation steps, prerequisites, usage examples, and environment setup here)*

---

Feel free to fork, improve, and reach out for collaboration or questions!

---

*Powered by AWS, Python, Bash, Ansible & DevOps best practices.*


------------------------------------------------------ Step By Step Guide For This Porject --------------------------------------------------------

> **Note:** If Windows nodes are created, you need to enable ports and configure the firewall for **WinRM**.  
> This is done using the script **`Setup-WinRM-For-Ansible`**.  
> Please add this script while launching Windows EC2 instances — it will automatically handle the initial configuration with no manual hassle.

---

## Steps

1. Once new instances are launched, rename them using:  
   ```bash
   python3 renameInstances.py
   ```

2. Create a dynamic inventory (**Recommended:** group by tag) using:  
   ```bash
   python3 dynamic_inventory.py
   ```

3. Enable passwordless authentication if the nodes are Linux using:  
   ```bash
   bash pwdlss_auth.sh
   ```
   Make sure to update necessary changes, such as the key file.

4. Test Linux nodes using:  
   ```bash
   ansible-playbook linux_check.yaml
   ```

5. If nodes are Windows, create a dynamic inventory using:  
   ```bash
   bash win_dynamic_Inv.sh
   ```

6. Test Windows nodes using:  
   ```bash
   ansible-playbook -i windows_inventory.ini win_check.yaml
   ```

7. Run the final report:  
   ```bash
   ansible-playbook FinalReport.yml
   ```
   This will:
   - Gather information from Linux nodes by running it on the corresponding machines
   - Gather information from Windows nodes
   - Send the email automatically
   - Optionally enable a cronjob as per user demand

8. **Optional:** Quick EC2 automation using:  
   ```bash
   python3 strt_stp_ter_skp_lst.py
   ```
   Options:
   - **List:** EC2
   - **Start:** EC2
   - **Stop:** EC2
   - **Terminate:** EC2
   - **Skip:** Keep selected instances running and manage others

---

## For Step 7, Review the Following Files:
1. `collect_system_report.yml`  
2. `win_sys_report.yml`  
3. `sendAutoMail.yml`  
4. Enter your details in `group_vars/all.yaml`  
5. HTML template is provided in the templates directory



