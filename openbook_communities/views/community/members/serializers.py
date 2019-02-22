from django.conf import settings
from rest_framework import serializers

from openbook_auth.models import User, UserProfile
from openbook_auth.validators import username_characters_validator, user_username_exists
from openbook_communities.models import Community, CommunityMembership
from openbook_communities.serializers_fields import CommunityMembershipsField
from openbook_communities.validators import community_name_characters_validator, community_name_exists


class JoinCommunitySerializer(serializers.Serializer):
    community_name = serializers.CharField(max_length=settings.COMMUNITY_NAME_MAX_LENGTH,
                                           allow_blank=False,
                                           validators=[community_name_characters_validator, community_name_exists])


class LeaveCommunitySerializer(serializers.Serializer):
    community_name = serializers.CharField(max_length=settings.COMMUNITY_NAME_MAX_LENGTH,
                                           allow_blank=False,
                                           validators=[community_name_characters_validator, community_name_exists])


class InviteCommunityMemberSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=settings.USERNAME_MAX_LENGTH,
                                     allow_blank=False,
                                     validators=[username_characters_validator, user_username_exists])
    community_name = serializers.CharField(max_length=settings.COMMUNITY_NAME_MAX_LENGTH,
                                           allow_blank=False,
                                           validators=[community_name_characters_validator, community_name_exists])


class GetCommunityMembersSerializer(serializers.Serializer):
    max_id = serializers.IntegerField(
        required=False,
    )
    count = serializers.IntegerField(
        required=False,
        max_value=20
    )
    exclude = serializers.ChoiceField(
        required=False,
        choices=(
            Community.EXCLUDE_COMMUNITY_ADMINISTRATORS_KEYWORD,
            Community.EXCLUDE_COMMUNITY_MODERATORS_KEYWORD,
        )
    )
    community_name = serializers.CharField(max_length=settings.COMMUNITY_NAME_MAX_LENGTH,
                                           allow_blank=False,
                                           validators=[community_name_characters_validator, community_name_exists])


class GetCommunityMembersMemberProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = (
            'avatar',
            'name'
        )


class GetCommunityMembersMemberSerializer(serializers.ModelSerializer):
    profile = GetCommunityMembersMemberProfileSerializer(many=False)

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class MembersCommunityMembershipSerializer(serializers.ModelSerializer):
    class Meta:
        model = CommunityMembership
        fields = (
            'id',
            'user_id',
            'community_id',
            'is_administrator',
            'is_moderator',
        )


class MembersCommunitySerializer(serializers.ModelSerializer):
    memberships = CommunityMembershipsField(community_membership_serializer=MembersCommunityMembershipSerializer)

    class Meta:
        model = Community
        fields = (
            'id',
            'memberships'
        )


class SearchCommunityMembersSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        required=False,
        max_value=20
    )
    query = serializers.CharField(
        max_length=settings.SEARCH_QUERIES_MAX_LENGTH,
        allow_blank=False,
        required=True
    )
    exclude = serializers.ChoiceField(
        required=False,
        choices=(
            Community.EXCLUDE_COMMUNITY_ADMINISTRATORS_KEYWORD,
            Community.EXCLUDE_COMMUNITY_MODERATORS_KEYWORD,
        )
    )
    community_name = serializers.CharField(max_length=settings.COMMUNITY_NAME_MAX_LENGTH,
                                           allow_blank=False,
                                           validators=[community_name_characters_validator, community_name_exists])
