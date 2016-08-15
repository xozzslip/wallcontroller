angular.module('wallcontrollerApp').component('communityList', {
    templateUrl: '/static/wallcontroller/js/community-list/community-list.template.html',
    controller: function($scope, $http){
        var self = this;
        $scope.isCommunitiesLoading = true
        $http.get('/api/communities/').then(function(response){
            self.communities = response.data;
            $scope.isCommunitiesLoading = false
            if (self.communities.length > 0){
                $scope.open(self.communities[0])
            }
            
        });
        $scope.open = function(community){
            opened_url = '/api/communities/' + community.pk;
            $scope.isSingleCommunityLoading = true
            $http.get(opened_url)
                .then(function(response){
                    $scope.opened_community = response.data;
                    $scope.isSingleCommunityLoading = false
                });
        }
    }
});

