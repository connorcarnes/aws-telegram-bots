$CipherText = (Get-SSMParameter -Name '/tgbots/fleetmorselbot').value
$EncryptedBytes = [System.Convert]::FromBase64String($cipherText)
$EncryptedMemoryStreamToDecrypt = New-Object System.IO.MemoryStream($encryptedBytes, 0, $encryptedBytes.Length)
$DecryptedMemoryStream = Invoke-KMSDecrypt -CiphertextBlob $encryptedMemoryStreamToDecrypt
$BotValues = ConvertFrom-Json ([System.Text.Encoding]::UTF8.GetString($decryptedMemoryStream.Plaintext.ToArray()))

$Uri = "https://api.telegram.org/bot$($BotValues.BOT_TOKEN)/setWebhook?url=$($ENV:FleetMorselBotWebhook)"

write-host "Setting webhook to $($Uri)"

Invoke-RestMethod -Uri $Uri


$CipherText = (Get-SSMParameter -Name '/tgbots/loquaciousechobot').value
$EncryptedBytes = [System.Convert]::FromBase64String($cipherText)
$EncryptedMemoryStreamToDecrypt = New-Object System.IO.MemoryStream($encryptedBytes, 0, $encryptedBytes.Length)
$DecryptedMemoryStream = Invoke-KMSDecrypt -CiphertextBlob $encryptedMemoryStreamToDecrypt
$BotValues = ConvertFrom-Json ([System.Text.Encoding]::UTF8.GetString($decryptedMemoryStream.Plaintext.ToArray()))

$Uri = "https://api.telegram.org/bot$($BotValues.BOT_TOKEN)/setWebhook?url=$($ENV:LoquaciousEchoBotWebhook)"

write-host "Setting webhook to $($Uri)"

Invoke-RestMethod -Uri $Uri
