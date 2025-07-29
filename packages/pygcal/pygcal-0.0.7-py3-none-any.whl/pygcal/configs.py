"""
All configurations
"""
from pytconf import Config, ParamCreator


class ConfigPagination(Config):
    """ Pagination parameters """
    page_size = ParamCreator.create_int(
        help_string="What page size to use for pagination (max is 50)",
        # if you set it for more than 50 it will be 50...
        default=50,
    )
