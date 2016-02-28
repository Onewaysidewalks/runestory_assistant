angular.module('app', ['ngAnimate', 'ui.bootstrap']);
angular.module('app').controller('MainCtrl', function ($scope, $http, $uibModal, $log) {

  $scope.$log = $log

  $scope.tabs = [
    {
      title: 'Characters'
    },
    { title: 'Weapons'
    }
  ]

  $scope.characterSearchText = ''
  $scope.weaponSearchText = ''

  $scope.classFilterModel = {}
  $scope.classFilterModel['lancer'] = false
  $scope.classFilterModel['brawler'] = false
  $scope.classFilterModel['sniper'] = false
  $scope.classFilterModel['fencer'] = false
  $scope.classFilterModel['mage'] = false
  $scope.classFilterModel['warrior'] = false
  $scope.classFilterModel['dualsaber'] = false
  $scope.classFilterModel['dragonrider'] = false

  $scope.classFilter = function(type) {
    return $scope.classFilterModel[type.toLowerCase().replace(' ', '')]
  }

  $scope.shouldShowCharacters = function() {
    for (tab in $scope.tabs) {
      if (tab.title == "Characters") {
        return tab.active;
      }
    }

    return false;
  }

  $http.get('api/data.json').
    success(function(data, status, headers, config) {
      $log.info('successful pull of data')
      $log.info(data)
      if (data.Characters) {
        $log.info('setting scope characters')
        $scope.characters = {}

        for (key in data.Characters) {
          if (data.Characters.hasOwnProperty(key)) {

            //We create a list from the map, to use as filters, as well as assign some methods to objects
            characterList = []
            for (charKey in data.Characters[key]) {
              if (data.Characters[key].hasOwnProperty(charKey)) {
                data.Characters[key][charKey].popupCharacter = function(char) {
                  $scope.selectedChar = char
                  $scope.openChar()
                }

                characterList.push(data.Characters[key][charKey])
              }
            }

            //This is the final reassignment to a list based structure
            $scope.characters[key] = characterList
          }
        }
      }
      if (data.Weapons) {
        $log.info('setting scope weapons')
        $scope.weapons = data.Weapons
      }
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
      templateUrl: 'popupWeapon.html',
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
.directive('characterItem', function() { //TODO: Move this to another file!
  return {
    template: '<img src="{{char.IconUrl}}" class="rs_character" ng-click="char.popupCharacter(char)" />'
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
