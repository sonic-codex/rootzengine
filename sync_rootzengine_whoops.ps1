# PowerShell script to sync up-to-date code from rootzengineWhoops into src/rootzengine

# Mirror audio, core, scripts, api, midi and tests
robocopy .\rootzengineWhoops\audio .\src\rootzengine\audio /MIR /E
robocopy .\rootzengineWhoops\core .\src\rootzengine\core /MIR /E
robocopy .\rootzengineWhoops\scripts .\src\rootzengine\scripts /MIR /E
robocopy .\rootzengineWhoops\api .\src\rootzengine\api /MIR /E
robocopy .\rootzengineWhoops\midi .\src\rootzengine\midi /MIR /E
robocopy .\rootzengineWhoops\tests .\tests /MIR /E
robocopy .\rootzengineWhoops\configs .\configs /MIR /E

# Remove stale duplicates (add any paths you want to clean up here)
# Remove-Item .\src\rootzengine\audio\features.py -Force

Write-Host "Sync complete. Please verify and fix any import paths as needed."
