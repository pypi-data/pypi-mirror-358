*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic checks
# ---------------------------------------------

*** Settings ***
Resource    settings.resource
Library     DateTime

*** Keywords ***
LPS.Alert Should Be Present
    [Arguments]     ${put_alert_text_here}  ${put_action_to_take}
    Alert Should Be Present     ${put_alert_text_here}  ${put_action_to_take}

LPS.Element Should Be Visible By Id
    [Arguments]    ${put_the_id_of_element}
    Element Should Be Visible    id=${put_the_id_of_element}

LPS.Element Should Be Visible By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Element Should Be Visible    xpath=${put_the_xpath_of_element}

LPS.Element Should Be Visible By Class
    [Arguments]    ${put_the_class_of_element}
    Element Should Be Visible    class=${put_the_class_of_element}

LPS.Set Focus To Element By Id
    [Arguments]    ${put_the_id_of_element}
    Set Focus To Element    id=${put_the_id_of_element}

LPS.Set Focus To Element By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Set Focus To Element    xpath=${put_the_xpath_of_element}

LPS.Set Focus To Element By Class
    [Arguments]    ${put_the_class_of_element}
    Set Focus To Element    class=${put_the_class_of_element}

LPS.Checkbox Should Be Selected by Id
    [Arguments]    ${put_the_id_of_element}
    Checkbox Should Be Selected    id=${put_the_id_of_element}

LPS.Checkbox Should Be Selected by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Checkbox Should Be Selected    xpath=${put_the_xpath_of_element}

LPS.Checkbox Should Be Selected by Class
    [Arguments]    ${put_the_class_of_element}
    Checkbox Should Be Selected    class=${put_the_class_of_element}

LPS.Checkbox Should Not Be Selected by Id
    [Arguments]    ${put_the_id_of_element}
    Checkbox Should Not Be Selected    id=${put_the_id_of_element}

LPS.Checkbox Should Not Be Selected by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Checkbox Should Not Be Selected    xpath=${put_the_xpath_of_element}

LPS.Checkbox Should Not Be Selected by Class
    [Arguments]    ${put_the_class_of_element}
    Checkbox Should Not Be Selected    class=${put_the_class_of_element}

LPS.Page Should Contain Checkbox by Id
    [Arguments]    ${put_the_id_of_element}
    Page Should Contain Checkbox    id=${put_the_id_of_element}

LPS.Page Should Contain Checkbox by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Page Should Contain Checkbox    xpath=${put_the_xpath_of_element}

LPS.Page Should Contain Checkbox by Class
    [Arguments]    ${put_the_class_of_element}
    Page Should Contain Checkbox    class=${put_the_class_of_element}

LPS.Page Should Contain Button by Id
    [Arguments]    ${put_the_id_of_element}
    Page Should Contain Button    id=${put_the_id_of_element}

LPS.Page Should Contain Button by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Page Should Contain Button    xpath=${put_the_xpath_of_element}

LPS.Page Should Contain Button by Class
    [Arguments]    ${put_the_class_of_element}
    Page Should Contain Button    class=${put_the_class_of_element}

LPS.Page Should Contain Element by Id
    [Arguments]    ${put_the_id_of_element}
    Page Should Contain Element    id=${put_the_id_of_element}

LPS.Page Should Contain Element by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Page Should Contain Element    xpath=${put_the_xpath_of_element}

LPS.Page Should Contain Element by Class
    [Arguments]    ${put_the_class_of_element}
    Page Should Contain Element    class=${put_the_class_of_element}

LPS.Page Should Contain Image by Id
    [Arguments]    ${put_the_id_of_element}
    Page Should Contain Image    id=${put_the_id_of_element}

LPS.Page Should Contain Image by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Page Should Contain Image    xpath=${put_the_xpath_of_element}

LPS.Page Should Contain Image by Class
    [Arguments]    ${put_the_class_of_element}
    Page Should Contain Image    class=${put_the_class_of_element}

LPS.Page Should Contain Radio Button by Id
    [Arguments]    ${put_the_id_of_element}
    Page Should Contain Radio Button    id=${put_the_id_of_element}

LPS.Page Should Contain Radio Button by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Page Should Contain Radio Button    xpath=${put_the_xpath_of_element}

LPS.Page Should Contain Radio Button by Class
    [Arguments]    ${put_the_class_of_element}
    Page Should Contain Radio Button    class=${put_the_class_of_element}

LPS.Page Should Contain Textfield by Id
    [Arguments]    ${put_the_id_of_element}
    Page Should Contain Textfield    id=${put_the_id_of_element}

LPS.Page Should Contain Textfield by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Page Should Contain Textfield    xpath=${put_the_xpath_of_element}

LPS.Page Should Contain Textfield by Class
    [Arguments]    ${put_the_class_of_element}
    Page Should Contain Textfield    class=${put_the_class_of_element}

LPS.Page Should Contain List by Id
    [Arguments]    ${put_the_id_of_element}
    Page Should Contain List    id=${put_the_id_of_element}

LPS.Page Should Contain List by XPath
    [Arguments]    ${put_the_xpath_of_element}
    Page Should Contain List    xpath=${put_the_xpath_of_element}

LPS.Page Should Contain List by Class
    [Arguments]    ${put_the_class_of_element}
    Page Should Contain List    class=${put_the_class_of_element}
    
LPS.Should Be Equal As Numbers
    [Arguments]     ${put_first_number}     ${put_second_number}
    Should Be Equal As Numbers    ${put_first_number}    ${put_second_number}

LPS.Should Be True
    [Arguments]    ${condition}    ${msg}=None
    Should Be True    ${condition}    ${msg}

LPS.Dictionary Should Contain Key
    [Arguments]    ${dictionary}    ${key}    ${msg}=None
    Dictionary Should Contain Key    ${dictionary}    ${key}    ${msg}

LPS.Get Current Date
    [Arguments]    ${result_format}=%Y-%m-%d    ${increment}=0 days
    ${date}=    Get Current Date    result_format=${result_format}    increment=${increment}
    RETURN    ${date}

LPS.File Should Exist
    [Arguments]    ${path}    ${msg}=None
    File Should Exist    ${path}    ${msg}

LPS.Should Be Equal
    [Arguments]    ${first}    ${second}    ${msg}=None    ${values}=None
    Should Be Equal    ${first}    ${second}    ${msg}    ${values}