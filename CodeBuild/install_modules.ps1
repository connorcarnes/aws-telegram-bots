<#
.SYNOPSIS
    This script is used in AWS CodeBuild to install the required PowerShell Modules for the build process.
.DESCRIPTION
    The version of PowerShell being run will be identified. This may vary depending on what type of build
    container you are running and if your buildspec is installing various versions of PowerShell. You will
    need to specify each module and version that is required for installation. You also need to specify
    which version of that module should be installed. Additionally, you will need to specify the S3 bucket
    location where that module currently resides, so that it can be downloaded and installed into the build
    container at runtime. This neccessitates that you download and upload your required modules to S3 prior to
    the build being executed.
.EXAMPLE
    Save-Module -Name Pester -RequiredVersion 4.4.5 -Path C:\RequiredModules
    Create an S3 bucket in your AWS account
    Zip the contents of the Pester Module up (when done properly the .psd1 of the module should be at the root of the zip)
    Name the ZIP file Pester_4.4.4 (adjust version as needed) unless you want to modify the logic below
    Upload the Pester Zip file up to S3 bucket you just created
.NOTES
    AWSPowerShell / AWSPowerShell.NetCore module should be included in all CodeBuild projects and is included below
    Pester, InvokeBuild, PSScriptAnalyzer, platyPS will typically be required by all module builds
    which is why they are included in this build script. Adjust versions as needed.
#>


$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
$VerbosePreference = 'SilentlyContinue'

# List of PowerShell Modules required for the build
# The AWS PowerShell Modules are added below, based on the $PSEdition
$modulesToInstall = [System.Collections.ArrayList]::new()
# https://github.com/pester/Pester
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'Pester'
            ModuleVersion = '5.3.1'
            BucketName    = 'PSGallery'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'InvokeBuild'
            ModuleVersion = '5.8.4'
            BucketName    = 'ps-invoke-modules'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'PSScriptAnalyzer'
            ModuleVersion = '1.20.0'
            BucketName    = 'ps-invoke-modules'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'AWSLambdaPSCore'
            ModuleVersion = '2.2.0.0'
            BucketName    = 'ps-invoke-modules'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'AWS.Tools.Common'
            ModuleVersion = '4.1.14.0'
            BucketName    = 'PSGallery'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'AWS.Tools.CloudFormation'
            ModuleVersion = '4.1.14.0'
            BucketName    = 'PSGallery'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'AWS.Tools.S3'
            ModuleVersion = '4.1.14.0'
            BucketName    = 'PSGallery'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'AWS.Tools.KeyManagementService'
            ModuleVersion = '4.1.14.0'
            BucketName    = 'PSGallery'
            KeyPrefix     = ''
        }))
$null = $modulesToInstall.Add(([PSCustomObject]@{
            ModuleName    = 'AWS.Tools.SimpleSystemsManagement'
            ModuleVersion = '4.1.14.0'
            BucketName    = 'PSGallery'
            KeyPrefix     = ''
        }))



Get-PackageProvider -Name Nuget -ForceBootstrap | Out-Null
'Installing PowerShell Modules'
Set-PSRepository -Name 'PSGallery' -InstallationPolicy Trusted
# $NuGetProvider = Get-PackageProvider -Name "NuGet" -ErrorAction SilentlyContinue
# if ( -not $NugetProvider ) {
#     Install-PackageProvider -Name "NuGet" -Confirm:$false -Force -Verbose
# }
foreach ($module in $modulesToInstall) {
    $installSplat = @{
        Name               = $module.ModuleName
        RequiredVersion    = $module.ModuleVersion
        Repository         = 'PSGallery'
        SkipPublisherCheck = $true
        Force              = $true
        ErrorAction        = 'Stop'
    }
    try {
        $ProgressPreference = 'SilentlyContinue'
        Install-Module @installSplat
        Import-Module -Name $module.ModuleName -ErrorAction Stop
        '  - Successfully installed {0}' -f $module.ModuleName
    }
    catch {
        $message = 'Failed to install {0}' -f $module.ModuleName
        "  - $message"
        throw
    }
}