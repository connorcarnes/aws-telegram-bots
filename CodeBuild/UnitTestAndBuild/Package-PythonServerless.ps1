<#
    .SYNOPSIS
    This bulid script copies all Python Lambda source files into the correct
    ServerlessApi folder so "aws cloudformation package" works as expected.
#>

$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

if ([String]::IsNullOrWhiteSpace($env:ARTIFACT_S3_BUCKET)) {
    throw 'The environment variable ARTIFACT_S3_BUCKET must be configured.'
}

# Setting this to a variable to assist with path generation.
Write-Host "When executing in CodeBuild, this file is executed from the root of the CodeBuild environment."
$codeBuildRoot = $env:CODEBUILD_SRC_DIR
Write-Host "codeBuildRoot is $codeBuildRoot"

$pythonLambdaRoot = [System.IO.Path]::Combine($codeBuildRoot, 'lambdafunctions', 'python')
Write-Host "pythonLambdaRoot is $pythonLambdaRoot"

$lambdaSourcePath = [System.IO.Path]::Combine($pythonLambdaRoot, 'src')
Write-Host "lambdaSourcePath is $lambdaSourcePath"

# $cfnServerlessApiPath = [System.IO.Path]::Combine($codeBuildRoot, 'cloudformation', 'apc-api')
# $lambdaSourceDestinationPath = [System.IO.Path]::Combine($cfnServerlessApiPath, 'src')

# $cfnCodeUriPath = [System.IO.Path]::Combine($env:CODEBUILD_SRC_DIR, 'cloudformation', 'childtemplates', 'src')
# Write-Host $cfnCodeUriPath
# Create the Lambda destination path
$lambdaPackagePath = [System.IO.Path]::Combine($pythonLambdaRoot, 'pkg')
$null = [System.IO.Directory]::CreateDirectory($lambdaPackagePath)
# $null = [System.IO.Directory]::CreateDirectory($lambdaSourceDestinationPath)
Write-Host "lambdaPackagePath is $lambdaPackagePath"

Write-Host "Contents of $lambdaSourcePath is:`r`n $(Get-ChildItem $lambdaSourcePath | Format-Table -AutoSize | Out-String)"

# Copy the "handler" files to the destination root
# Copy-Item -Path $lambdaSourcePath -Destination $lambdaSourceDestinationPath -Force
Get-ChildItem $lambdaSourcePath | Copy-Item -Destination $lambdaPackagePath -Force

Write-Host "Contents of $lambdaPackagePath is:`r`n $(Get-ChildItem $lambdaPackagePath | Format-Table -AutoSize | Out-String)"

$lambdaRequirementsPath = [System.IO.Path]::Combine($lambdaSourcePath, 'requirements.txt')
Write-Host "lambdaRequirementsPathis $lambdaRequirementsPath"
pip install -t $lambdaPackagePath -r $lambdaRequirementsPath

$lambdaZipPath = [System.IO.Path]::Combine($pythonLambdaRoot, 'pkg.zip')
Write-Host "lambdaZipPath is $lambdaZipPath"

Get-ChildItem $lambdaPackagePath | Compress-archive -DestinationPath "$lambdaPackagePath.zip"

aws s3 cp $lambdaZipPath s3://pytgbudgetbot-514215195183-artifacts/pkg.zip
# Copy all other Lambda source files to the destination, with folder structure
# $folders = Get-ChildItem -Path $pythonLambdaRoot -Directory | Where-Object {
#     $_.Name -notin ('__pycache__', 'src', 'tests')
# }
# Write-Host $($folders | format-table -AutoSize | Out-string)
#
# foreach ($folder in $folders) {
#     # Create the destination folder
#     # $destinationPath = [System.IO.Path]::Combine($lambdaSourceDestinationPath, $folder.Name)
#     $destinationPath = [System.IO.Path]::Combine($cfnCodeUriPath, $folder.Name)
#     $null = [System.IO.Directory]::CreateDirectory($destinationPath)
#     Write-Host "Copying $($folder.FullName)"
#     $sourceFiles = [System.IO.Path]::Combine($folder.FullName, '*.py')
#     Copy-Item -Path $sourceFiles -Destination $destinationPath -Force -Exclude '__pycache__'
# }
#
# Write-Host $(gci $cfnCodeUriPath -recurse | format-table -AutoSize | Out-string)