from booker.control import ERROR


class CONFIG_DIRECTORY_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("something went wrong with the config directory.", cause)


class CONFIG_FILE_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("something went wrong with the config file.", cause)


class DB_READ_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("something went wrong when reading from database.", cause)


class DB_WRITE_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("something went wrong when writing to the database.", cause)


class ID_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("something went wrong with the id supplied.", cause)


class JSON_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("something is wrong with the supplied JSON file.", cause)


class VALIDATION_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("something is wrong with the supplied input.", cause)


class EXISTENCE_ERROR(ERROR):
    def __init__(self, cause: Exception):
        super().__init__("the resource you are looking for does not exist.", cause)