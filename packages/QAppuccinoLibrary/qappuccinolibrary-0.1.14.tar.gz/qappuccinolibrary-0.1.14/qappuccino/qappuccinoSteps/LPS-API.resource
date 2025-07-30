*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic browser controls
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Create Session
    [Arguments]    ${alias}    ${base_url}    ${headers}=None    ${cookies}=None    ${auth}=None    ${timeout}=None    ${proxies}=None    ${verify}=True
    ${headers}=    Run Keyword If    '${headers}'=='None'    Create Dictionary    ELSE    Set Variable    ${headers}
    ${cookies}=    Run Keyword If    '${cookies}'=='None'    Create Dictionary    ELSE    Set Variable    ${cookies}
    ${auth}=       Run Keyword If    '${auth}'=='None'       Create Dictionary    ELSE    Set Variable    ${auth}
    ${proxies}=    Run Keyword If    '${proxies}'=='None'    Create Dictionary    ELSE    Set Variable    ${proxies}
    Create Session    ${alias}    ${base_url}    headers=${headers}    cookies=${cookies}    auth=${auth}    timeout=${timeout}    proxies=${proxies}    verify=${verify}

LPS.GET
    [Arguments]    ${url}    ${headers}=None    ${params}=None    ${allow_redirects}=True    ${timeout}=None
    ${headers}=    Run Keyword If    '${headers}'=='None'    Create Dictionary    ELSE    Set Variable    ${headers}
    ${params}=     Run Keyword If    '${params}'=='None'     Create Dictionary    ELSE    Set Variable    ${params}
    ${response}=    GET    ${url}    headers=${headers}    params=${params}    allow_redirects=${allow_redirects}    timeout=${timeout}
    RETURN    ${response}

LPS.OPTIONS
    [Arguments]    ${url}    ${headers}=None    ${allow_redirects}=True    ${timeout}=None
    ${headers}=    Run Keyword If    '${headers}'=='None'    Create Dictionary    ELSE    Set Variable    ${headers}
    ${response}=    OPTIONS    ${url}    headers=${headers}    allow_redirects=${allow_redirects}    timeout=${timeout}
    RETURN    ${response}

LPS.GET On Session
    [Arguments]    ${alias}    ${uri}    ${params}=None    ${headers}=None    ${allow_redirects}=True    ${timeout}=None
    ${headers}=    Run Keyword If    '${headers}'=='None'    Create Dictionary    ELSE    Set Variable    ${headers}
    ${params}=     Run Keyword If    '${params}'=='None'     Create Dictionary    ELSE    Set Variable    ${params}
    ${response}=    Get Request    ${alias}    ${uri}    params=${params}    headers=${headers}    allow_redirects=${allow_redirects}    timeout=${timeout}
    RETURN    ${response}

LPS.Set Variable
    [Arguments]    ${value}
    ${variable}=    Set Variable    ${value}
    RETURN    ${variable}

LPS.Evaluate
    [Arguments]    ${expression}    ${modules}=None
    ${modules}=    Run Keyword If    '${modules}'=='None'    Set Variable    ''    ELSE    Set Variable    ${modules}
    ${result}=    Evaluate    ${expression}    modules=${modules}
    RETURN    ${result}

LPS.Run Process
    [Arguments]    @{args}
    ${result}=    Run Process    @{args}
    RETURN    ${result}

LPS.Run Keyword Unless
    [Arguments]    ${condition}    ${keyword}    @{args}
    Run Keyword Unless    ${condition}    ${keyword}    @{args}

LPS.Fail
    [Arguments]    ${message}=Test failed.
    Fail    ${message}