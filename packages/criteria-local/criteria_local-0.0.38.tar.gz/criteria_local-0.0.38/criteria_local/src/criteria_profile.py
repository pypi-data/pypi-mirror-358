# TODO: move to another repository and fix the references
import datetime
from collections import defaultdict
from functools import lru_cache
from typing import Tuple

from database_mysql_local.generic_crud import GenericCRUD
from logger_local.MetaLogger import MetaLogger

try:
    from .constants_src import CRITERIA_CODE_LOGGER_OBJECT
    from .criteria_local import CriteriaLocal
except ImportError:  # needed for the CLI
    from constants_src import CRITERIA_CODE_LOGGER_OBJECT
    from criteria_local import CriteriaLocal


# TODO: add the insert_ methods to queue
class CriteriaProfile(GenericCRUD, metaclass=MetaLogger, object=CRITERIA_CODE_LOGGER_OBJECT):
    def __init__(self, is_test_data: bool = False) -> None:
        GenericCRUD.__init__(
            self, default_schema_name="criteria_profile", default_entity_name="criteria_profile", default_table_name="criteria_profile_table",
            is_test_data=is_test_data)
        self.criteria_local_instance = CriteriaLocal(is_test_data=is_test_data)

    def insert_profiles_by_campaign_criteria_set_id(self, campaign_criteria_set_id: int) -> None:
        criteria_set_ids = self.select_multi_value_by_column_and_value(
            schema_name="campaign_criteria_set",
            view_table_name="campaign_criteria_set_view",
            select_clause_value="criteria_set_id",
            column_name="campaign_criteria_set_id",
            column_value=campaign_criteria_set_id)
        self.insert_profiles_by_criteria_set_ids(criteria_set_ids)

    @lru_cache
    def get_criteria_set_ids_list_by_campaign_id(self, campaign_id: int) -> Tuple[int, ...]:
        """Given a campaign_id, find its criteria_set_ids from campaign_criteria_set_view"""
        criteria_set_ids = self.select_multi_value_by_column_and_value(
            schema_name="campaign_criteria_set", view_table_name="campaign_criteria_set_view",
            select_clause_value="criteria_set_id", column_name="campaign_id", column_value=campaign_id)
        return criteria_set_ids

    def insert_profiles_by_campaign_id(self, campaign_id: int) -> None:
        criteria_set_ids = self.get_criteria_set_ids_list_by_campaign_id(
            campaign_id)
        self.insert_profiles_by_criteria_set_ids(criteria_set_ids)

    def insert_profiles_by_criteria_set_ids(self, criteria_set_ids: Tuple[int, ...],
                                            append_where: str = None) -> Tuple[int, int]:
        """
        1. Find all the criteria_ids and entity_type_ids from criteria_set_general_view.
        2. With the entities, get schema_name & criteria_table_name from entity_type_view.
        3. For each entity, get all the profiles that satisfy the criteria.
        4. Insert the profile_id, criteria_id, and batch_timestamp into criteria_profile_table.
        """
        profile_ids_per_criteria_id, profile_ids_per_criteria_set_id = \
            self.criteria_local_instance.get_profile_ids_per_criteria_and_criteria_set_id(
                criteria_set_ids=criteria_set_ids, append_where=append_where)
        # Note: may not be the sql server time
        # The UTC timezone constant was introduced in Python 3.11
        batch_timestamp = datetime.datetime.now(datetime.UTC)
        data_dicts_criterias = []
        criteria_set_list_of_dicts = []
        for criteria_set_id, profiles_ids in profile_ids_per_criteria_set_id.items():
            for profile_id in profiles_ids:
                data_dict_criteria_set = {
                    "profile_id": profile_id,
                    "criteria_set_id": criteria_set_id,
                    "batch_timestamp": batch_timestamp
                }

                if data_dict_criteria_set not in criteria_set_list_of_dicts:
                    criteria_set_list_of_dicts.append(data_dict_criteria_set)

        for criteria_id, profiles_ids in profile_ids_per_criteria_id.items():
            for profile_id in profiles_ids:
                data_dict_criteria = {
                    "profile_id": profile_id,
                    "criteria_id": criteria_id,
                    "batch_timestamp": batch_timestamp
                }
                if data_dict_criteria not in data_dicts_criterias:
                    data_dicts_criterias.append(data_dict_criteria)

        # insert to criteria_profile
        inserted_rows_criteria = super().insert_many_dicts(
            data_dicts=data_dicts_criterias)
        inserted_rows_criteria_set = super().insert_many_dicts(
            table_name="criteria_set_profile_table",
            data_dicts=criteria_set_list_of_dicts)
        self.logger.debug(object=locals())
        return inserted_rows_criteria, inserted_rows_criteria_set

    @lru_cache  # TODO: use our cache to allow list and not just tuple
    def get_profile_ids_per_criteria_set_id(self, criteria_set_ids: Tuple[int, ...]) -> dict[int, Tuple[int, ...]]:
        """Given a set of criteria_set_ids, find the profile_ids from criteria_set_profile_table"""
        result = GenericCRUD.select_multi_dict_by_column_and_value(
            self, view_table_name="criteria_set_profile_view",
            select_clause_value="criteria_set_id, profile_id",
            column_name="criteria_set_id", column_value=criteria_set_ids)

        profile_ids_per_criteria_set_id = defaultdict(tuple)
        for row in result:
            profile_ids_per_criteria_set_id[row["criteria_set_id"]
                                            ] += (row["profile_id"],)
        return profile_ids_per_criteria_set_id

    @lru_cache
    def get_profile_ids_by_criteria_id(self, criteria_id: int) -> Tuple[int, ...]:
        """Given a criteria_id, find the profile_ids from criteria_profile_table"""
        profile_ids = GenericCRUD.select_multi_value_by_column_and_value(
            self, select_clause_value="profile_id", column_name="criteria_id", column_value=criteria_id)
        return profile_ids


if __name__ == "__main__":
    # CLI
    import argparse

    parser = argparse.ArgumentParser(
        description="Insert profiles by criteria_set_ids or campaign_id")

    parser.add_argument("--campaign_id", type=int, required=False)
    parser.add_argument("--criteria_set_ids", type=int,
                        nargs="+", required=False)
    parser.add_argument("--campaign_criteria_set_id", type=int, required=False)

    args = parser.parse_args()
    criteria_local = CriteriaProfile()
    if args.campaign_id:
        criteria_local.insert_profiles_by_campaign_id(
            campaign_id=args.campaign_id)
    elif args.criteria_set_ids:
        criteria_local.insert_profiles_by_criteria_set_ids(
            criteria_set_ids=tuple(args.criteria_set_ids))
    elif args.campaign_criteria_set_id:
        criteria_local.insert_profiles_by_campaign_criteria_set_id(
            campaign_criteria_set_id=args.campaign_criteria_set_id)
    else:
        parser.print_help()
