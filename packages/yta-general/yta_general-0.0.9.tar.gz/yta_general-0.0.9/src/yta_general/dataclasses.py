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
from yta_constants.file import FileType, FileParsingMethod
from yta_programming.decorators.requires_dependency import requires_dependency
from yta_validation import PythonValidator
from dataclasses import dataclass
from typing import Union

import io


@dataclass
class FileReturned:
    """
    Dataclass to use when we are returning a file
    from a method, so we know more information 
    about the file that we are returning, or even
    being able to return the file content directly
    instead.

    A file that has been obtained from a platform,
    that can be downloaded as a file or only as its
    content. The 'filename' property indicates the
    filename of the original file that has been
    downloaded to be read, and the 'content' 
    property has the content, in bytes, of the file
    (that has not been downloaded). The 'type' and
    the 'parsing_method' are to indicate how we 
    should parse the content of that file.
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
    
    @property
    def has_parsing_method(
        self
    ) -> bool:
        """
        Indicate if there is a parsing method so
        the content or filename can be parsed by
        using that method.
        """
        return self.parsing_method is not None
    
    @requires_dependency('yta_file', 'yta_general', 'yta_file')
    @requires_dependency('yta_temp', 'yta_general', 'yta_temp')
    @requires_dependency('moviepy', 'yta_general', 'moviepy')
    @requires_dependency('PIL', 'yta_general', 'pillow')
    @requires_dependency('cv2', 'yta_general', 'opencv-python')
    @requires_dependency('pydub', 'yta_general', 'pydub')
    @requires_dependency('numpy', 'yta_general', 'numpy')
    @property
    def content_parsed(
        self
    ) -> any:
        """
        The file content parsed according to its type. This
        method requires a lot of libraries to be able to
        parse the content properly.
        """
        # TODO: Maybe be more strict with the types
        from yta_file.handler import FileHandler
        from yta_temp import Temp
        from moviepy import VideoFileClip, AudioFileClip
        from PIL import Image
        from pydub import AudioSegment
        import numpy as np
        import cv2

        # This was in the previous FileReturn class, because
        # sometimes you don't need to parse the content, so
        # I keep the code here (commented) just in case
        # if not PythonValidator.is_instance(self.file, [bytes, bytearray, io.BytesIO]):
        #     return self.file

        # TODO: If 'parsing_method' is set we need to use
        # it instead of 'type' because it is more precise
        # indicating the library we should use to parse
        # the content
        if (
            self.is_content and
            self.is_parsed
        ):
            return self.content
        
        # TODO: This uses a lot of libraries
        if self.parsing_method == FileParsingMethod.UNPARSEABLE:
            raise Exception('The content is unparseable.')
        elif self.parsing_method in [
            FileParsingMethod.IO_SUBTITLES,
            FileParsingMethod.IO_TEXT
        ]:
            return (
                io.BytesIO(self.content).getvalue().decode('utf-8')
                if self.is_content else
                io.BytesIO(self.filename).getvalue().decode('utf-8')
            )
        elif self.parsing_method == FileParsingMethod.MOVIEPY_VIDEO:
            return (
                VideoFileClip(FileHandler.write_binary(Temp.get_filename('video.mp4'), self.content))
                if self.is_content else
                VideoFileClip(self.filename)
            )
        elif self.parsing_method == FileParsingMethod.MOVIEPY_AUDIO:
            return (
                AudioFileClip(FileHandler.write_binary(Temp.get_filename('video.mp4'), self.content))
                if self.is_content else
                AudioFileClip(self.filename)
            )
        elif self.parsing_method == FileParsingMethod.PILLOW_IMAGE:
            return (
                Image.open(io.BytesIO(self.content))
                if self.is_filename else
                Image.open(self.filename)
            )
        elif self.parsing_method == FileParsingMethod.OPENCV_IMAGE:
            return (
                cv2.imdecode(np.frombuffer(self.content, np.uint8), cv2.IMREAD_COLOR)
                if self.is_content else
                cv2.imread(self.filename)
            )
        elif self.parsing_method == FileParsingMethod.PYDUB_AUDIO:
            return (
                AudioSegment.from_file(io.BytesIO(self.content))
                if self.is_filename else
                AudioSegment.from_file(self.filename)
            )
        else:
            # No 'parsing_method'
            return (
                # TODO: This method needs a lot of libraries
                FileHandler.parse_file_content(self.content, self.type)
                if self.is_content else
                FileHandler.parse_filename(self.filename)
                if self.is_filename else
                None # TODO: I think this cannot happen and maybe
                # I should raise an Exception
            )

    def __init__(
        self,
        content: Union[bytes, bytearray, io.BytesIO, any, None],
        filename: Union[str, None],
        output_filename: Union[str, None],
        # TODO: Maybe transform this to a general 'type'
        type: Union[FileType, None],
        is_parsed: bool,
        parsing_method: Union[FileParsingMethod, None],
        extra_args: Union[any, None]
    ):
        # TODO: Validate params as non-mandatory
        self.autodetected_type: Union[FileType, None] = (
            FileType.get_type_from_filename(filename)
            if filename is not None else
            FileType.get_type_from_filename(output_filename)
            if output_filename is not None else
            None
        )
        """
        Type that is autodetected from the 'filename' or
        'output_filename' if existing.
        """
        self.content: Union[bytes, bytearray, io.BytesIO, any, None] = content
        """
        The content of the file obtained by our system,
        that can be raw or already parsed.
        """
        self.filename: Union[str, None] = filename
        """
        The filename of the file that has been detected.
        """
        self.output_filename: Union[str, None] = output_filename
        """
        The filename that has to be used when writing
        the file if needed.
        """
        self.type: Union[FileType, None] = type
        """
        The type of the file.
        """
        self.is_parsed: bool = (
            is_parsed
            if PythonValidator.is_boolean(is_parsed) else
            False
        )
        """
        The indicator of the content, to know if it
        has been already parsed or not. If parsed,
        the 'parsing_method' associated will determine
        which specific type of file it is.
        """
        self.parsing_method: Union[FileParsingMethod, None] = parsing_method
        """
        The indicator of which method should we use to
        parse the file content, that describes also the
        library we need and how to do it through the
        FileParsingMethod enum elements we have.
        """
        self.extra_args: any = extra_args
        """
        Any extra arg we should use when parsing the file
        using the 'parsing_method' attribute.
        """

        if (
            (
                not self.is_content and
                not self.is_filename
            ) or
            (
                not self.has_type and
                not self.autodetected_type and
                not self.has_parsing_method
            )
        ):
            raise Exception('A file must have "content" or a "filename", and also a way of parsing the content.')

    @requires_dependency('yta_file', 'yta_general', 'yta_file')
    def write(
        self,
        filename: str
    ):
        """
        Write the content to a local file with the 
        'filename' provided.
        """
        from yta_file.handler import FileHandler
        # TODO: What if no extension (?)
        # TODO: What if extension is different than the
        # real type (?)
        # TODO: What if 'is_filename' and the destination
        # is the same than the origin (?)
        return (
            FileHandler.write_binary(filename, self.content)
            if self.is_content else
            FileHandler.copy_file(self.filename, filename)
        )

"""
TODO: The 'parsing_method' has a method to obtain
the 'FileType' associated, but we also have a 
'type' attribute that determines this manually, so
there is a conflict.
"""

        