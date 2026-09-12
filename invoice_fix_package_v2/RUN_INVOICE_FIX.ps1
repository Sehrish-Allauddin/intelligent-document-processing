Set-Location (Split-Path -Parent $PSScriptRoot)
& .\venv\Scripts\python.exe .\invoice_fix_package\fix_invoice_module.py
& .\venv\Scripts\python.exe -m py_compile .\src\pipelines\document_pipeline.py .\streamlit_app\app.py
Write-Host ""
Write-Host "INVOICE FIX COMPLETE" -ForegroundColor Green
Write-Host "Restart Streamlit:"
Write-Host "streamlit run .\streamlit_app\app.py"
