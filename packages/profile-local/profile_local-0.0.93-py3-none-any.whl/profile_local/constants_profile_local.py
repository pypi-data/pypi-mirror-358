from language_remote.lang_code import LangCode
from logger_local.LoggerComponentEnum import LoggerComponentEnum

DEFAULT_LANG_CODE = LangCode.ENGLISH

PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 170
PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'profile-local python package'

PROFILE_LOCAL_PYTHON_LOGGER_CODE = {
    'component_id': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

OBJECT_TO_INSERT_TEST = {
    'component_id': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': PROFILE_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Unit_Test.value,
    'testing_framework': LoggerComponentEnum.testingFramework.pytest.value,
    'developer_email': 'tal.g@circ.zone'
}
