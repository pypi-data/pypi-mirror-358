class IAdditionalAttributes:

    def set_additional_attributes(self, attributes):
        raise NotImplemented

    def get_additional_attributes(self):
        raise NotImplemented

    def get_additional_attribute(self, attribute, default=None):
        raise NotImplemented
