import json


class Criterion:
    """Criterion class"""

    # TODO Why you changed main_entity_type_id to entity_type_id? -
    #  We might have multiple entity_type_ids, one of them will probably be the main_entity_type_id
    # TODO Shall we change is_test_data default to false everywhere?
    def __init__(self, *, entity_type_id: int = None, name: str = None,
                 min_age: float = None,
                 max_age: float = None, group_list_id: int = None,
                 min_number_of_kids: int = None,
                 max_number_of_kids: int = None, min_kids_age: float = None,
                 max_kids_age: float = None,
                 gender_list_id: int = None, min_height: int = None,
                 max_height: int = None,
                 partner_experience_level: int = None, number_of_partners: int = None,
                 location_id: int = None, location_list_id: int = None,
                 coordinate: str = None,
                 radius: int = None, radius_measure: str = None,
                 radius_km: int = None,
                 job_group_list_id: int = None,
                 job_location_list_id: int = None,
                 vacancy_list_id: int = None,
                 workplace_profile_list_id: int = None,
                 start_date_type_id: int = None,
                 job_types_id: int = None,
                 visibility_id: int = None,
                 where_sql: str = None,
                 is_test_data: bool = None, internet_domain_id: int = None,
                 internet_domain_list_id: int = None,
                 organization_name: str = None,
                 group_id: int = None,
                 profile_list_id: int = None, international_code: int = None,
                 **kwargs) -> None:
        """Initialize a Criterion object."""
        for key, value in locals().items():
            if key not in ["self", "kwargs", "__class__"]:
                setattr(self, key, value)

        for key, value in kwargs.items():
            setattr(self, key, value)

    def to_dict(self) -> dict:
        """Convert the Criterion object to a dictionary."""
        to_dict_result = {k: v for k,
                          v in self.__dict__.items() if v is not None}
        return to_dict_result

    def __eq__(self, other: 'Criterion') -> bool:
        """Check if two Criterion objects are equal."""
        eq_result = self.to_dict() == other.to_dict()
        return eq_result

    # Performance
    def __hash__(self) -> int:
        hash_result = hash(tuple(sorted(self.to_dict().items())))
        return hash_result

    def to_json(self) -> str:
        """Convert the Criterion object to a JSON string."""
        return json.dumps(self.to_dict(), default=str)
