"""
When we handle files with our system we obtain them
in different formats. Sometimes we get them from urls
so they are just a bytes array, and sometimes we 
obtain an image, for example, that has been previously
loaded with its corresponding library.

We try to treat all those files in the same way so we
have created this class to interact with them and make
easier the way we handle them.
"""
from yta_constants.file import FileType
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_validation import PythonValidator
from dataclasses import dataclass
from typing import Union

import io


# TODO: This class has to disappear because it needs
# a lot of dependencies we don't want to have. We
# have created the new 'FileReturned' that is able
# to parse the content only with the optional 
# dependency, which is better.
@dataclass
class FileReturn:
    """
    This dataclass has been created to handle a file
    that has been created or downloaded, so we are
    able to return the file itself and also the 
    filename in the same return.
    """

    # TODO: Set valid types
    file: Union[bytes, bytearray, io.BytesIO, any]
    """
    The file content as raw as it was obtained by
    our system, that could be binary or maybe an
    actually parsed file.
    """
    type: Union[FileType, None]
    """
    The type of the obtained file.
    """
    filename: str
    """
    The filename of the obtained file.
    """

    @property
    def file_type(self) -> Union[FileType, None]:
        """
        Get the FileType associated to the
        'output_filename' extension if existing and
        valid.
        """
        return FileType.get_type_from_filename(self.filename)

    @property
    def file_converted(self):
        """
        The file parsed according to its type. This
        can be the same as 'file' attribute if it
        was obtained in a converted format.
        """
        # TODO: Deprecated, but as I created the new 
        # FileReturned class I keep it as it is
        from yta_general_utils.file.reader import FileReader

        # Sometimes the file that has been set is
        # already converted, so we just send it
        # as it is
        if not PythonValidator.is_instance(self.file, [bytes, bytearray, io.BytesIO]):
            return self.file
        
        if self.type is None:
            # TODO: What about this (?)
            import warnings
            warnings.warn('The type is None so we do not actually know the file type. Returning it raw.')
            return self.file

        return FileReader.parse_file_content(self.file, self.type)

    def __init__(
        self,
        file: Union[bytes, bytearray, io.BytesIO, any],
        type: Union[FileType, None],
        filename: str
    ):
        if type is not None:
            type = FileType.to_enum(type)

        self.file = file
        self.type = type
        self.filename = filename

@dataclass
class FileReturned:
    """
    Dataclass to use when we are returning a file
    from a method, so we know more information 
    about the file that we are returning, or even
    being able to return the file content directly
    instead.
    """

    @property
    def is_content(
        self
    ) -> bool:
        """
        Indicate if the instance is holding the raw
        content of the file instead of a filename.
        """
        return self.content is not None
    
    @property
    def is_filename(
        self
    ) -> bool:
        """
        Indicate if the instance is holding the filename
        of a file and must be read to obtain the file
        content.
        """
        return self.filename is not None
    
    @property
    def has_type(
        self
    ) -> bool:
        """
        Indicate if there is a type set so the content
        or filename can be parsed using that type.
        """
        return self.type is not None
    
    @requires_dependency('yta_file', 'yta_general_utils', 'yta_file')
    @property
    def content_parsed(
        self
    ) -> any:
        """
        The file content parsed according to its type.
        """
        # TODO: Maybe be more strict with the types
        from yta_file.handler import FileHandler

        # TODO: Maybe this should be raised within
        # the '__init__.py' method
        if (
            (
                not self.is_content and
                not self.is_filename
            ) or
            (
                # TODO: Maybe this is possible when the content
                # is actually bytes or similar, but by now I
                # keep it as an exception
                self.is_content and
                not self.has_type
            ) or
            (
                # TODO: In this case I can detect the type from
                # the extension maybe
                self.is_filename and
                not self.has_type
            )
        ):
            raise Exception('The content is not parseable.')

        # This was in the previous FileReturn class, because
        # sometimes you don't need to parse the content, so
        # I keep the code here (commented) just in case
        # if not PythonValidator.is_instance(self.file, [bytes, bytearray, io.BytesIO]):
        #     return self.file
        
        return (
            FileHandler.parse_file_content(self.content, self.type)
            if self.is_content else
            FileHandler.parse_filename(self.filename)
            if self.is_filename else
            None # TODO: I think this cannot happend and maybe
            # I should raise an Exception
        )
    
    def __init__(
        self,
        # TODO: Maybe transform this to a general 'type'
        content: Union[bytes, bytearray, io.BytesIO, any, None],
        filename: Union[str, None],
        type: Union[FileType, None]
    ):
        self.autodetected_type: Union[FileType, None] = (
            None
            if filename is None else
            FileType.get_type_from_filename(filename)
        )
        """
        Type that is autodetected from the filename if
        existing.
        """
        self.content: Union[bytes, bytearray, io.BytesIO, any, None] = content
        """
        The file content as raw as it was obtained by
        our system, that could be binary or maybe an
        actually parsed file.
        """
        self.filename: Union[str, None] = filename
        """
        The filename of the file.
        """
        self.type: Union[FileType, None] = type
        """
        The type of the file.
        """

        if (
            (
                not self.is_content and
                not self.is_filename
            ) or
            (
                # TODO: Maybe this is possible when the content
                # is actually bytes or similar, but by now I
                # keep it as an exception
                self.is_content and
                not self.has_type
            ) or
            (
                # TODO: In this case I can detect the type from
                # the extension maybe
                self.is_filename and
                not self.has_type and
                not self.autodetected_type
            )
        ):
            # TODO: Improve this message please
            raise Exception('Sorry, this is not possible.')

        