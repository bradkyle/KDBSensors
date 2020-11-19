
import pulumi
import pulumi_docker as docker

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


class ImageBuilder(object):
    def __init__(self, base_image):
        self.dockerfile = DockerFileBuilder(

        )

        self.image = Image(
            "sensor-image",
            image_name="",
            build=DockerBuild(
                target="dependencies",
                context=self.dockerfile.path,
            ),
            skip_push=True,
        ) # TODO skp

