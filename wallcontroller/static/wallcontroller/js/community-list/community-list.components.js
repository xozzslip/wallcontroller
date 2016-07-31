angular.module('wallcontrollerApp').component('communityList', {
    templateUrl: '/static/wallcontroller/js/community-list/community-list.template.html',
    controller: function($http){
    	var self = this

    	$http.get('/api/communities/').then(function(response){
    		self.communities = response.data;
    	});
    }
});