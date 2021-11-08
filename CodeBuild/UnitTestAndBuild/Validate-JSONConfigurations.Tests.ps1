$paths = @(
    '../../cloudformation'
)
$files = Get-ChildItem -Path $paths -File -Recurse -Filter '*.json'
$ErrorActionPreference = 'Stop'
BeforeAll {

}

Describe -Name 'JSON Configuration File Validation' -Fixture {
    Context -Name 'JSON Parameter Files' -Foreach $files {
        foreach ($file in $files) {
            BeforeAll {
                $file = $_
            }
            Context -Name $file.Name -Fixture {
                It -Name 'is valid' -Test {
                    { $null = ConvertFrom-Json -InputObject (Get-Content -Path $file.FullName -Raw) } | Should -Not -Throw
                }
            }
        } #foreach_file
    } #context_json_paramter_files
} #describe