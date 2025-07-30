from logger_local.LoggerComponentEnum import LoggerComponentEnum

CRITERION_ENTITY_TYPE_ID = 4

CRITERIA_LOCAL_PYTHON_COMPONENT_ID = 210
CRITERIA_LOCAL_PYTHON_COMPONENT_NAME = 'criteria-local-python'
DEVELOPER_EMAIL = 'akiva.s@circ.zone'

CRITERIA_CODE_LOGGER_OBJECT = {
    'component_id': CRITERIA_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': CRITERIA_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email": DEVELOPER_EMAIL
}

CRITERIA_TEST_LOGGER_OBJECT = {
    'component_id': CRITERIA_LOCAL_PYTHON_COMPONENT_ID,
    'component_name': CRITERIA_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    "developer_email": DEVELOPER_EMAIL
}
