param(
    [string]$Command
)

# =========================
# Exchange Credential
# =========================

$username = "AUTOMATE\administrator"

$password = ConvertTo-SecureString `
    "C0anhtien@123" `
    -AsPlainText `
    -Force

$Credential = New-Object System.Management.Automation.PSCredential(
    $username,
    $password
)

# =========================
# Connect Exchange
# =========================

$sessionOption = New-PSSessionOption `
    -SkipRevocationCheck

$session = New-PSSession `
    -ConfigurationName Microsoft.Exchange `
    -ConnectionUri "https://dc-01.automate.com.vn/powershell" `
    -Authentication Basic `
    -Credential $Credential `
    -SessionOption $sessionOption `
    -AllowRedirection

if (-not $session) {
    Write-Error "Failed to create Exchange session"
    exit 1
}

try {
    Import-PSSession `
        $session `
        -DisableNameChecking `
        -AllowClobber `
        -ErrorAction Stop | Out-Null
}
catch {
    Write-Error $_.Exception.Message
    Remove-PSSession $session
    exit 1
}

# =========================
# Execute Command
# =========================


if (:IsNullOrWhiteSpace($Command)) {
    Write-Error "Command is empty"
    exit 1
}

try {
    $result = Invoke-Expression $Command

    if ($null -ne $result) {
        $result
    }
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
finally {
    if ($session) {
        Remove-PSSession $session
    }
}
