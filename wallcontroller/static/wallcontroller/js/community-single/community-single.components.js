angular.module('wallcontrollerApp').component('communitySingle', {
    templateUrl: '/static/wallcontroller/js/community-single/community-single.template.html',
    controller: function($http, $routeParams){
        var self = this 

        $http.get('/api/communities/' + $routeParams.phoneId).then(function(response){
            self.community = response.data;
        });
    }
});
