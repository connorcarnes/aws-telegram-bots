$paths = @(
    '../../cloudformation'
)
$files = Get-ChildItem -Path $paths -Recurse | Where-Object { $_.Extension -eq '.yml' }
$ErrorActionPreference = 'Stop'
BeforeAll {

}
Describe 'CloudFormation Template Validation' {
    Context -Name 'CloudFormation Templates' -Foreach $files {
        foreach ($file in $files) {
            BeforeAll {
                $file = $_
            }
            Context -Name $file.Name -Fixture {
                It -Name 'is valid' -Test {
                    { Test-CFNTemplate -TemplateBody (Get-Content -Path $file.FullName -Raw) } | Should -Not -Throw
                }
            }
        } #foreach_file
    } #context_cfn_templates
} #describe