
class DockerFileBuilder():
    def __init__(
          self,
          name,
          base_image=None,
          base_builder=None,
          path=pathlib.Path().absolute(),
          files=[],
        ):
        self.base_image = base_image
        self.path=path
        self.files = []

    def build(self):
        pass

    def clean(self):
        pass

