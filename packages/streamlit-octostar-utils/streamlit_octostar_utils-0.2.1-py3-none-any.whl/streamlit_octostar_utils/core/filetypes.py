import mimetypes
import filetype


def add_filetypes():
    mimetypes.add_type("text/csv", ".csv")


def recognize_filetype(file, filename):
    from_name_guess, _ = mimetypes.guess_type(filename)
    from_file_guess = filetype.guess(file)
    if from_file_guess:
        from_file_guess = from_file_guess.mime
    recognized_filetype = None
    if not from_file_guess and not from_name_guess:
        recognized_filetype = "unknown"
    elif not (from_file_guess and from_name_guess):
        recognized_filetype = from_file_guess or from_name_guess
    elif from_file_guess.split("/", 1)[0] != from_name_guess.split("/", 1)[0]:
        recognized_filetype = from_file_guess
    elif from_file_guess.split("/", 1)[-1] != from_name_guess.split("/", 1)[-1]:
        recognized_filetype = from_name_guess
    else:
        recognized_filetype = from_name_guess
    return recognized_filetype
