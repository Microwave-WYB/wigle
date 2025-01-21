import time

from wigle import BluetoothSearch

query = BluetoothSearch(namelike="QT %", resultsPerPage=5)
page = 0
while page < 2:
    result = query.result_or_status()
    while result == 429:
        time.sleep(3600)
        result = query.result_or_status()
    match result:
        case int():
            print(f"Error: {result}")
        case _:
            print(result)
            query.searchAfter = result.searchAfter
            page += 1
