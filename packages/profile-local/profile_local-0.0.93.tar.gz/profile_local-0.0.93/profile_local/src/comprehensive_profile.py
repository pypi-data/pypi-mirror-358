from typing import Dict

from database_mysql_local.point import Point
from email_address_local.email_address import EmailAddressesLocal
from gender_local.gender import Gender
from group_profile_remote.group_profile import GroupProfilesRemote
from group_remote.groups_remote import GroupsRemote
from language_remote.lang_code import LangCode
from location_local.locations_local_crud import LocationsLocal
from logger_local.MetaLogger import MetaLogger
from operational_hours_local.operational_hours import OperationalHours
from profile_profile_local.profile_profile import ProfileProfile
# TODO from profile_reaction_local.profile_reactions
from profile_reaction_local.profile_reaction import ProfileReactions
from reaction_local.reaction import ReactionsLocal
from storage_local.aws_s3_storage_local.Storage import Storage
from storage_local.aws_s3_storage_local.StorageConstants import FileTypeEnum

from .constants_profile_local import PROFILE_LOCAL_PYTHON_LOGGER_CODE, DEFAULT_LANG_CODE
from .profiles_local import ProfilesLocal

from dotenv import load_dotenv
load_dotenv()

# TODO Shall we use LocationLocal().get_test_longitude() and latiture?
DEFAULT_LONGITUDE = 0
DEFAULT_LATITUDE = 0


