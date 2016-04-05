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
    } else if (type === 'Ranking (JP)') {
      if (!obj1.JpRanking && !obj2.JpRanking) { //if both are not set, they are equal
        return 0
      } else if (!obj1.JpRanking && obj2.JpRanking) { //take one being set as higher than the other
        return 1
      } else if (obj1.JpRanking && !obj2.JpRanking) { //take one being set as higher than the other
        return -1
      } else { //both are set, do a comparison
        //we calculate a value based the letter and modifier (+), and use that for comparison
        //each letter grade is worth 2, and a + is worth 1

        obj1OrderValue = 0;
        if (obj1.JpRanking.indexOf('C') != -1) {
          obj1OrderValue = 2;
        } else if (obj1.JpRanking.indexOf('B') != -1) {
          obj1OrderValue = 4;
        } else if (obj1.JpRanking.indexOf('A') != -1) {
          obj1OrderValue = 6;
        } else if (obj1.JpRanking.indexOf('SS') != -1) {
          obj1OrderValue = 10;
        } else if (obj1.JpRanking.indexOf('S') != -1) { //note S is after SS, due to the 'contains' check
          obj1OrderValue = 8;
        }

        if (obj1.JpRanking.indexOf('+') != -1) {
          obj1OrderValue++
        }

        obj2OrderValue = 0;
        if (obj2.JpRanking.indexOf('C') != -1) {
          obj2OrderValue = 2;
        } else if (obj2.JpRanking.indexOf('B') != -1) {
          obj2OrderValue = 4;
        } else if (obj2.JpRanking.indexOf('A') != -1) {
          obj2OrderValue = 6;
        } else if (obj2.JpRanking.indexOf('SS') != -1) {
          obj2OrderValue = 10;
        } else if (obj2.JpRanking.indexOf('S') != -1) { //note S is after SS, due to the 'contains' check
          obj2OrderValue = 8;
        }

        if (obj2.JpRanking.indexOf('+') != -1) {
          obj2OrderValue++
        }

        if (obj1OrderValue == obj2OrderValue) {
          return 0;
        } else if (obj1OrderValue > obj2OrderValue) { //note we take a reverse stance on ordering, due to a larger value being a higher rated unit
          return -1;
        } else {
          return 1;
        }
      }



      return 1 //we default to greater if it has no rank (note: greater means further down the list)
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
