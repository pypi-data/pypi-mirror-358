from datetime import datetime
from functools import lru_cache
from typing import Dict

from database_mysql_local.generic_crud import GenericCRUD
from database_mysql_local.generic_mapping import GenericMapping
from language_remote.lang_code import LangCode
from logger_local.MetaLogger import MetaLogger
from person_local.persons_local import PersonsLocal

from .constants_profile_local import PROFILE_LOCAL_PYTHON_LOGGER_CODE, DEFAULT_LANG_CODE

# TODO Can you please confirm that when we create non-main record (i.e. profile) is_main=NULL and not is_main=FALSE? We should add to all tests creating two non main records to verify it.  # noqa


class ProfilesLocal(GenericCRUD, metaclass=MetaLogger, object=PROFILE_LOCAL_PYTHON_LOGGER_CODE):
    def __init__(self, is_test_data: bool = False):
        super().__init__(default_schema_name="profile", default_table_name="profile_table",
                         default_view_table_name="profile_view", default_column_name="profile_id",
                         is_test_data=is_test_data)

    # TODO Shall we give insert() the main_person_id or shell insert() UPSERT person?
    # TODO shall we move main_person_id into profile_dict? And reduce the number of parameters
    # TODO Please add a test of adding the same profile twice for the same user, it should raise an exception
    def insert(self, *, profile_dict: Dict[str, any], main_person_id: int) -> int:  # noqa
        """Returns the new profile_id
        TODO Please document the exceptions i.e. profile already exist
        """
        if "main_person_id" not in profile_dict:
            profile_dict["main_person_id"] = main_person_id
        if 'gender_id' in profile_dict:
            profile_dict["profile.gender_id"] = profile_dict.pop('gender_id')
        if "main_user_id" in profile_dict:
            profile_dict["profile.main_user_id"] = profile_dict.pop('main_user_id')
        if not isinstance(profile_dict.get('preferred_lang_code'), str):
            profile_dict["preferred_lang_code"] = profile_dict.get(
                'preferred_lang_code', DEFAULT_LANG_CODE).value

        valid_columns = ['experience_years_min', 'identifier', 'internal_description', 'is_approved',
                         'is_business_profile', 'is_employed', 'is_looking_for_job', 'is_main', 'is_rip', 'is_system',
                         'last_dialog_workflow_state_id_old', 'main_location_id', 'main_person_id', 'main_phone_id',
                         'number', 'preferred_lang_code', 'profile.gender_id', 'profile.main_email_address',
                         'profile.main_user_id', 'profile.name', 'profile_id', 'profile_type_id', 'stars',
                         'visibility_id']

        profile_dict = {k: v for k, v in profile_dict.items() if k in valid_columns}
        profile_dict_ml = profile_dict.copy()
        if "name" in profile_dict:
            profile_dict['profile.name'] = profile_dict.pop('name')
        elif 'profile.name' not in profile_dict:
            profile_dict['profile.name'] = profile_dict_ml.get('title')
        if 'title' not in profile_dict_ml:
            profile_dict_ml['title'] = profile_dict.get('profile.name')

        profile_dict.pop('title', None)
        profile_dict.pop('title_approved', None)
        super().insert(data_dict=profile_dict)

        profile_id = self.cursor.lastrowid()
        profile_ml_table_dict = {
            "profile_id": profile_id,
            "lang_code": profile_dict_ml.get('lang_code', DEFAULT_LANG_CODE).value,
            "title": profile_dict_ml['title'],  # Cannot be None
            "title_approved": profile_dict_ml.get('title_approved'),
            "about": profile_dict_ml.get('about')
        }
        super().insert(table_name="profile_ml_table", data_dict=profile_ml_table_dict)
        self.__insert_person_profile(person_id=main_person_id, profile_id=profile_id)

        return profile_id

    def update(self, profile_dict: Dict[str, any]) -> None:
        profile_id = profile_dict['profile_id']
        profile_dict = {
            "main_person_id": profile_dict.get('main_person_id'),
            "profile.name": profile_dict.get('profile.name'),
            "profile.main_user_id": profile_dict.get('profile.main_user_id'),
            "is_main": profile_dict.get('is_main'),
            "visibility_id": profile_dict.get('visibility_id'),
            "is_approved": profile_dict.get('is_approved'),
            "profile_type_id": profile_dict.get('profile_type_id'),
            "preferred_lang_code": profile_dict.get('preferred_lang_code', DEFAULT_LANG_CODE).value,
            "experience_years_min": profile_dict.get('experience_years_min'),
            "main_phone_id": profile_dict.get('main_phone_id'),
            "is_rip": profile_dict.get('is_rip'),
            "profile.gender_id": profile_dict.get('profile.gender_id'),
            "stars": profile_dict.get('stars'),
        }
        self.update_by_column_and_value(column_value=profile_id, data_dict=profile_dict)

        profile_ml_dict = {
            "profile_id": profile_id,
            "lang_code": profile_dict.get('lang_code', DEFAULT_LANG_CODE).value,
            "title": profile_dict['profile.name'],
            "title_approved": profile_dict.get('title_approved'),
            "about": profile_dict.get('about')
        }
        self.update_by_column_and_value(table_name="profile_ml_table",
                                        column_value=profile_id, data_dict=profile_ml_dict)

    # TODO develop get_profile_object_by_profile_id( self, profile_id: int ) -> Profile[]:
    # TODO I think it is more accurate to call it get_profile_dict_by_profile_id(...), as _dict can be str in a format of a DICT
    @lru_cache
    def get_profile_dict_by_profile_id(self, profile_id: int) -> Dict[str, any]:
        profile_ml_dict = self.select_one_dict_by_column_and_value(
            view_table_name="profile_ml_view", column_value=profile_id)
        profile_dict = self.select_one_dict_by_column_and_value(column_value=profile_id)

        if not profile_ml_dict or not profile_dict:
            return {}
        return {**profile_ml_dict, **profile_dict}

    @lru_cache
    def get_profile_id_by_email_address(self, email_address: str) -> int:
        return self.select_one_dict_by_column_and_value(column_name="profile.main_email_address",
                                                        column_value=email_address,
                                                        select_clause_value="profile_id").get('profile_id')

    def delete_by_profile_id(self, profile_id: int):
        self.delete_by_column_and_value(column_value=profile_id)

    @lru_cache  # TODO: preferred_lang_code can change over time
    def get_preferred_lang_code_by_profile_id(self, profile_id: int) -> LangCode:
        preferred_lang_code = self.select_one_value_by_column_and_value(
            column_value=profile_id, select_clause_value='preferred_lang_code')
        if not preferred_lang_code:
            preferred_lang_code = DEFAULT_LANG_CODE
        else:
            preferred_lang_code = LangCode(preferred_lang_code)
        return preferred_lang_code

    def get_test_profile_id(self) -> int:
        person_id = PersonsLocal().get_test_person_id()
        test_name = f"Test Profile {datetime.now().strftime('%Y/%m/%d-%H:%M:%S')}"
        return self.get_test_entity_id(entity_name="profile",
                                       insert_function=self.insert,
                                       insert_kwargs={"profile_dict": {"name": test_name},
                                                      "main_person_id": person_id})

    def insert_profile_type(self, is_test_data: bool = False) -> int:
        profile_type_table_dict = {"is_test_data": is_test_data or self.is_test_data}
        profile_type_id = super().insert(table_name="profile_type_table", data_dict=profile_type_table_dict)
        return profile_type_id

    @lru_cache
    def get_test_profile_type_id(self) -> int:
        return self.get_test_entity_id(entity_name="profile_type",
                                       insert_function=self.insert_profile_type)

    # TODO: Move this method to https://github.com/circles-zone/person-profile-local-python-package
    def __insert_person_profile(self, person_id: int, profile_id: int) -> int:
        """
        Insert person_profile
        :param person_id: person_id
        :param profile_id: profile_id
        :return: person_profile_id
        """
        if person_id is not None:
            generic_mapping_instance = GenericMapping(
                default_schema_name="person_profile", default_table_name="person_profile_table",
                default_column_name="person_profile_id", default_entity_name1="person",
                default_entity_name2="profile", is_test_data=self.is_test_data)
            person_profile_id = generic_mapping_instance.insert_mapping_if_not_exists(
                entity_name1="person", entity_name2="profile",
                entity_id1=person_id, entity_id2=profile_id,
                view_table_name="person_profile_view")
            return person_profile_id
