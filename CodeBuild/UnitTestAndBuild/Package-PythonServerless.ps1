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

$lambdaSharedPath = [System.IO.Path]::Combine($pythonLambdaRoot, 'shared')
Write-Host "lambdaSharedPath is $lambdaSharedPath"

# Create the Lambda destination path
$lambdaPackagePath = [System.IO.Path]::Combine($pythonLambdaRoot, 'pkg')
$null = [System.IO.Directory]::CreateDirectory($lambdaPackagePath)
Write-Host "lambdaPackagePath is $lambdaPackagePath"

Write-Host "Contents of $lambdaSourcePath is:`r`n $(Get-ChildItem $lambdaSourcePath | Format-Table -AutoSize | Out-String)"

# Copy handlers from /src and helper functions from /shared to /pkg
Get-ChildItem $lambdaSourcePath | Copy-Item -Destination $lambdaPackagePath -Force
Get-ChildItem $lambdaSharedPath  | Copy-Item -Destination $lambdaPackagePath -Force

Write-Host "Contents of $lambdaPackagePath is:`r`n $(Get-ChildItem $lambdaPackagePath | Format-Table -AutoSize | Out-String)"

$lambdaRequirementsPath = [System.IO.Path]::Combine($lambdaSourcePath, 'requirements.txt')
Write-Host "lambdaRequirementsPathis $lambdaRequirementsPath"
pip install -t $lambdaPackagePath -r $lambdaRequirementsPath

$lambdaZipPath = [System.IO.Path]::Combine($pythonLambdaRoot, 'pkg.zip')
Write-Host "lambdaZipPath is $lambdaZipPath"

Write-Host "Contents of $lambdaPackagePath is:`r`n $(Get-ChildItem $lambdaPackagePath | Format-Table -AutoSize | Out-String)"

Get-ChildItem $lambdaPackagePath | Compress-archive -DestinationPath "$lambdaPackagePath.zip"

aws s3 cp $lambdaZipPath s3://tgbots-514215195183-artifacts/pkg.zip
