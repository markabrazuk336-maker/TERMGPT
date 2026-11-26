param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("encrypt","decrypt")]
    [string]$Mode
)

$ErrorActionPreference = "Stop"

Add-Type -AssemblyName System.Security

$data = [Convert]::FromBase64String(
    [Console]::In.ReadToEnd().Trim()
)

$scope = [System.Security.Cryptography.DataProtectionScope]::CurrentUser

if ($Mode -eq "encrypt") {
    $result = [System.Security.Cryptography.ProtectedData]::Protect(
        $data, $null, $scope
    )
} else {
    $result = [System.Security.Cryptography.ProtectedData]::Unprotect(
        $data, $null, $scope
    )
}

[Console]::Write(
    [Convert]::ToBase64String($result)
)
