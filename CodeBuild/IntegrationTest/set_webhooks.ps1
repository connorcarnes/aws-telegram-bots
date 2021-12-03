$Bots = @(
    'FleetMorselBot',
    'LoquaciousEchoBot'
)

foreach ($Bot in $Bots) {
    Write-Host "Setting $Bot webhook..."
    $Webhook = [Environment]::GetEnvironmentVariable(($Bot + 'Webhook'))
    $CipherText = (Get-SSMParameter -Name "/tgbots/$Bot").value
    $EncryptedBytes = [System.Convert]::FromBase64String($CipherText)
    $EncryptedMemory = New-Object System.IO.MemoryStream($EncryptedBytes, 0, $EncryptedBytes.Length)
    $DecryptedMemory = Invoke-KMSDecrypt -CiphertextBlob $EncryptedMemory
    $BotValues = ConvertFrom-Json ([System.Text.Encoding]::UTF8.GetString($DecryptedMemory.Plaintext.ToArray()))
    $Uri = "https://api.telegram.org/bot$($BotValues.BOT_TOKEN)/setWebhook?url=$Webhook"
    Invoke-RestMethod -Uri $Uri
}

