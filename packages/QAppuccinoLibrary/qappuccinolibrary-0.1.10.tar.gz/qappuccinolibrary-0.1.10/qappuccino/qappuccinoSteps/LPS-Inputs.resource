*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic input
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Input Text Into Alert
    [Arguments]    ${put_your_text_here}
    Input Text Into Alert    ${put_your_text_here}

LPS.Input Text By Id
    [Arguments]    ${put_the_id_of_element}    ${put_your_text_here}
    Input Text    id=${put_the_id_of_element}    ${put_your_text_here}

LPS.Input Text By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${put_your_text_here}
    Input Text    xpath=${put_the_xpath_of_element}    ${put_your_text_here}

LPS.Input Text By Class
    [Arguments]    ${put_the_class_of_element}    ${put_your_text_here}
    Input Text    class=${put_the_class_of_element}    ${put_your_text_here}

LPS.Input Password By Id
    [Arguments]    ${put_the_id_of_element}    ${put_your_text_here}
    Input Password    id=${put_the_id_of_element}    ${put_your_text_here}

LPS.Input Password By XPath
    [Arguments]    ${put_the_xpath_of_element}    ${put_your_text_here}
    Input Password    xpath=${put_the_xpath_of_element}    ${put_your_text_here}

LPS.Input Password By Class
    [Arguments]    ${put_the_class_of_element}    ${put_your_text_here}
    Input Password    class=${put_the_class_of_element}    ${put_your_text_here}

LPS.Clear Text By Id
    [Arguments]    ${put_the_id_of_element}
    Clear Element Text    id=${put_the_id_of_element}

LPS.Clear Text By XPath
    [Arguments]    ${put_the_xpath_of_element}
    Clear Element Text    xpath=${put_the_xpath_of_element}

LPS.Clear Text By Class
    [Arguments]    ${put_the_class_of_element}
    Clear Element Text    class=${put_the_class_of_element}

LPS.Choose File By Id
    [Arguments]    ${put_the_id_of_element}     ${put_your_path_here}
    Choose File    id=${put_the_id_of_element}    ${put_your_path_here}

LPS.Choose File By XPath
    [Arguments]    ${put_the_xpath_of_element}     ${put_your_path_here}
    Choose File    xpath=${put_the_xpath_of_element}    ${put_your_path_here}

LPS.Choose File By Class
    [Arguments]    ${put_the_class_of_element}     ${put_your_path_here}
    Choose File    class=${put_the_class_of_element}    ${put_your_path_here}

LPS.Press Key by Id
    [Arguments]     ${put_the_id_of_element}    ${put_key_here}
    Press Key    id=${put_the_id_of_element}    ${put_key_here}

LPS.Press Key by XPath
    [Arguments]     ${put_the_xpath_of_element}    ${put_key_here}
    Press Key    xpath=${put_the_xpath_of_element}    ${put_key_here}

LPS.Press Key by Class
    [Arguments]     ${put_the_class_of_element}    ${put_key_here}
    Press Key    class=${put_the_class_of_element}    ${put_key_here}

LPS.Press Keys
    Press Keys