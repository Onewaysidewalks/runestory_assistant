angular.module("app-utils", []).filter("customSorter", function() {

  function compare(obj1, obj2, type) {
    if (type === 'Rarity') {
      //first by rarity, then by Name
      obj1Order = rarityOrder(obj1)
      obj2Order = rarityOrder(obj2)

      if (obj1Order < obj2Order) {
        return 1
      } else if (obj1Order > obj2Order) {
        return -1
      } else {
        return compare(obj1, obj2, 'Name')
      }
    } else if (type === 'Name') {
      return obj1.Name > obj2.Name ? 1 : -1;
    }

    return 1
  }

  function rarityOrder(obj) {
    switch(obj.Rarity) {
      case '5':
        return 5;
      case '4':
        return 4;
      case '3':
        return 3;
      case '2':
        return 2;
      case '1':
        return 1;
    }

    return 0;
  }

  return function(items, field) {
    var filtered = [];
    angular.forEach(items, function(item) {
      filtered.push(item);
    });
    filtered.sort(function (a, b) {
      return compare(a, b, field);
    });
    return filtered;
  };
})

.filter('characterFilter', function() { //filter based on type, name, etc.
  return function(characterList, type, searchText) {
    retList = []
    for (characterIndex in characterList) {

      character = characterList[characterIndex]
      typeMatch = true;
      nameMatch = true;

      if (typeMatch && type != 'All' && type != character.Type) {
        typeMatch = false;
      }

      if (nameMatch
        && character.Name
        && character.Name.toLowerCase().indexOf(searchText.toLowerCase()) < 0) {
        nameMatch = false;
      }

      if (typeMatch && nameMatch) {
        retList.push(character)
      }
    }

    return retList
  }
});
