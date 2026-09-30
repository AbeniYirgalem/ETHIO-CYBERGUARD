<#
.SYNOPSIS
    ETHIO-CYBERGUARD Windows Endpoint Security Event Collector
.DESCRIPTION
    Polls and streams Windows Security and PowerShell Operational logs,
    normalizes to the ETHIO-CYBERGUARD standard ECS schema, and forwards
    via HTTP REST or WebSocket to the ingestion service.
#>

param (
    [string]$IngestUrl = "http://localhost:8000/api/v1/events/ingest",
    [string]$ApiKey = "ecg_agent_token_dev_secret",
    [int]$PollIntervalSeconds = 5,
    [switch]$VerboseOutput = $true
)

$HostName = $env:COMPUTERNAME
$IPAddress = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.InterfaceAlias -notmatch 'Loopback' } | Select-Object -First 1).IPAddress

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "🛡️ ETHIO-CYBERGUARD Windows Security Collector Active" -ForegroundColor Green
Write-Host "Host: $HostName | IP: $IPAddress" -ForegroundColor Yellow
Write-Host "Ingestion Endpoint: $IngestUrl" -ForegroundColor Gray
Write-Host "======================================================================" -ForegroundColor Cyan

function Send-SecurityEvent {
    param ([hashtable]$EventData)

    $JsonBody = $EventData | ConvertTo-Json -Depth 6
    try {
        $headers = @{
            "Content-Type" = "application/json"
            "X-Agent-Key"  = $ApiKey
        }
        $response = Invoke-RestMethod -Uri $IngestUrl -Method Post -Body $JsonBody -Headers $headers -TimeoutSec 3 -ErrorAction Stop
        if ($VerboseOutput) {
            Write-Host "[+] Forwarded event: $($EventData.event_type) - Severity: $($EventData.severity)" -ForegroundColor DarkCyan
        }
    }
    catch {
        Write-Warning "[-] Ingestion transmission error: $_"
    }
}

# Track last check timestamp
$LastTimestamp = [DateTime]::UtcNow.AddMinutes(-10)

while ($true) {
    $Now = [DateTime]::UtcNow
    
    # 1. Event 4688: Process Creation
    try {
        $ProcEvents = Get-WinEvent -FilterHashtable @{
            LogName   = 'Security'
            Id        = 4688
            StartTime = $LastTimestamp
        } -ErrorAction SilentlyContinue

        foreach ($ev in $ProcEvents) {
            $xml = [xml]$ev.ToXml()
            $eventDataNodes = $xml.Event.EventData.Data
            $dataMap = @{}
            foreach ($d in $eventDataNodes) { $dataMap[$d.Name] = $d.'#text' }

            $processName = $dataMap['NewProcessName']
            $cmdLine = $dataMap['CommandLine']
            $user = $dataMap['SubjectUserName']

            # Assess baseline severity
            $severity = "INFO"
            if ($cmdLine -match "(-enc|-encodedcommand|downloadstring|bypass|mimikatz|invoke-expression|iex)" -or $processName -match "powershell\.exe|cmd\.exe") {
                $severity = "HIGH"
            }

            $normalized = @{
                event_uid     = "win_$(Get-Random)"
                timestamp     = $ev.TimeCreated.ToUniversalTime().ToString("o")
                source        = @{
                    type     = "endpoint"
                    hostname = $HostName
                    ip       = $IPAddress
                    os       = "Windows"
                }
                event_type    = "process_execution"
                severity      = $severity
                user          = $user
                process       = @{
                    name         = [System.IO.Path]::GetFileName($processName)
                    path         = $processName
                    command_line = $cmdLine
                    pid          = $dataMap['ProcessId']
                }
                raw_data      = @{
                    EventID = 4688
                    RecordID = $ev.RecordId
                }
            }

            Send-SecurityEvent -EventData $normalized
        }
    } catch {}

    # 2. Event 4625: Failed Logon (Brute Force Monitoring)
    try {
        $LogonFails = Get-WinEvent -FilterHashtable @{
            LogName   = 'Security'
            Id        = 4625
            StartTime = $LastTimestamp
        } -ErrorAction SilentlyContinue

        foreach ($ev in $LogonFails) {
            $xml = [xml]$ev.ToXml()
            $eventDataNodes = $xml.Event.EventData.Data
            $dataMap = @{}
            foreach ($d in $eventDataNodes) { $dataMap[$d.Name] = $d.'#text' }

            $normalized = @{
                event_uid     = "win_fail_$(Get-Random)"
                timestamp     = $ev.TimeCreated.ToUniversalTime().ToString("o")
                source        = @{
                    type     = "endpoint"
                    hostname = $HostName
                    ip       = $IPAddress
                    os       = "Windows"
                }
                event_type    = "user_logon_failure"
                severity      = "MEDIUM"
                user          = $dataMap['TargetUserName']
                network       = @{
                    source_ip = $dataMap['IpAddress']
                    workstation_name = $dataMap['WorkstationName']
                }
                raw_data      = @{
                    EventID = 4625
                    SubStatus = $dataMap['SubStatus']
                }
            }

            Send-SecurityEvent -EventData $normalized
        }
    } catch {}

    $LastTimestamp = $Now
    Start-Sleep -Seconds $PollIntervalSeconds
}
