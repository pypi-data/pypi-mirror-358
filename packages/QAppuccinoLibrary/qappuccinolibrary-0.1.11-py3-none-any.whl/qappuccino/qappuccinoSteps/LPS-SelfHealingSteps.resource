*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic Self Healing Steps
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Self Healing Click Element
    [Arguments]    ${set_primary_locator}    @{list_fallback_locators}
    ${locators}=    Create List    ${set_primary_locator}    @{list_fallback_locators}
    ${clicked}=     Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Element Should Be Visible    ${locator}    3s
        IF    ${status}
            Click Element    ${locator}
            Log    Clicked element using: ${locator}
            ${clicked}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${clicked}    Fail    All locators failed: ${locators}

LPS.Self Healing Input Text
    [Arguments]    ${set_primary_locator}    ${put_your_text_here}    @{list_fallback_locators}
    ${locators}=    Create List    ${set_primary_locator}    @{list_fallback_locators}
    ${inputted}=    Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Element Should Be Visible    ${locator}    3s
        IF    ${status}
            Input Text    ${locator}    ${put_your_text_here}
            Log    Input text using: ${locator}
            ${inputted}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${inputted}    Fail    All locators failed: ${locators}

LPS.Self Healing Wait Until Element Is Visible
    [Arguments]    ${set_primary_locator}    ${set_timeout_in_seconds}=10s    @{list_fallback_locators}
    ${locators}=    Create List    ${set_primary_locator}    @{list_fallback_locators}
    ${found}=       Set Variable    False
    FOR    ${locator}    IN    @{locators}
        ${status}=    Run Keyword And Return Status    Wait Until Element Is Visible    ${locator}    ${set_timeout_in_seconds}
        IF    ${status}
            Log    Found element using: ${locator}
            ${found}=    Set Variable    True
            Exit For Loop
        END
    END
    Run Keyword Unless    ${found}    Fail    Element not visible for any locator: ${locators}
