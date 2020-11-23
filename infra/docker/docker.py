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
          precmd_run = [],
          command=[]
        ):
        self.base_image = base_image
        self.path=str(path)
        self.files = files
        self.prefix=prefix
        self.precmd_run=precmd_run
        self.command=command
        if self.prefix is not None:
            self.dockerfile = self.prefix+".Dockerfile"
        else:
            self.dockerfile = "Dockerfile"

        self.infra_path = self.path + "/__infra__"
        pathlib.Path(self.infra_path).mkdir(parents=True, exist_ok=True)
        self.dockerfile_path=self.infra_path+"/"+self.dockerfile

        self.content = []
        self.content += ["FROM "+base_image]
        # self.content += base_builder.content
        for f in self.files:
            self.content += ["COPY "+f+" ."]

        for f in self.precmd_run:
            self.content += ["RUN "+f]

        self.content += ["CMD "+self.command]
        with open(self.dockerfile_path, "w") as f:
            f.writelines("\n".join(self.content))


class ImageBuilder(DockerFileBuilder):
    def __init__(
          self,
          name,
          create=True,
          skip_push=True,
          overwrite=True,
          prefix="",
          base_image=None,
          base_builder=None,
          path=os.path.dirname(os.path.abspath(__file__)),
          files=[],
          precmd_run=[],
          command=[]
        ):
        self.skip_push = skip_push
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
          precmd_run=precmd_run,
          command=command
        )
        self.image = docker.Image(
            name,
            image_name=name,
            build=docker.DockerBuild(
                dockerfile=self.dockerfile_path,
                context=self.path,
            ),
            skip_push=self.skip_push,
        ) # TODO skp

