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
LPS.Open Browser To URL
    [Arguments]    ${put_the_url}    ${put_the_browser}
    Open Browser    ${put_the_url}    ${put_the_browser}

LPS.Maximize Browser Window
    Maximize Browser Window

LPS.Minimize Browser Window
    Minimize Browser Window

LPS.Close Window
    Close Window

LPS.Close All Browser
    Close All Browsers

LPS.Go To URL
    [Arguments]    ${put_the_url}
    Go To    ${put_the_url}

LPS.Go Back To Previous Page
    Go Back

LPS.Get Browser Aliases
    Get Browser Aliases

LPS.Get Browser Id
    Get Browser Ids

LPS.Get Cookie
    [Arguments]     ${put_name_of_cookie}
    Get Cookie    ${put_name_of_cookie}

LPS.Get Cookies
    Get Cookies

LPS.Get Location
    Get Location

LPS.Get Locations
    Get Locations

LPS.Get Session Id
    Get Session Id

LPS.Get Windows Handles
    Get Window Handles

LPS.Get Window Identifiers
    Get Window Identifiers

LPS.Get Window Names
    Get Window Names

LPS.Title Should Be
    [Arguments]     ${put_title_here}
    Title Should Be    ${put_title_here}

LPS.Get Window Titles
    Get Window Titles

LPS.Location Should Be
    [Arguments]     ${put_url_here}
    Location Should Be    ${put_url_here}

LPS.Location Should Contain
    [Arguments]     ${put_expected_here}
    Location Should Contain    ${put_expected_here}

LPS.Close Browser
    Close Browser

LPS.Log
    [Arguments]     ${put_container_here}
    Log     ${put_container_here}

LPS.Should Contain
    [Arguments]    ${container}    ${item}    ${msg}=None    ${values}=None
    Should Contain    ${container}    ${item}    ${msg}    ${values}

LPS.Should Not Contain
    [Arguments]    ${container}    ${item}    ${msg}=None    ${values}=None
    Should Not Contain    ${container}    ${item}    ${msg}    ${values}

LPS.Log Location
    Log Location

LPS.Set Browser Implicit Wait in Seconds
    [Arguments]     ${put_in_seconds}
    Set Browser Implicit Wait    ${put_in_seconds}

LPS.Set Selenium Implicit Wait in Seconds
    [Arguments]     ${put_in_seconds}
    Set Selenium Implicit Wait    ${put_in_seconds}

LPS.Switch Browser
    [Arguments]     ${put_browser_id_or_alias}
    Switch Browser    ${put_browser_id_or_alias}

LPS.Switch Window
    Switch Window