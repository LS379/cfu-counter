class MethodAccessTrait(object):

    def __getattribute__(self, name):
        try:
            attr = object.__getattribute__(self, name)
        except AttributeError as exc:
            cls_name = self.__class__.__name__
            name = name.split('_{}'.format(cls_name))
            name = name[-1]

            for base in self.__class__.__mro__:
                mangled =  "_{}{}".format(base.__name__, name)

                try:
                    return object.__getattribute__(self, mangled)
                except:
                    continue

            raise

        return attr
