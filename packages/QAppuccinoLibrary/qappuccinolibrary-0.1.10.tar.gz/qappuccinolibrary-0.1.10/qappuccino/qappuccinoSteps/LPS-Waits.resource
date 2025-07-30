*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic waits
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Wait Until Element Is Visible By Id
    [Arguments]    ${put_the_id_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Page Contains Element    id=${put_the_id_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Visible By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Page Contains Element    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Visible By Class
    [Arguments]    ${put_the_class_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Page Contains Element    class=${put_the_class_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Element Contains Text By Id
    [Arguments]    ${put_the_id_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}=30s
    Wait Until Element Contains    id=${put_the_id_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}

LPS.Wait Until Element Contains Text By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}=30s
    Wait Until Element Contains    xpath=${put_the_xpath_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}

LPS.Wait Until Element Contains Text By Class
    [Arguments]    ${put_the_class_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}=30s
    Wait Until Element Contains    class=${put_the_class_of_element}    ${put_your_text_here}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Not Visible By Id
    [Arguments]    ${put_the_id_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Not Visible    id=${put_the_id_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Not Visible By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Not Visible    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Not Visible By Class
    [Arguments]    ${put_the_class_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Not Visible    class=${put_the_class_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Page Contains Text
    [Arguments]    ${put_your_text_here}    ${set_timeout_in_seconds}=30s
    Wait Until Page Contains    ${put_your_text_here}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Interactable by Id
    [Arguments]    ${put_the_id_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Visible    id=${put_the_id_of_element}    ${set_timeout_in_seconds}
    Wait Until Element Is Enabled    id=${put_the_id_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Interactable by XPath
    [Arguments]    ${put_the_xpath_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Visible    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}
    Wait Until Element Is Enabled    xpath=${put_the_xpath_of_element}    ${set_timeout_in_seconds}

LPS.Wait Until Element Is Interactable by Class
    [Arguments]    ${put_the_class_of_element}    ${set_timeout_in_seconds}=30s
    Wait Until Element Is Visible    xpath=${put_the_class_of_element}    ${set_timeout_in_seconds}
    Wait Until Element Is Enabled    xpath=${put_the_class_of_element}    ${set_timeout_in_seconds}

LPS.Wait For Seconds
    [Arguments]    ${put_seconds}=3s
    Log    ⏳ Waiting for ${put_seconds} ...
    Sleep   ${put_seconds}