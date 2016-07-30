angular.module('wallcontrollerApp').component('communityList', {
	template: 
        '<ul>' +
          '<li ng-repeat="phone in $ctrl.phones">' +
            '<span>{{phone.url}}</span>' +
            '<p>{{phone.title}}</p>' +
          '</li>' +
        '</ul>',
    controller: function($http){
    	var self = this

    	$http.get('/api/communities/').then(function(response){
    		self.phones = response.data;
    	});
    }
});