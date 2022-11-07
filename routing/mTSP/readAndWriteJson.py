import json as js

# Reads a Json file, and returns a dictionary corresponding to the data in the Json file
def readJsonFileToDictionary(fileName: str) -> dict:
    with open(fileName) as d:
        dictionary = js.load(d)
    return dictionary


# Returns a list of all the keys in a dictionary
def extractKeyNames(dictionary: dict) -> list:
    return list(dictionary.keys())


# Saves a dictionary to a Json file
def saveDictToJsonFile(dictionary: dict, fileName: str):
    with open(fileName, "w") as outfile:
        js.dump(dictionary, outfile)


def main():
    print("Hollow world!")


# If imported in another file, main is not run
if __name__ == '__main__':
    main()