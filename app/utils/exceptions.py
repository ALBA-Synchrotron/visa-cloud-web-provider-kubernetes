class APIConfigError(Exception):
    pass


class VISAK8sInstallError(Exception):
    pass


class KubernetesError(Exception):
    pass


class KubernetesNotFoundError(KubernetesError):

    def __init__(self, obj_name: str, obj_type_name: str):
        self.obj_name = obj_name
        self.obj_type_name = obj_type_name


class KubernetesNotFoundInInstanceError(KubernetesNotFoundError):
    def __init__(self, obj_name: str, obj_type_name: str, obj_recipient_name: str, obj_type_recipient_name: str):
        super().__init__(obj_name, obj_type_name)
        self.obj_type_recipient_name = obj_type_recipient_name
        self.obj_recipient_name = obj_recipient_name


class InvalidPayloadFormat(Exception):
    pass


class CloudProviderResourceQuotaExceeded(Exception):
    pass
