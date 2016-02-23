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
        $scope.characters = data.Characters

        for (key in $scope.characters) {
          if ($scope.characters.hasOwnProperty(key)) {
            for (charKey in $scope.characters[key]) {
              if ($scope.characters[key].hasOwnProperty(charKey)) {
                $scope.characters[key][charKey].popupCharacter = function(char) {
                  $scope.selectedChar = char
                  $scope.openChar()
                }

                $scope.characters[key][charKey].shouldFilter = function() {
                  for (tab in $scope.tabs) {
                    if (tab.title == 'Characters') {
                      $log.info("iteration tabs...")
                      if (tab.filterText && $scope.characters[key][charKey].Name.startsWith(tab.filterText)) {
                        $log.info("filterting by " + tab.filterText)
                        return true;
                      }
                    }
                  }

                  return false;
                }
              }
            }
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
      templateUrl: 'popupCharacter.html',
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
      $log.info('Character Modal close at: ' + new Date());
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
      $log.info('Weapon Modal close at: ' + new Date());
    });
  }

})
.directive('characterItem', function() { //TODO: Move this to another file!
  return {
    template: '<img src="{{char.IconUrl}}" style="width:100%px; height:50px" ng-click="char.popupCharacter(char)" ng-hide="char.shouldFilter()" />'
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
