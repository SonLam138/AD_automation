# tools/create_ldap_credential.ps1

param(
    [string]$OutputFile = "app\security\ldap_credential.dat"
)

$password =
    Read-Host `
        "LDAP Password" `
        -AsSecureString

$password |
    ConvertFrom-SecureString |
    Out-File `
        $OutputFile `
        -Encoding utf8

Write-Host ""
Write-Host "LDAP credential created:"
Write-Host $OutputFile