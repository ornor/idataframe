from typing import List

__all__ = ['list_remove_duplicates']


def list_remove_duplicates(original:List[str]) -> List[str]:
    """
    Removes duplicate values from list.

    In contrast to 'list(set(original))' the order will be remained. The first occurance will be kept.
    """
    unique_list = []
    for el in original:
        if el not in unique_list:
            unique_list.append(el)
    return unique_list
