import os
import pathlib
import pulumi
import pulumi_docker as docker

class DockerFileBuilder():
    def __init__(
          self,
          name,
          create=True,
          overwrite=True,
          prefix="",
          base_image=None,
          base_builder=None,
          path=pathlib.Path().absolute(),
          files=[],
          command=[]
        ):
        self.base_image = base_image
        self.path=str(path)
        self.files = files
        self.prefix=prefix
        self.command=command
        if self.prefix is not None:
            self.dockerfile = self.prefix+".Dockerfile"
        else:
            self.dockerfile = "Dockerfile"
        self.dockerfile_path=self.path+"/"+self.dockerfile

        self.content = []
        self.content += ["FROM "+base_image]
        # self.content += base_builder.content
        for f in self.files:
            self.content += ["COPY "+f+" ."]

        self.content += ["CMD "+self.command]
        with open(self.dockerfile_path, "w") as f:
            f.writelines("\n".join(self.content))


class ImageBuilder(DockerFileBuilder):
    def __init__(
          self,
          name,
          create=True,
          overwrite=True,
          prefix="",
          base_image=None,
          base_builder=None,
          path=os.path.dirname(os.path.abspath(__file__)),
          files=[],
          command=[]
        ):
        DockerFileBuilder.__init__(
          self,
          name=name,
          create=create,
          overwrite=overwrite,
          base_image=base_image,
          base_builder=base_builder,
          path=path,
          files=files,
          prefix=prefix,
          command=command
        )
        self.image = docker.Image(
            name,
            image_name=name,
            build=docker.DockerBuild(
                dockerfile=self.dockerfile_path,
                context=self.path,
            ),
            skip_push=True,
        ) # TODO skp

