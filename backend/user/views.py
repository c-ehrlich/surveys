from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterUserSerializer
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserCreate(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Create a new user
        TODO: deal with bad inputs, maybe add more returns etc
        example: trying to register an email that already exists
        just sends back a 400 with no explanation of what the
        problem is
        """
        reg_serializer = RegisterUserSerializer(data=request.data)
        if reg_serializer.is_valid():
            newuser = reg_serializer.save()
            if newuser:
                return Response(status=status.HTTP_201_CREATED)
        return Response(reg_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BlacklistTokenView(APIView):
    """
    Adds a refresh token to the blacklist (eg when a user logs out)
    TODO: hitting logout repreatedly creates more blacklist tokens, somehow
    (and also more outstanding tokens) - fix this!
    TODO: currently the token remains in outstanding tokens - maybe remove it from there?
    """

    permission_classes = [AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data["refresh_token"]
            token = RefreshToken(refresh_token)
            token.blacklist()
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)
