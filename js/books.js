var app = angular.module("booksApp", []);

app.constant("baseUrl", "books");

app.controller("booksCtrl", ['$scope', '$http', 'baseUrl', function ($scope, $http, baseUrl, fileUpload) {
    $scope.displayMode = "list";
    $scope.currentProduct = null;

    $scope.listProducts = function () {
        $http.get(baseUrl).success(function (data) {
            $scope.products = data;
        });
    }

    $scope.generatePageLink = function (product) {
        var hashids = new Hashids("Citlembik salt");
        var tokens = [9, 99, 999, 9999];
        for (var i = 0; i < 3; ++i) {
            tokens.push(Math.floor(Math.random() * 100000) + 1);
        }
        product.pageLink = hashids.encode(tokens);
        var base = "/books/";
    }

    $scope.deleteProduct = function (product) {
        $http({
            method: "DELETE",
            url: baseUrl + "/" + product.key
        }).success(function () {
            $scope.products.splice($scope.products.indexOf(product), 1);
        });
    }

    $scope.createProduct = function (product) {
        $http.post(baseUrl, product).success(function (newProduct) {
            $scope.products.push(newProduct);
            $scope.displayMode = "list";
        });
    }

    $scope.updateProduct = function (product) {
        $http({
            url: baseUrl + "/" + product.key,
            method: "PUT",
            data: product
        }).success(function (modifiedProduct) {
            for (var i = 0; i < $scope.products.length; i++) {
                if ($scope.products[i].key == modifiedProduct.key) {
                    $scope.products[i] = modifiedProduct;
                    break;
                }
            }
            $scope.displayMode = "list";
        });

    }

    $scope.createBookObj = function () {
        var o = {isbn:"", featured: "No", priority:0.1, name:"", image:"nocover.png", pageLink:""};
        $scope.generatePageLink(o);
        return o;
    }

    $scope.editOrCreateProduct = function (product) {
        $scope.currentProduct =
            product ? angular.copy(product) : $scope.createBookObj();
        if ($scope.currentProduct.featured == null) {
            $scope.currentProduct.featured = false;
        }
        $scope.displayMode = "edit";
    }

    $scope.saveEdit = function (product) {
        if (angular.isDefined(product.key)) {
            $scope.updateProduct(product);
        } else {
            $scope.createProduct(product);
        }
    }

    $scope.cancelEdit = function () {
        $scope.currentProduct = {};
        $scope.displayMode = "list";
    }

    $scope.listProducts();
}]);