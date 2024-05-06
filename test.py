import enum


class CustomIDs(enum.Enum):
    SHOWCHANNELS = "showchannels"
    ADDCHANNELS = "addchannels"
    REMOVECHANNELS = "removechannels"

    def __str__(self):
        return self.value

    @staticmethod
    def getID(value: str):
        return CustomIDs.__getitem__(value.upper())


def main():
    print(CustomIDs.getID("showchannels"))



if __name__ == "__main__":
    main()