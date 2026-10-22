class BaseException(Exception):
    pass


class APIConfigError(BaseException):
    pass


class VISAK8sInstallError(BaseException):
    pass


class KubernetesError(BaseException):
    pass

class KubernetesNotFoundError(KubernetesError):

    def __init__(self, obj_name: str, obj_type_name: str):
        self.obj_name = obj_name
        self.obj_type_name = obj_type_name