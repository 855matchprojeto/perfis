import abc
from server.schemas.arquivo_schema import FileUploaderInput, FileUploaderOutput


class FileUploaderService:

    @abc.abstractmethod
    def upload(self, file_input: FileUploaderInput) -> FileUploaderOutput:
        """
        Interface para upload de arquivos
        """
        pass

