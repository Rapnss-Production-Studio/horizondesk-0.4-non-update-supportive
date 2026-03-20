$subjectName = "CN=Rapnss Production Studio"
$certStoreLocation = "Cert:\CurrentUser\My"
$pfxFilePath = ".\RapnssCert.pfx"
$passwordString = "Rapnss123!"

Write-Host "Creating Self-Signed Certificate for Code Signing..."
$cert = New-SelfSignedCertificate -Type Custom -Subject $subjectName -KeyUsage DigitalSignature -FriendlyName "Horizon Desk Code Signing" -CertStoreLocation $certStoreLocation -TextExtension @("2.5.29.37={text}1.3.6.1.5.5.7.3.3", "2.5.29.19={text}")

Write-Host "Exporting Certificate to $pfxFilePath..."
$pwd = ConvertTo-SecureString -String $passwordString -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath $pfxFilePath -Password $pwd

Write-Host "Certificate generation complete. You can use $pfxFilePath to sign your installer."
Write-Host "Note: To avoid 'Unknown Publisher', you must also install this certificate to the 'Trusted Root Certification Authorities' store on the target machine."
