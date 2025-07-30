*** Comments ***
-------------------------------------------------------------------------------
This code is created by LPS PH ODC.
Unauthorized use, modification, distribution, or reproduction of this code
is strictly prohibited. This code shall only be used within LPS and for
its authorized purposes.
Copyright (c) 2024 LPS. All rights reserved.
-------------------------------------------------------------------------------

# ---------------------------------------------
# ✅ Atomic Timestamp and Screenshot
# ---------------------------------------------

*** Settings ***
Resource    settings.resource

*** Keywords ***
LPS.Get Current Timestamp
    ${timestamp}=    Evaluate    datetime.datetime.now().strftime("%Y%m%d%H%M%S")    modules=datetime
    RETURN    ${timestamp}

LPS.Capture Screenshot With Timestamp And Attach To Allure
    [Arguments]    ${put_directory_where_to_save_screenshots}
    ${get_current_timestamp}=    LPS.Get Current Timestamp
    ${set_filename}=    Set Variable    ${get_current_timestamp}_screenshot.png
    Capture Page Screenshot    ${put_directory_where_to_save_screenshots}/${set_filename}
    Attach File    ${put_directory_where_to_save_screenshots}/${set_filename}    Screenshot