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

Write-Host("codeBuildRoot: When executing in CodeBuild, this file is executed from the root of the CodeBuild environment. " +
    "Setting this to a variable to assist with path generation."
$codeBuildRoot = $env:CODEBUILD_SRC_DIR
Write-Host"codeBuildRoot is: $($codeBuildRoot)"

$pythonLambdaRoot = [System.IO.Path]::Combine($codeBuildRoot, 'lambdafunctions', 'python')
Write-Host"pythonLambdaRoot is $pythonLambdaRoot"

$lambdaHandlerSourceFiles = [System.IO.Path]::Combine($pythonLambdaRoot, 'src', '*.py')
Write-Host"lambdaHandlerSourceFiles is $lambdaHandlerSourceFiles"
Write-Host $($lambdaHandlerSourceFiles | format-table -AutoSize | Out-string)

# $cfnServerlessApiPath = [System.IO.Path]::Combine($codeBuildRoot, 'cloudformation', 'apc-api')
# $lambdaSourceDestinationPath = [System.IO.Path]::Combine($cfnServerlessApiPath, 'src')

$cfnCodeUriPath = [System.IO.Path]::Combine($env:CODEBUILD_SRC_DIR, 'cloudformation', 'childtemplates', 'src')
Write-Host $cfnCodeUriPath
# Create the Lambda destination path
$null = [System.IO.Directory]::CreateDirectory($cfnCodeUriPath)
# $null = [System.IO.Directory]::CreateDirectory($lambdaSourceDestinationPath)

# Copy the "handler" files to the destination root
# Copy-Item -Path $lambdaHandlerSourceFiles -Destination $lambdaSourceDestinationPath -Force
Copy-Item -Path $lambdaHandlerSourceFiles -Destination $cfnCodeUriPath -Force

# Copy all other Lambda source files to the destination, with folder structure
$folders = Get-ChildItem -Path $pythonLambdaRoot -Directory | Where-Object {
    $_.Name -notin ('__pycache__', 'src', 'tests')
}
Write-Host $($folders | format-table -AutoSize | Out-string)

foreach ($folder in $folders) {
    # Create the destination folder
    # $destinationPath = [System.IO.Path]::Combine($lambdaSourceDestinationPath, $folder.Name)
    $destinationPath = [System.IO.Path]::Combine($cfnCodeUriPath, $folder.Name)
    $null = [System.IO.Directory]::CreateDirectory($destinationPath)
    Write-Host "Copying $($folder.FullName)"
    $sourceFiles = [System.IO.Path]::Combine($folder.FullName, '*.py')
    Copy-Item -Path $sourceFiles -Destination $destinationPath -Force -Exclude '__pycache__'
}

Write-Host $(gci $cfnCodeUriPath -recurse | format-table -AutoSize | Out-string)