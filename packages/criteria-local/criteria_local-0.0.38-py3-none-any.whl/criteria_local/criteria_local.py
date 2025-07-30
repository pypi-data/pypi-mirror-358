from collections import defaultdict
from functools import lru_cache
from typing import Tuple

from database_mysql_local.generic_crud_ml import GenericCRUDML
from database_mysql_local.table_columns import table_columns
from logger_local.MetaLogger import MetaLogger
from opensearch_local.our_opensearch import OurOpenSearch
from .criterion import Criterion

try:
    from .constants_src import CRITERIA_CODE_LOGGER_OBJECT, \
        CRITERION_ENTITY_TYPE_ID
except ImportError:  # needed for the CLI
    from constants_src import CRITERIA_CODE_LOGGER_OBJECT, CRITERION_ENTITY_TYPE_ID  # noqa

cache = {}

# TODO Add file to support criteria_set

# TODO: limit recipients in the second phase, i.e. when retrieving the profiles from criteria_profile_table
#   This is security measure either from the database or from the code
#   Let's keep it and reduce to small number such as 100 until we get confidence.
# TODO I think we should move max_audience from campaign_table to campaign_criteria_set, right?


class CriteriaLocal(GenericCRUDML, metaclass=MetaLogger, object=CRITERIA_CODE_LOGGER_OBJECT):
    """CriteriaLocal class"""

    def __init__(self, is_test_data: bool = False) -> None:
        super().__init__(default_schema_name="criteria",
                         is_test_data=is_test_data)

    def insert(self, criterion: Criterion) -> int:  # noqa
        """
        Insert a criterion into the database.
        criterion.entity_type_id is required.

        :param criterion: The criterion to insert.
        :type criterion: Criterion
        :rtype: None
        """
        criteria_dict = criterion.to_dict()
        criterion_id = super().insert(data_dict=criteria_dict)
        return criterion_id

    def update(self, criteria_id: int, new_criterion: Criterion) -> None:
        """
        Update a criterion in the database.

        :param criteria_id: The ID of the criterion to update.
        :param new_criterion: The new criterion.
        :type criteria_id: int
        :type new_criterion: Criterion
        :rtype: None
        """
        criteria_dict = new_criterion.to_dict()
        super().update_by_column_and_value(column_value=criteria_id,
                                           data_dict=criteria_dict)

    def select_criterion_object(self, criteria_id: int) -> Criterion:
        """
        Select a criterion from the database.

        :param criteria_id: The ID of the criterion to select.
        :type criteria_id: int
        :rtype: Criterion
        """
        criterion = self.select_criterion_dict(criteria_id=criteria_id)
        criterion_object = Criterion(**criterion)
        return criterion_object

    def select_criterion_dict(self, criteria_id: int) -> dict:
        """
        Select a criterion from the database.

        :param criteria_id: The ID of the criterion to select.
        :type criteria_id: int
        :rtype: dict
        """
        criterion_dict = super().select_one_dict_by_column_and_value(
            column_value=criteria_id)
        return criterion_dict

    def delete(self, criteria_id: int) -> None:
        """
        Delete a criterion from the database.

        :param criteria_id: The ID of the criterion to delete.
        :type criteria_id: int
        :rtype: None
        """
        self.delete_by_column_and_value(column_value=criteria_id)

    def get_test_criteria_id(self, criterion: Criterion = None, **kwargs) -> int:
        if not criterion:
            criterion = Criterion(
                entity_type_id=CRITERION_ENTITY_TYPE_ID, is_test_data=True, **kwargs)
        test_criteria_id = super().get_test_entity_id(
            entity_name="criteria", insert_function=self.insert, insert_kwargs={"criterion": criterion})
        return test_criteria_id

    @lru_cache
    def get_entity_criteria_by_criterion(self, *, criterion: Criterion, is_criteria: bool = True) -> dict:
        """Get entity details by criterion, based on entity_type_id and where_sql using entity_type_view
        For example, criterion.entity_type_id=17 will return values from people_view, as per entity_type_view"""
        where_sql = criterion.where_sql  # noqa
        entity_type_id = criterion.entity_type_id  # noqa

        # TODO: move to entity repo
        schema_key = "criteria_schema_name" if is_criteria else "schema_name"
        view_key = "criteria_view_name" if is_criteria else "view_name"
        select_clause_value = f"{schema_key}, {view_key}"
        entity = self.select_one_dict_by_column_and_value(
            schema_name="entity_type", view_table_name="entity_type_view",
            column_name="entity_type_id", column_value=entity_type_id,
            select_clause_value=select_clause_value)
        if not entity:
            raise Exception(
                f"entity_type_id {entity_type_id} is not supported")
        schema_name = entity[schema_key]
        view_table_name = entity[view_key]
        if not schema_name or not view_table_name:
            raise Exception(f"{schema_key} or {view_key} not found for entity_type_id {entity_type_id}.\n"
                            f"{schema_key}: {schema_name}, {view_key}: {view_table_name}")
        entity_dict = self.select_one_dict_by_where(
            schema_name=schema_name, view_table_name=view_table_name,
            where=where_sql, select_clause_value="*")
        return entity_dict

    @lru_cache
    def get_childs_criteria_set_ids_per_parent(self) -> dict[int, list[dict]]:
        select_clause_value = "parent_criteria_set_id, child_criteria_set_id, criteria_id, entity_type_id"
        all_rows = self.select_multi_dict_by_where(
            view_table_name="criteria_set_general_view",
            select_clause_value=select_clause_value, where="TRUE")
        childs_criteria_set_ids_per_parent = {}
        for row in all_rows:
            parent_criteria_set_id = row["parent_criteria_set_id"]
            row.pop("parent_criteria_set_id")
            if parent_criteria_set_id not in childs_criteria_set_ids_per_parent:
                childs_criteria_set_ids_per_parent[parent_criteria_set_id] = []
            childs_criteria_set_ids_per_parent[parent_criteria_set_id].append(
                row)
        return childs_criteria_set_ids_per_parent

    # For performance
    @lru_cache  # TODO: split this function into multiple functions
    def get_criterias_per_criteria_set_id(self, criteria_set_ids: Tuple[int, ...]) -> dict[int, list[dict]]:
        """Given (parent) criteria_set_id, find its child_criteria_set_id which now becomes parent_criteria_set_id,
            and continue recursively until all child_criteria_set_id not found in parent_criteria_set_id.
            For each such leaf, return its critiria_id and entity_type_id
            returns: {criteria_set_id: [{criteria_id: int, entity_type_id: int}]}
            """

        childs_criteria_set_ids_per_parent = self.get_childs_criteria_set_ids_per_parent()
        criterias_per_criteria_set_ids = defaultdict(list)

        def recursive_find_criteria_set(parent_criteria_set_id: int) -> None:
            if parent_criteria_set_id not in childs_criteria_set_ids_per_parent:
                # it's a child
                for childs in childs_criteria_set_ids_per_parent.values():
                    for child in childs:
                        if child["child_criteria_set_id"] == parent_criteria_set_id:
                            if not child["criteria_id"] or not child["entity_type_id"]:
                                raise Exception(f"criteria_id and entity_type_id not found for criteria_set_id "
                                                f"{parent_criteria_set_id}")
                            criterias_per_criteria_set_ids[parent_criteria_set_id].append(
                                {"criteria_id": child["criteria_id"], "entity_type_id": child["entity_type_id"]})
                            return
            if parent_criteria_set_id in childs_criteria_set_ids_per_parent:
                for row in childs_criteria_set_ids_per_parent[parent_criteria_set_id]:
                    if row["child_criteria_set_id"] in childs_criteria_set_ids_per_parent:
                        recursive_find_criteria_set(
                            row["child_criteria_set_id"])
                    elif row["criteria_id"] and row["entity_type_id"]:  # leaf
                        criterias_per_criteria_set_ids[parent_criteria_set_id].append(
                            {"criteria_id": row["criteria_id"], "entity_type_id": row["entity_type_id"]})

        for criteria_set_id in criteria_set_ids:
            recursive_find_criteria_set(criteria_set_id)
        if not criterias_per_criteria_set_ids:
            raise Exception(
                f"No criteria found for criteria_set_ids {criteria_set_ids}")
        return criterias_per_criteria_set_ids

    def _get_entity_where(self, *, entity_list_id: int, entity_id: int, entity_name: str,
                          column_name: str, schema_name: str = None, criteria_id: int) -> str:
        if entity_list_id and entity_id:
            self.logger.warning(
                f"Both {entity_name}_list_id and {entity_name}_id are provided. Ignoring the list.")

        if entity_id is not None:
            where = f" AND {column_name} = {entity_id}"
        elif entity_list_id is not None:
            schema_name = schema_name or entity_name
            entity_in_list = self.sql_in_list_by_entity_list_id(
                schema_name=schema_name, entity_name=entity_name, entity_list_id=entity_list_id)
            where = f" AND {column_name} " + entity_in_list
        else:
            where = ""

        if where:
            self.logger.info(
                object={"criteria_id": criteria_id,
                        "entity_name": entity_name, "where": where},
                message=f"Adding {entity_name} criteria to where clause: {where}")

        return where

    # Used both in criteria-local and message-send-local
    def get_where_by_criteria_dict(self, criteria_dict: dict) -> str:
        # TODO add support to user_external_id in criteria_dict
        min_age = criteria_dict.get("min_age")
        max_age = criteria_dict.get("max_age")

        # profile_id didn't receive messages from this campaign for campaign.minimal_days
        where = "TRUE "
        if min_age is not None:
            where += f" AND TIMESTAMPDIFF(YEAR, `person.birthday_date`, CURDATE()) >= {min_age}"
        if max_age is not None:
            where += f" AND TIMESTAMPDIFF(YEAR, `person.birthday_date`, CURDATE()) <= {max_age}"

        # TODO add support to profile_list_id
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("gender_list_id"), entity_id=criteria_dict.get("gender_id"),
            entity_name="gender", criteria_id=criteria_dict['criteria_id'], column_name="`profile.gender_id`")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("location_list_id"), entity_id=criteria_dict.get("location_id"),
            entity_name="location", criteria_id=criteria_dict['criteria_id'], column_name="location_id")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("group_list_id"), entity_id=criteria_dict.get("group_id"),
            entity_name="group", criteria_id=criteria_dict['criteria_id'], column_name="group_profile.group_id")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("country_list_id"), entity_id=criteria_dict.get("country_id"),
            entity_name="country", criteria_id=criteria_dict['criteria_id'], column_name="country_id", schema_name="location")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("county_list_id"), entity_id=criteria_dict.get("county_id"),
            entity_name="county", criteria_id=criteria_dict['criteria_id'], column_name="county_id", schema_name="location")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("state_list_id"), entity_id=criteria_dict.get("state_id"),
            entity_name="state", criteria_id=criteria_dict['criteria_id'], column_name="state_id", schema_name="location")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("city_list_id"), entity_id=criteria_dict.get("city_id"),
            entity_name="city", criteria_id=criteria_dict['criteria_id'], column_name="city_id", schema_name="location")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("label_list_id"), entity_id=criteria_dict.get("label_id"),
            entity_name="label", criteria_id=criteria_dict['criteria_id'], column_name="label_id")
        where += self._get_entity_where(
            entity_list_id=criteria_dict.get("profile_list_id"), entity_id=criteria_dict.get("profile_id"),
            entity_name="profile", criteria_id=criteria_dict['criteria_id'], column_name="profile.profile_id")

        self.logger.info(
            object={"criteria_dict": criteria_dict, "where": where})
        return where

    def get_profiles_ids_satisfying_criteria(self, criteria_dict: dict,
                                             append_where: str = None) -> list[int]:
        # TODO: return dict[int: str] profile_ids with reason why the profile is choosen
        """Get a list of profile ids for the given criteria_dict
        :param criteria_dict: dictionary of criteria, each of which includes:
            min_age, max_age, gender_list_id, group_list_id
        :param append_where: additional where clause to append to the query (add parentheses if needed)"""
        function_name = "get_profiles_satisfying_criteria"
        if function_name not in cache:
            cache[function_name] = {}
        cache_key = str(criteria_dict)
        if cache_key in cache[function_name]:
            profiles_ids = cache[function_name][cache_key]
            return profiles_ids

        where = self.get_where_by_criteria_dict(criteria_dict)
        if append_where:
            # assert all(recipient.get_profile_id() is not None for recipient in recipients)
            # profile_ids_str = ",".join(str(recipient.get_profile_id()) for recipient in recipients)
            # where += f" AND user.profile_id IN ({profile_ids_str})"
            where = f"({where}) {append_where}"
        # Old:             SELECT DISTINCT user_id,
        #                             person_id,
        #                             user.main_email_address,
        #                             user.profile_id AS profile_id,
        #                             profile_phone_full_number_normalized,
        #                             profile_preferred_lang_code
        query_for_potentials_recipients = """
            SELECT DISTINCT profile.profile_id AS profile_id
            FROM profile.profile_view AS profile """
        if criteria_dict.get("min_age") or criteria_dict.get("max_age"):
            self.logger.info(
                "the criteria_dict has min_age or max_age, so we need to join with person.birthday_date. criteria_id:{cr}")
            self.logger.info(
                f"min_age: {criteria_dict.get('min_age')}, max_age: {criteria_dict.get('max_age')}")

            query_for_potentials_recipients += """
            LEFT JOIN person_profile.person_profile_view AS person_profile
                ON person_profile.profile_id = profile.profile_id
            LEFT JOIN person.person_general_view AS person
                ON `person.person_id` = profile.main_person_id
            """

        if criteria_dict.get("group_id") or criteria_dict.get("group_list_id"):
            self.logger.info(
                "the criteria_dict has group_id or group_list_id, so we need to join with group_profile.group_profile_view")
            self.logger.info(
                f"group_id: {criteria_dict.get('group_id')}, group_list_id: {criteria_dict.get('group_list_id')}")

            query_for_potentials_recipients += """
                  LEFT JOIN group_profile.group_profile_view AS group_profile
                     on group_profile.profile_id = profile.profile_id"""

        # LEFT JOIN location_profile.xxx
        if (criteria_dict.get("location_id") or criteria_dict.get("location_list_id")
                or criteria_dict.get("country_id") or criteria_dict.get("country_list_id")
                or criteria_dict.get("county_id") or criteria_dict.get("county_list_id")
                or criteria_dict.get("state_id") or criteria_dict.get("state_list_id")
                or criteria_dict.get("city_id") or criteria_dict.get("city_list_id")

                or criteria_dict.get("label_id") or criteria_dict.get("label_list_id")):
            self.logger.info(
                "the criteria_dict has location information, so we need to join with location_profile")
            self.logger.info(
                f"location_id: {criteria_dict.get('location_id')}, location_list_id: {criteria_dict.get('location_list_id')}, "
                f"country_id: {criteria_dict.get('country_id')}, country_list_id: {criteria_dict.get('country_list_id')}, "
                f"county_id: {criteria_dict.get('county_id')}, county_list_id: {criteria_dict.get('county_list_id')}, "
                f"state_id: {criteria_dict.get('state_id')}, state_list_id: {criteria_dict.get('state_list_id')}, "
                f"city_id: {criteria_dict.get('city_id')}, city_list_id: {criteria_dict.get('city_list_id')}, "
                f"label_id: {criteria_dict.get('label_id')}, label_list_id: {criteria_dict.get('label_list_id')}")

            if criteria_dict.get("label_id") or criteria_dict.get("label_list_id"):
                view_name = "location_profile_label_general_view"
            else:
                view_name = "location_profile_general_view"
            query_for_potentials_recipients += f"""
                  LEFT JOIN location_profile.{view_name} AS location_profile
                     on location_profile.profile_id = profile.profile_id"""

        query_for_potentials_recipients += f" WHERE {where}"
        # columns = ("user_id, person_id, user.main_email_address, profile_id,"
        #            "profile_phone_full_number_normalized, profile_preferred_lang_code")
        self.cursor.execute(query_for_potentials_recipients)
        profiles_ids = [row[0] for row in self.cursor.fetchall()]
        cache[function_name][cache_key] = profiles_ids
        return profiles_ids

    @lru_cache
    # list -> Tuple for performance?
    # TODO Shall we remove "criteria" from the method name?
    def get_profile_ids_per_criteria_and_criteria_set_id(
            self, criteria_set_ids: Tuple[int, ...], append_where: str = None) \
            -> Tuple[dict[int, list[int]], dict[int, list[int]]]:
        profile_ids_per_criteria_id = {}
        profile_ids_per_criteria_set_id = {}
        criterias_per_criteria_set_id = self.get_criterias_per_criteria_set_id(
            criteria_set_ids)
        for criteria_set_id, criterias in criterias_per_criteria_set_id.items():
            for criteria in criterias:
                self.logger.info(
                    object={"criteria_set_id": criteria_set_id, "criteria_id": criteria["criteria_id"]})
                criterion = Criterion(criteria_id=criteria["criteria_id"],
                                      entity_type_id=criteria["entity_type_id"],
                                      where_sql="`criteria.criteria_id`=" + str(criteria["criteria_id"]))
                entity_dict = self.get_entity_criteria_by_criterion(
                    criterion=criterion)
                entity_dict["criteria_id"] = criteria["criteria_id"]
                profiles_ids = self.get_profiles_ids_satisfying_criteria(
                    criteria_dict=entity_dict, append_where=append_where)
                profile_ids_per_criteria_id[criteria["criteria_id"]
                                            ] = profiles_ids
                profile_ids_per_criteria_set_id[criteria_set_id] = profiles_ids
        return profile_ids_per_criteria_id, profile_ids_per_criteria_set_id

    def is_match(self, *, criteria_set_ids: Tuple[int, ...] | int, profile_id: int) -> bool:
        """Check if the profile matches the criteria_set_ids"""
        if isinstance(criteria_set_ids, int):
            criteria_set_ids = (criteria_set_ids,)
        elif isinstance(criteria_set_ids, list):
            criteria_set_ids = tuple(criteria_set_ids)

        _, profile_ids_per_criteria_set_id = self.get_profile_ids_per_criteria_and_criteria_set_id(
            criteria_set_ids)
        result = profile_id in any(
            profile_ids for profile_ids in profile_ids_per_criteria_set_id.values())
        return result  # TODO: test

    # OurOpenSearch integration methods

    def initialize_opensearch(self, buffer_size: int = 300) -> OurOpenSearch:

        # self.logger.info(object="Initializing OurOpenSearch client")
        opensearch_client = OurOpenSearch(buffer_size=buffer_size)
        return opensearch_client

    def get_criteria_index_name(self, is_test_data: bool = False) -> str:

        index_prefix = "test_" if is_test_data else ""
        return f"{index_prefix}criteria_index"

    def create_criterion_index(self, opensearch_client: OurOpenSearch = None):

        if opensearch_client is None:
            opensearch_client = self.initialize_opensearch()

        index_name = self.get_criteria_index_name(
            is_test_data=self.is_test_data)

        is_exists = opensearch_client.client.indices.exists(index=index_name)

        if not is_exists:
            try:
                criteria_table_columns = table_columns["criteria_table"]

                criteria_body = {
                    "mappings": {
                        "properties": {
                            column: {"type": "keyword"} for column in criteria_table_columns
                        }
                    }
                }

                self.logger.info(object={
                    "message": f"Creating index {index_name} in OurOpenSearch",
                    "criteria_body": criteria_body
                })
                print(f"Index body type: {type(criteria_body)}")
                print(f"Index body content: {criteria_body}")

                opensearch_client.client.indices.create(
                    index=index_name,
                    body=criteria_body,
                )
            except Exception as e:
                self.logger.error(object={
                    "message": f"Error creating index {index_name} in OurOpenSearch",
                    "error": str(e)
                })
                raise Exception(f"Error creating index {index_name}: {str(e)}")

    def sync_criteria_to_opensearch(self, where: str, limit: int = None, opensearch_client: OurOpenSearch = None, is_test_data: bool = None) -> dict:
        if is_test_data is None:
            is_test_data = self.is_test_data

        if limit is None:
            limit = 100

        if opensearch_client is None:
            opensearch_client = self.initialize_opensearch()

        index_name = self.get_criteria_index_name(is_test_data=is_test_data)
        self.create_criterion_index(opensearch_client=opensearch_client)

        respones_dict = self.foreach(
            where=where,
            limit=limit,
            function=opensearch_client.insert,
            id_column_name="criteria_id",
            index_name=index_name,
        )

        return respones_dict

    def search_criteria(self, query: dict, opensearch_client: OurOpenSearch = None, is_test_data: bool = False) -> dict:

        if opensearch_client is None:
            opensearch_client = self.initialize_opensearch()

        index_name = self.get_criteria_index_name(is_test_data=is_test_data)

        try:
            search_results = opensearch_client.search(
                index=index_name,
                body=query
            )
            return search_results
        except Exception as e:
            self.logger.error(
                object={"message": "Error searching criteria in OurOpenSearch", "error": str(e)})
            return {"error": str(e)}

    def query_criteria_by_metadata(self, metadata: dict, opensearch_client: OurOpenSearch = None,
                                   is_test_data: bool = False) -> dict:

        if opensearch_client is None:
            opensearch_client = self.initialize_opensearch()

        must_clauses = []
        for field, value in metadata.items():
            if isinstance(value, (list, tuple)):
                # For lists, use terms query
                must_clauses.append({"terms": {field: value}})
            else:
                # For single values, use term query
                must_clauses.append({"term": {field: value}})

        query = {
            "query": {
                "bool": {
                    "must": must_clauses
                }
            }
        }

        return self.search_criteria(query, opensearch_client, is_test_data)
