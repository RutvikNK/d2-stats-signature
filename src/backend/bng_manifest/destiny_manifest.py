import pickle, os
from dotenv import load_dotenv

from backend.bng_manifest.create_local_manifest import create_manifest, build_dict

class DestinyManifest:
    def __init__(self) -> None:
        self.hashes = {
            'DestinyAchievementDefinition': 'hash',
            'DestinyActivityGraphDefinition': 'hash',
            'DestinyActivityInteractableDefinition': 'hash',
            'DestinyActivityModeDefinition': 'hash',
            'DestinyActivityModifierDefinition': 'hash',
            'DestinyActivityDefinition': 'hash',
            'DestinyActivityTypeDefinition': 'hash',
            'DestinyClassDefinition': 'hash',
            'DestinyCollectibleDefinition': 'hash',
            'DestinyInventoryBucketDefinition': 'hash',
            'DestinyInventoryItemDefinition': 'hash',
            'DestinyProgressionDefinition': 'hash',
            'DestinyRaceDefinition': 'hash',
            'DestinyHistoricalStatsDefinition': 'statId',
            'DestinyStatDefinition': 'hash',
            'DestinySandboxPerkDefinition': 'hash',
            'DestinyDestinationDefinition': 'hash',
            'DestinyPlaceDefinition': 'hash',
            'DestinyStatGroupDefinition': 'hash',
            'DestinyFactionDefinition': 'hash'
        }

        self.define_manifest_data()

    def define_manifest_data(self):
        load_dotenv()

        MANIFEST_PATH = os.getenv('PATH_TO_MANIFEST')

        if os.path.isfile(f'{MANIFEST_PATH}manifest.content') == False:
            create_manifest()
            self.all_data = build_dict(self.hashes)
            with open(f'{MANIFEST_PATH}manifest.pickle', 'wb') as data:
                pickle.dump(self.all_data, data)
                print("'manifest.pickle' created!\nDONE!")
        else:
            print('Pickle Exists')

        with open(f'{MANIFEST_PATH}/manifest.pickle', 'rb') as data:
            self.all_data = pickle.load(data)

def unsigned_to_signed(num):
    max = 2 ** 31 - 1
    if num < max:
        return num
    else:
        return num - 2 ** 32

def main():
    manifest = DestinyManifest()

    hash = unsigned_to_signed(1363886209)
    ghorn = manifest.all_data["DestinyInventoryItemDefinition"][hash]

    print('Name: ' + ghorn['displayProperties']['name'])
    print('Type: ' + ghorn['itemTypeDisplayName'])
    print('Tier: ' + ghorn['itemTypeAndTierDisplayName'])
    print(ghorn['flavorText'])

if __name__ == "__main__":
    main()