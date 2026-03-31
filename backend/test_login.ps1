$body = @{username='admin';password='Admin123!';role='system_admin'} | ConvertTo-Json -Compress
$result = Invoke-RestMethod -Method POST -Uri 'http://localhost:5174/api/v1/auth/login' -ContentType 'application/json' -Body $body
Write-Host "Login response:"
$result | ConvertTo-Json
$token = $result.data.access_token
Write-Host "Token: $token"

Write-Host "`nCalling companies/pending..."
$companies = Invoke-RestMethod -Method GET -Uri 'http://localhost:5174/api/v1/admin/companies/pending?current=1&size=20&status=0' -Headers @{"Authorization"="Bearer $token"}
Write-Host "Companies response:"
$companies | ConvertTo-Json