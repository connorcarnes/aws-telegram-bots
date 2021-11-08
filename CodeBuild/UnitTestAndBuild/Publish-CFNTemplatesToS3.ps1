$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'

if ([String]::IsNullOrWhiteSpace($env:ARTIFACT_S3_BUCKET)) {
    throw 'The environment variable ARTIFACT_S3_BUCKET must be configured.'
}

if ([String]::IsNullOrWhiteSpace($env:S3_KEY_PREFIX)) {
    throw 'The environment variable S3_KEY_PREFIX must be configured.'
}

# # Paths are based from the root of the GIT repository
# $paths = @(
#     './cloudformation'
# )

# foreach ($path in $paths) {
#     Write-Host "Processing cloudformation Templates in '$path':"
#     # All cloudformation Templates to publish are located in or below the "./cloudformation" folder
#     foreach ($file in (Get-ChildItem -Path $path -Recurse -File -Filter "*.yml")) {

#         '' # Blank line to separate CodeBuild Output

#         # Calculate the S3 Key Prefix, keeping the correct Folder Structure
#         if ($file.Name -like '*controlplane.yml') {
#             $s3KeyPrefix = '{0}/cloudformation/{1}' -f $env:S3_KEY_PREFIX, $file.Directory.Name
#         }
#         elseif ($file.Directory.Name -like '*childtemplates*') {
#             # Find the parent template path
#             $parentPath = Split-Path -Path $file.Directory
#             $templatePath = Split-Path -Path $parentPath -Leaf
#             $s3KeyPrefix = '{0}/cloudformation/{1}/{2}' -f $env:S3_KEY_PREFIX, $templatePath, $file.Directory.Name
#         }
#         elseif ($file.Directory.Name -eq 'manual') {
#             Write-Host 'Manually deployed CFN detected. Skipping.'
#             continue
#         }
#         else {
#             throw 'Unexpected directory encountered inside cloudformation folder'
#         }

#         $s3Key = '{0}/{1}' -f $s3KeyPrefix, $file.Name
#         Write-Host " - $s3Key"
#         Write-S3Object -BucketName $env:ARTIFACT_S3_BUCKET -Key $s3Key -File $file.FullName

#         Remove-Variable -Name @('s3Key', 's3KeyPrefix') -ErrorAction SilentlyContinue
#     }
# }
# Update the ControlPlane Parameters JSON files with the target Artifact S3 Bucket.
# All JSON files will be updated, however the deployment CodePipeline is hard coded
# to a specific JSON file so other deployments will not be affected.
foreach ($controlPlaneFolder in (Get-ChildItem -Path './cloudformation' -Recurse -Filter '*control_plane_parameters' -Directory)) {
    foreach ($file in (Get-ChildItem -Path $controlPlaneFolder.FullName -Filter '*.json')) {
        Write-Host "Updating $file"
        $fileContent = Get-Content -Path $file.FullName -Raw | ConvertFrom-Json

        $fileContent.Parameters.ArtifactS3Bucket = $env:ARTIFACT_S3_BUCKET
        $fileContent.Parameters.ArtifactS3KeyPrefix = $env:S3_KEY_PREFIX

        $fileContent | ConvertTo-Json -Compress -Depth 6 | Out-File -FilePath $file.FullName -Force
    }
}