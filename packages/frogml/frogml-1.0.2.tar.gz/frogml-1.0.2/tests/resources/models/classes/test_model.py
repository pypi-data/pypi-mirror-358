from typing_extensions import override, Self

from frogml import FrogMlModel


class ModelClassResource(FrogMlModel):
    def __init__(self: Self):
        super().__init__()
        self.__model = None

    @property
    def model(self):
        return self.__model

    @override
    def build(self: Self):
        pass

    @override
    def predict(self: Self, df):
        pass
