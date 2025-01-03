from typing import Dict, List, Any, Union



def get_first_ten_records(data: Dict[str, List[Any]]) -> Dict[str, Union[List[Any], str]]:
    """
    Returns the first ten records for each key in the dictionary.

    Args:
        data (Dict[str, List[Any]]): The data dictionary where each key has a list of records.

    Returns:
        Dict[str, List[Any]]: A dictionary with the same keys but only containing the first ten records.
    """
    if not data:
        return {'results': "No records found."}
    return {key: values[:10] for key, values in data.items()}
