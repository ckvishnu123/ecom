from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.response import Response
from rest_framework import permissions, authentication
from rest_framework.decorators import action
from rest_framework import serializers
from rest_framework import mixins, generics

from api.serializers import ProductSerializer, CartSerializer, ReviewSerializer
from api.models import Products, Cart, Reviews
from api.custompermissions import IsOwner
# Create your views here.

class ProductsView(ModelViewSet):
    # if we not need any method for example delete we can eliminate it from the list
    http_method_names = ["get", "put", "post", "delete"]
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [authentication.TokenAuthentication]

    serializer_class = ProductSerializer
    queryset = Products.objects.all()
    
    # overriding list api - need to include catogory wise sorting may be given in
    # optional query parameter
    def list(self, request, *args, **kwargs):
        qs = Products.objects.all()
        if "category" in request.query_params:
            qs = qs.filter(category=request.query_params.get("category"))
        serializer = ProductSerializer(qs, many=True)
        return Response(data=serializer.data)

    # custom method
    # for listing all categories
    # /products/list_category/
    @action(methods=["GET"], detail=False)
    def list_category(self, request, *ar, **kw):
        # if flat = True is not given then qs will be list of tuples
        # .distinct is used to avoid duplicates
        qs = Products.objects.values_list("category", flat=True).distinct()
        # no need to serialize bcoz already a list   
        return Response(data=qs)

    # custom method
    # for adding items to cart by login user
    # /products/add_to_cart/
    @action(methods=["POST"], detail=True)
    def add_to_cart(self, request, *ar, **kw):
        product = self.get_object()
        user = request.user
        # here no data is send in body still data=request.data is needed
        serializer = CartSerializer(data=request.data, context={"user": user,
        "product": product})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)

    # custom method
    # /products/{product_id}/add_review/
    @action(methods=["POST"], detail=True)
    def add_review(self, request, *ar, **kw):
        product = self.get_object()
        user = request.user
        serializer = ReviewSerializer(data=request.data, context={"product":product,
        "user": user})
        if serializer.is_valid():
            serializer.save()
            return Response(data=serializer.data)
        else:
            return Response(data=serializer.errors)



# here we can use viewset bcoz create method is already written ('add_to_cart')
# we don't need default create here
# while using viewset method names should be list, retrieve, destroy, create, update
# self.get_object won't work in view set - so id can taken by kw.get("pk") than take object
class CartsView(ViewSet):
    permission_classes = [permissions.IsAuthenticated]
    # authentication_classes = [authentication.TokenAuthentication]
    
    # /carts/
    def list(self, request, *ar, **kw):
        qs = Cart.objects.filter(user=request.user)
        serializer = CartSerializer(qs, many=True)
        return Response(data=serializer.data)

    # /carts/{cart id}/
    def destroy(self, request, *ar, **kw):
        id = kw.get("pk")
        object = Cart.objects.get(id=id)
        if object.user == request.user:
            object.delete()
            return Response(data="success")
        else:
            raise serializers.ValidationError("you have no permission to perform this operation")


""" class ReviewView(ViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def destroy(self, request, *ar, **kw):
        id = kw.get("pk")
        obj = Reviews.objects.filter(id=id)[0]
        
        if obj.user == request.user:
            obj.delete()
            return Response(data="success")
        else:
            raise serializers.ValidationError("you have no permission to perform this operation")
         """
# this delete can be written using generic view with lesser lines of code

# while using mixins we need to use generic api view
# it also need mapping via path in urls because this is like api view
class ReviewDeleteView(mixins.DestroyModelMixin, generics.GenericAPIView):
    # authentication_classes = [authentication.TokenAuthentication]
    permission_classes = [IsOwner]

    serializer_class = ReviewSerializer
    queryset = Reviews.objects.all()

    def delete(self, request, *ar, **kw):
        return self.destroy(request, *ar, **kw)