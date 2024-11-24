from typing import Dict, List, Any


def get_first_ten_records(data: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
    """
    Returns the first ten records for each key in the dictionary.

    Args:
        data (Dict[str, List[Any]]): The data dictionary where each key has a list of records.

    Returns:
        Dict[str, List[Any]]: A dictionary with the same keys but only containing the first ten records.
    """
    return {key: values[:10] for key, values in data.items()}
