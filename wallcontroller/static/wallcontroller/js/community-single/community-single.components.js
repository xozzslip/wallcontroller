angular.module('wallcontrollerApp').component('communitySingle', {
    templateUrl: '/static/wallcontroller/js/community-single/community-single.template.html',
    controller: function($http){
        var self = this 

        $http.get('/api/communities/').then(function(response){
            self.community = response.data;
        });
    }
});
