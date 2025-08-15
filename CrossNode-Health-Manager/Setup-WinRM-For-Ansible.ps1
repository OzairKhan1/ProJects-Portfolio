<powershell>
# Enable PowerShell Remoting
Enable-PSRemoting -Force

# Set WinRM service startup type to Automatic
Set-Service WinRM -StartupType 'Automatic'

# Configure WinRM Service Authentication and Encryption for HTTP
Set-Item -Path WSMan:\localhost\Service\Auth\Certificate -Value $false
Set-Item -Path WSMan:\localhost\Service\AllowUnencrypted -Value $true
Set-Item -Path WSMan:\localhost\Service\Auth\Basic -Value $true
Set-Item -Path WSMan:\localhost\Service\Auth\CredSSP -Value $true

# Create WinRM HTTP listener if not exists
$listenerExists = winrm enumerate winrm/config/listener | Select-String "Transport=HTTP"
if (-not $listenerExists) {
    winrm create winrm/config/Listener?Address=*+Transport=HTTP
}

# Create firewall rule to allow WinRM HTTP inbound (port 5985) if not exists
if (-not (Get-NetFirewallRule -DisplayName "Allow WinRM HTTP" -ErrorAction SilentlyContinue)) {
    New-NetFirewallRule -DisplayName "Allow WinRM HTTP" -Direction Inbound -LocalPort 5985 -Protocol TCP -Action Allow
}

# Configure TrustedHosts to allow all
Set-Item WSMan:\localhost\Client\TrustedHosts -Value "*" -Force

# Disable UAC remote restrictions
New-ItemProperty -Path "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System" `
    -Name "LocalAccountTokenFilterPolicy" -Value 1 -PropertyType DWord -Force

# Set PowerShell Execution Policy to Unrestricted
Set-ExecutionPolicy Unrestricted -Force

# Restart WinRM to apply all changes
Restart-Service WinRM

# Output WinRM listeners for verification
winrm enumerate winrm/config/listener
</powershell>
