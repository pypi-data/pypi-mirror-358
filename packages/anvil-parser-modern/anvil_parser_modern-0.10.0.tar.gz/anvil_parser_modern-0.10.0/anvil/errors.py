class OutOfBoundsCoordinates(ValueError):
    """Exception used for when coordinates are out of bounds"""

class ChunkNotFound(Exception):
    """Exception used for when a chunk was not found"""

class EmptySectionAlreadyExists(Exception):
    """
    Exception used for when trying to add an `EmptySection` to an `EmptyChunk`
    and the chunk already has a section with the same Y
    """

class EmptyRegionFile(Exception):
    """
    Exception used when trying to read a region file which has no data
    """

class GZipChunkData(Exception):
    """Exception used when trying to get chunk data compressed in gzip"""

class CorruptedData(Exception):
    """
    Exception used when trying to read corrupted data
    """
class InvalidFileType(Exception):
    """
    Exception raised when file parameter is not a valid file path or file-like object
    """
