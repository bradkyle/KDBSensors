
import os
import pathlib

class FileBuilder():
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