class ComprehensiveProfilesLocal(metaclass=MetaLogger, object=PROFILE_LOCAL_PYTHON_LOGGER_CODE):
    def __init__(self, is_test_data: bool = False):
        self.location_local = LocationsLocal(is_test_data=is_test_data)
        self.profile_local = ProfilesLocal(is_test_data=is_test_data)
        self.storage = Storage(is_test_data=is_test_data)
        self.gender = Gender(is_test_data=is_test_data)
        self.profile_profile = ProfileProfile()
        self.group_profiles_remote = GroupProfilesRemote(is_test_data=is_test_data)
        self.email_addresses_local = EmailAddressesLocal(is_test_data=is_test_data)
        self.operational_hours = OperationalHours()
        self.reaction = ReactionsLocal(is_test_data=is_test_data)
        self.profile_reactions = ProfileReactions(is_test_data=is_test_data)

    # TODO: rename profile_dict to something like compound_profile_dict (& backword compatibility)
    def insert(self, profile_dict: dict, lang_code: LangCode) -> int:
        """Returns the profile_id of the inserted profile"""
        # TODO: split into multiple functions for each `if x in profile_dict`
        profile_id = location_id = None

        if "location" in profile_dict:
            location_entry: Dict[str, any] = profile_dict["location"]
            location_data: Dict[str, any] = {
                "coordinate": Point(longitude=location_entry.get("coordinate", {}).get("latitude", DEFAULT_LATITUDE),
                                    latitude=location_entry.get("coordinate", {}).get("longitude", DEFAULT_LONGITUDE)),
                "address_local_language": location_entry.get("address_local_language"),
                "address_english": location_entry.get("address_english"),
                "postal_code": location_entry.get("postal_code"),
                "phonecode": location_entry.get("phonecode"),
                "neighborhood": location_entry.get("neighborhood"),
                "county": location_entry.get("county"),
                "region": location_entry.get("region"),
                "state": location_entry.get("state"),
                "country": location_entry.get("country")
            }
            location_id = self.location_local.insert(data=location_data, lang_code=lang_code)

        # Insert person to db
        if 'person' in profile_dict:
            # person_dict: Dict[str, any] = profile_dict['person']

            # TODO I would expect the 1st thing we do with person_dict is "person: PersonLocal(person_dict)". Can we do this approach on all entities?

            # TODO: I prefer we use "person.getGender()"
            # Why shall we push those comments to our repo?
            # gender_id = self.gender.get_gender_id_by_title(person_entry.get('gender'))
            # person_data: Dict[str, any] = {
            #     'last_coordinate': person_entry.get('last_coordinate'),
            # }
            # TODO: Why do we need gender_id and person_data?
            # Person class has errors - TODO Let's fix them
            '''
            person_dto = PersonDto(
                gender_id, person_data.get('last_coordinate'),
                person_data.get('location_id'))

            # TODO We prefer PersonsLocal.insert(person) which updates both person_table and person_ml_table
            person_id = PersonsLocal.insert(person_dto)
            PersonsLocal.insert_person_ml(
                person_id,
                lang_code,
                person_data.get('first_name'),
                person_data.get('last_name'))
            '''

        # Insert profile to db
        if 'profile' in profile_dict and 'person_id' in profile_dict.get("person", {}):
            profile_id = self.profile_local.insert(profile_dict=profile_dict['profile'],
                                                   main_person_id=profile_dict['person']['person_id'])

        # insert profile_profile to db
        if 'profile_profile' in profile_dict:
            profile_profile_entry: Dict[str, any] = profile_dict['profile_profile']
            for i in profile_profile_entry:
                profile_profile_part_entry: Dict[str, any] = profile_profile_entry[i]
                profile_profile_data: Dict[str, any] = {
                    'from_profile_id': profile_profile_part_entry.get('from_profile_id'),
                    'relationship_type_id': profile_profile_part_entry.get('relationship_type_id'),
                    'job_title': profile_profile_part_entry.get('job_title', None)
                }
                profile_profile_id = self.profile_profile.insert_profile_profile(
                    profile_id1=profile_profile_data['from_profile_id'], profile_id2=profile_id,
                    relationship_type_id=profile_profile_data['relationship_type_id'],
                    job_title=profile_profile_data['job_title'])
                self.logger.info(object={"profile_profile_id": profile_profile_id})

        # insert group to db
        if 'group' in profile_dict:
            group_entry: Dict[str, any] = profile_dict['group']
            group_id = GroupsRemote().create_group(
                title=group_entry.get('title'),
                lang_code=group_entry.get('lang_code', DEFAULT_LANG_CODE),
                parent_group_id=group_entry.get('parent_group_id'),
                is_interest=group_entry.get('is_interest'),
                image=group_entry.get('image'))
            self.logger.info(object={"group_id": group_id})
            # TODO: create_group returns a response and sometimes bad status code

        # insert group_profile to db
        if 'group_profile' in profile_dict:
            group_profile_entry: Dict[str, any] = profile_dict['group_profile']
            group_profile_data: Dict[str, any] = {
                'group_id': group_profile_entry.get('group_id'),
                'relationship_type_id': group_profile_entry.get('relationship_type_id'),
            }
            group_profile_id = self.group_profiles_remote.create(
                group_id=group_profile_data['group_id'],
                relationship_type_id=group_profile_data['relationship_type_id'])
            self.logger.info(object={"group_profile_id": group_profile_id})

        # insert email to db
        if 'email' in profile_dict:
            email_entry: Dict[str, any] = profile_dict['email']
            email_address_dict: Dict[str, any] = {
                'email_address': email_entry.get('email_address'),
                'lang_code': email_entry.get('lang_code', DEFAULT_LANG_CODE),
                'name': email_entry.get('name'),
            }
            email_address_id = self.email_addresses_local.insert(
                email_address_dict['email_address'], email_address_dict['lang_code'],
                email_address_dict['name'])
            self.logger.info(object={"email_address_id ": email_address_id})

        # Insert storage to db
        if "storage" in profile_dict:
            storage_data = {
                "path": profile_dict["storage"].get("path"),
                "filename": profile_dict["storage"].get("filename"),
                "region": profile_dict["storage"].get("region"),
                "url": profile_dict["storage"].get("url"),
                "file_extension": profile_dict["storage"].get("file_extension"),
                "file_type": profile_dict["storage"].get("file_type")
            }
            if storage_data["file_type"] == "Profile Image":
                if storage_data.get("url"):
                    local_file_path = storage_data["filename"]
                    # TODO save_image_in_storage_by_url_str( image_url_str ...
                    self.storage.save_image_in_storage_by_url(image_url=storage_data["url"],
                                                              local_file_path=local_file_path,
                                                              profile_id=profile_id,
                                                              # TODO file_type_id -> file_type: FileTypeEnum
                                                              file_type_id=FileTypeEnum.PROFILE_IMAGE.value),
                else:
                    self.logger.warning("No URL provided for profile image")

        # Insert reaction to db
        if "reaction" in profile_dict:
            reaction_ml_dict = {
                "title": profile_dict["reaction"].get("title"),
                "description": profile_dict["reaction"].get("description"),
            }
            reaction_dict = {
                "value": profile_dict["reaction"].get("value"),
                "image": profile_dict["reaction"].get("image"),
            }
            reaction_id, reaction_ml_id = self.reaction.insert(
                reaction_dict=reaction_dict, reaction_ml_dict=reaction_ml_dict, lang_code=lang_code)
            # Insert profile-reactions to db
            self.profile_reactions.insert(profile_id=profile_id, reaction_id=reaction_id)

        # Insert operational hours to db
        if "operational_hours" in profile_dict:
            operational_hours_list_of_dicts = OperationalHours.generate_hours_list(profile_dict["operational_hours"])
            self.operational_hours.insert(profile_id, location_id, operational_hours_list_of_dicts)

        return profile_id
