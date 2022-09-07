import json as js


def readJsonFileToDictionary(fileName: str) -> dict:
    with open(fileName) as d:
        dictionary = js.load(d)
    return dictionary


def extractKeyNames(dictionary: dict) -> list:
    return list(dictionary.keys())


def saveDictToJsonFile(dictionary: dict, fileName: str):
    with open(fileName, "w") as outfile:
        js.dump(dictionary, outfile)


def main():
    print("Hollow world!")


# If imported in another file, main is not run
if __name__ == '__main__':
    main()
