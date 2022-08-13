__app_name__ = "booker"
__version__ = "0.1.0"

(
    SUCCESS,
    CONFIG_DIRECTORY_ERROR,
    CONFIG_FILE_ERROR,
    DB_READ_ERROR,
    DB_WRITE_ERROR,
    JSON_ERROR,
    ID_ERROR,
) = range(7)


ERRORS = {
    CONFIG_DIRECTORY_ERROR: "config directory error",
    CONFIG_FILE_ERROR: "config file error",
    DB_READ_ERROR: "error reading from database",
    DB_WRITE_ERROR: "error writing to database",
    ID_ERROR: "error with id supplied",
}
