*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic clicks
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Click Element By Id
    [Arguments]    ${put_the_id_of_element}
    Click Element    id=${put_the_id_of_element}

LPS.Click Element By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Click Element    xpath=${put_the_xpath_of_element}

LPS.Click Element By Class
    [Arguments]    ${put_the_class_of_element}
    Click Element    class=${put_the_class_of_element}

LPS.Click Button By Id
    [Arguments]    ${put_the_id_of_element}
    Click Button    id=${put_the_id_of_element}

LPS.Click Button By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Click Button    xpath=${put_the_xpath_of_element}

LPS.Click Button By Class
    [Arguments]    ${put_the_class_of_element}
    Click Button    class=${put_the_class_of_element}

LPS.Click Link By Id
    [Arguments]    ${put_the_id_of_element}
    Click Link    id=${put_the_id_of_element}

LPS.Click Link By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Click Link    xpath=${put_the_xpath_of_element}

LPS.Click Link By Class
    [Arguments]    ${put_the_class_of_element}
    Click Link    class=${put_the_class_of_element}

LPS.Double Click Element By Id
    [Arguments]    ${put_the_id_of_element}
    Double Click Element    id=${put_the_id_of_element}

LPS.Double Click Element By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Double Click Element    xpath=${put_the_xpath_of_element}

LPS.Double Click Element By Class
    [Arguments]    ${put_the_class_of_element}
    Double Click Element    class=${put_the_class_of_element}

LPS.Click Image By Id
    [Arguments]    ${put_the_id_of_element}
    Click Image    id=${put_the_id_of_element}

LPS.Click Image By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Click Image    xpath=${put_the_xpath_of_element}

LPS.Click Image By Class
    [Arguments]    ${put_the_class_of_element}
    Click Image    class=${put_the_class_of_element}

LPS.Click Element At Coordinates By Id
    [Arguments]    ${put_the_id_of_element}     ${x_offset_value}   ${y_offset_value}
    Click Element At Coordinates    id=${put_the_id_of_element}    ${x_offset_value}    ${y_offset_value}

LPS.Click Element At Coordinates By XPath
    [Arguments]    ${put_the_xpath_of_element}     ${x_offset_value}   ${y_offset_value}
    Click Element At Coordinates    xpath=${put_the_xpath_of_element}    ${x_offset_value}    ${y_offset_value}

LPS.Click Element At Coordinates By Class
    [Arguments]    ${put_the_class_of_element}     ${x_offset_value}   ${y_offset_value}
    Click Element At Coordinates    class=${put_the_class_of_element}    ${x_offset_value}    ${y_offset_value}
