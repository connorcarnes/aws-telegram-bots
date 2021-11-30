$CipherText = (Get-SSMParameter -Name '/tgbots/fleetmorselbot').value
$EncryptedBytes = [System.Convert]::FromBase64String($cipherText)
$EncryptedMemoryStreamToDecrypt = New-Object System.IO.MemoryStream($encryptedBytes, 0, $encryptedBytes.Length)
$DecryptedMemoryStream = Invoke-KMSDecrypt -CiphertextBlob $encryptedMemoryStreamToDecrypt
$BotValues = ConvertFrom-Json ([System.Text.Encoding]::UTF8.GetString($decryptedMemoryStream.Plaintext.ToArray()))

$Uri = "https://api.telegram.org/bot$($BotValues.token)/setWebhook?url=$($ENV:FleetMorselBotWebhook)"

Invoke-RestMethod -Uri $Uri