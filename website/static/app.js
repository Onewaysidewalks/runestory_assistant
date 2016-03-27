angular.module('app', ['ngAnimate', 'ui.bootstrap', 'app-utils']);

angular.module('app').controller('MainCtrl', function ($scope, $http, $uibModal, $log, $rootScope) {

  $rootScope.isLoaded = false

  $scope.$log = $log

  $scope.tabs = [
    {
      title: 'Home'
    },
    {
      title: 'Characters'
    },
    {
      title: 'Weapons'
    }
  ]

  //default selected tab
  $rootScope.selectedTab = $scope.tabs[0].title

  $scope.characterSortTypes = [
    { name: "Rarity"},
    { name: "Name"}
    // "Waifu" //figure out how to rate this!
  ]

  $scope.sortOnCharacter = function(sortType) {
      $scope.selectedCharacterSortName = sortType.name
  }

  $scope.selectedCharacterSortName = $scope.characterSortTypes[0].name //default sort name

  $scope.characterFilterTypes = [
    { name: "All", id: "0"},
    { name: "Hero", id: "1"},
    { name: "Defense", id: "2"},
    { name: "Support", id: "3"},
    { name: "Technical", id: "4"},
    { name: "Balance", id: "5"},
    { name: "Skill", id: "6"},
    { name: "Attacker", id: "7"}
  ]

  $scope.selectedCharacterFilterTypeName = $scope.characterFilterTypes[0].name //default character type filter (all/no filter)

  $scope.filterOnCharacterType = function(characterFilterType) {
    $scope.selectedCharacterFilterTypeName = characterFilterType.name
  }

  $scope.weaponSortTypes = [
    { name: "Name"}
  ]

  $scope.sortOnWeapon = function(sortType) {
      $scope.selectedWeaponSortName = sortType.name
  }

  $scope.selectedWeaponSortName = $scope.weaponSortTypes[0].name //default sort name

  $scope.characterSearchText = ''
  $scope.weaponSearchText = ''

  $scope.classFilterModel = {}
  $scope.classFilterModel['lancer'] = true
  $scope.classFilterModel['brawler'] = true
  $scope.classFilterModel['sniper'] = true
  $scope.classFilterModel['fencer'] = true
  $scope.classFilterModel['mage'] = true
  $scope.classFilterModel['warrior'] = true
  $scope.classFilterModel['dualsaber'] = true
  $scope.classFilterModel['dragonrider'] = true

  $scope.weaponFilterModel = {}
  $scope.weaponFilterModel['lancer'] = true
  $scope.weaponFilterModel['brawler'] = true
  $scope.weaponFilterModel['sniper'] = true
  $scope.weaponFilterModel['fencer'] = true
  $scope.weaponFilterModel['mage'] = true
  $scope.weaponFilterModel['warrior'] = true
  $scope.weaponFilterModel['dualsaber'] = true
  $scope.weaponFilterModel['dragonrider'] = true

  $scope.showIntroMessage = function() {
    return !$scope.classFilterModel['lancer'] &&
      !$scope.classFilterModel['brawler'] &&
      !$scope.classFilterModel['sniper'] &&
      !$scope.classFilterModel['fencer'] &&
      !$scope.classFilterModel['mage'] &&
      !$scope.classFilterModel['warrior'] &&
      !$scope.classFilterModel['dualsaber'] &&
      !$scope.classFilterModel['dragonrider'] &&
      !$scope.weaponFilterModel['lancer'] &&
      !$scope.weaponFilterModel['brawler'] &&
      !$scope.weaponFilterModel['sniper'] &&
      !$scope.weaponFilterModel['fencer'] &&
      !$scope.weaponFilterModel['mage'] &&
      !$scope.weaponFilterModel['warrior'] &&
      !$scope.weaponFilterModel['dualsaber'] &&
      !$scope.weaponFilterModel['dragonrider'];
  }

  $scope.characterClassFilter = function(type) {
    return $scope.classFilterModel[type.toLowerCase().replace(' ', '')]
  }

  $scope.weaponClassFilter = function(type) {
    return $scope.weaponFilterModel[type.toLowerCase().replace(' ', '')]
  }

  $scope.shouldShowCharacters = function() {
    for (tab in $scope.tabs) {
      if (tab.title == "Characters") {
        return tab.active;
      }
    }

    return false;
  }

  $scope.popupCharacter = function(charId, charType) {
    for (key in $scope.characters) {
      if ($scope.characters.hasOwnProperty(key)) {
        for (var i=0; i<$scope.characters[key].length;i++) {
          var char = $scope.characters[key][i]
          if (char && char.Id == charId) {
            $scope.selectedChar = char
            $scope.openChar()
          }
        }
      }
    }
  }

  $http.get('api/data.json').
    success(function(data, status, headers, config) {
      $log.info('successful pull of data')

      $scope.current = {
        'characters': [],
        'weapons': [],
        'events': []
      }

      if (data.Characters) {
        $log.info('setting scope characters')
        $scope.characters = {}

        for (key in data.Characters) {
          if (data.Characters.hasOwnProperty(key)) {

            //We create a list from the map, to use as filters, as well as assign some methods to objects
            characterList = []
            for (charKey in data.Characters[key]) {
              if (data.Characters[key].hasOwnProperty(charKey)) {
                character = data.Characters[key][charKey]
                characterList.push(character) //add to display list
                //add to current gacha list if applicable
                if (data.Current.Characters.indexOf(character.Id) > -1) {
                  $log.info("adding character to current list")

                  $scope.current.characters.push(character)
                }
              }
            }

            //This is the final reassignment to a list based structure
            $scope.characters[key] = characterList
          }
        }
      }
      if (data.Weapons) {
        $log.info('setting scope weapons')
        $scope.weapons = {}

        for (key in data.Weapons) {
          if (data.Weapons.hasOwnProperty(key)) {
            weaponList = []
            for (weaponId in data.Weapons[key]) {
              if (data.Weapons[key].hasOwnProperty(weaponId)) {
                data.Weapons[key][weaponId].popupWeapon = function(weapon) {
                  $scope.selectedWep = weapon
                  $scope.openWeapon()
                }

                weapon = data.Weapons[key][weaponId]
                weaponList.push(weapon) //add to display list
                //then add to current gacha if available
                if (data.Current.Weapons.indexOf(weapon.Id) > -1) {
                  $log.info("adding weapon to current list")
                  $scope.current.weapons.push(weapon)
                }
              }
            }

            $scope.weapons[key] = weaponList
          }
        }
      }

      $rootScope.isLoaded = true
    })
    .error(function(data, status, headers, config) {
      $log.error(data);
      $log.error(status);
      $log.error(headers);
      $log.error(config);
    })

  $scope.model = {
    name: 'Main'
  }

  $scope.openChar = function () {
    var modalInstance = $uibModal.open({
      animation: true,
      templateUrl: '/static/popupCharacter.html',
      controller: 'CharModalInstanceCtrl',
      size: 'lg',
      resolve: {
        character: function () {
          return $scope.selectedChar;
        }
      }
    });

    modalInstance.result.then(function (selectedChar) {
      $scope.selectedChar = selectedChar;
    }, function () {
      //on close event
    });
  }

  $scope.openWeapon = function () {
    var modalInstance = $uibModal.open({
      animation: true,
      templateUrl: '/static/popupWeapon.html',
      controller: 'WeaponModalInstanceCtrl',
      size: 'lg',
      resolve: {
        character: function () {
          return $scope.selectedWep;
        }
      }
    });

    modalInstance.result.then(function (selectedWep) {
      $scope.selectedWep = selectedWep;
    }, function () {
      //on close event
    });
  }

})
.directive('characterItem', function() {
  return {
    templateUrl: '/static/characterCell.html'
  }
})
.directive('weaponItem', function() {
  return {
    templateUrl: '/static/weaponCell.html'
  }
});

angular.module('app').controller('CharModalInstanceCtrl', function ($scope, $uibModalInstance, character) {
  $scope.char = character

  $scope.close = function () {
    $uibModalInstance.dismiss('cancel');
  }
});

angular.module('app').controller('WeaponModalInstanceCtrl', function ($scope, $uibModalInstance, weapon) {
  $scope.weapon = weapon

  $scope.close = function () {
    $uibModalInstance.dismiss('cancel');
  }
});
