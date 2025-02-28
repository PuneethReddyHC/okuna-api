from generic_relations.relations import GenericRelatedField
from rest_framework import serializers

from openbook_auth.models import User, UserProfile
from openbook_common.models import Emoji, Language, Badge
from openbook_common.serializers import CommonHashtagSerializer
from openbook_common.serializers_fields.post import IsEncircledField
from openbook_common.serializers_fields.post_comment import PostCommentIsMutedField
from openbook_communities.models import Community, CommunityInvite
from openbook_notifications.models import Notification, PostCommentNotification, ConnectionRequestNotification, \
    ConnectionConfirmedNotification, FollowNotification, CommunityInviteNotification, PostCommentReplyNotification, \
    PostCommentReactionNotification, PostCommentUserMentionNotification, PostUserMentionNotification, \
    CommunityNewPostNotification
from openbook_notifications.models.post_reaction_notification import PostReactionNotification
from openbook_notifications.models.user_new_post_notification import UserNewPostNotification
from openbook_notifications.serializer_fields import ParentCommentField
from openbook_posts.models import PostComment, PostReaction, Post, PostImage, PostCommentReaction, \
    PostUserMention, PostCommentUserMention
from openbook_notifications.validators import notification_id_exists


class ReadNotificationsSerializer(serializers.Serializer):
    max_id = serializers.IntegerField(
        required=False,
    )
    types = serializers.ListField(
        child=serializers.ChoiceField(
            choices=Notification.get_notification_types_values(),
            required=False,
        ),
        required=False,
    )


class UnreadNotificationsCountSerializer(serializers.Serializer):
    max_id = serializers.IntegerField(
        required=False,
    )
    types = serializers.ListField(
        child=serializers.ChoiceField(
            choices=Notification.get_notification_types_values(),
            required=False,
        ),
        required=False,
    )


class GetNotificationsSerializer(serializers.Serializer):
    count = serializers.IntegerField(
        required=False,
        max_value=20
    )
    max_id = serializers.IntegerField(
        required=False,
    )
    types = serializers.ListField(
        child=serializers.ChoiceField(
            choices=Notification.get_notification_types_values(),
            required=False,
        ),
        required=False,
    )


class NotificationsBadgeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Badge
        fields = (
            'keyword',
            'keyword_description'
        )


class PostCommentCommenterProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class PostCommentCommenterSerializer(serializers.ModelSerializer):
    profile = PostCommentCommenterProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class PostCommentCreatorProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class PostCommentCreatorSerializer(serializers.ModelSerializer):
    profile = PostCommentCreatorProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class PostImageSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(read_only=True)

    class Meta:
        model = PostImage
        fields = (
            'id',
            'image',
            'width',
            'height'
        )


class PostCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = (
            'id',
            'name',
            'avatar',
            'cover',
            'color'
        )


class NotificationPostSerializer(serializers.ModelSerializer):
    creator = PostCommentCreatorSerializer()
    is_encircled = IsEncircledField()
    community = PostCommunitySerializer()
    # Temp backwards compat
    image = PostImageSerializer(many=False)

    class Meta:
        model = Post
        fields = (
            'id',
            'uuid',
            'text',
            'creator',
            'created',
            'community',
            'is_closed',
            'is_encircled',
            'media_height',
            'media_width',
            'media_thumbnail',
            # Temp backwards compat
            'image'
        )


class PostCommentLanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Language
        fields = (
            'id',
            'code',
            'name',
        )


class NotificationPostCommentParentSerializer(serializers.ModelSerializer):
    commenter = PostCommentCommenterSerializer()
    is_muted = PostCommentIsMutedField()
    language = PostCommentLanguageSerializer()

    class Meta:
        model = PostComment
        fields = (
            'id',
            'commenter',
            'language',
            'text',
            'created',
            'is_edited',
            'is_muted'
        )


class NotificationPostCommentSerializer(serializers.ModelSerializer):
    commenter = PostCommentCommenterSerializer()
    post = NotificationPostSerializer()
    parent_comment = NotificationPostCommentParentSerializer()
    is_muted = PostCommentIsMutedField()
    language = PostCommentLanguageSerializer()
    hashtags = CommonHashtagSerializer(many=True)

    class Meta:
        model = PostComment
        fields = (
            'id',
            'commenter',
            'language',
            'text',
            'post',
            'created',
            'parent_comment',
            'is_muted',
            'hashtags'
        )


class PostCommentNotificationSerializer(serializers.ModelSerializer):
    post_comment = NotificationPostCommentSerializer()

    class Meta:
        model = PostCommentNotification
        fields = (
            'id',
            'post_comment'
        )


class PostCommentReplyNotificationSerializer(serializers.ModelSerializer):
    post_comment = NotificationPostCommentSerializer()
    # TODO Remove after a couple of releases. Not needed anymore as the post_comment includes parent_comment
    parent_comment = ParentCommentField(parent_comment_serializer=NotificationPostCommentParentSerializer)

    class Meta:
        model = PostCommentReplyNotification
        fields = (
            'id',
            'post_comment',
            'parent_comment'
        )


class PostCommentReactionReactorProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class PostCommentReactionReactorSerializer(serializers.ModelSerializer):
    profile = PostCommentReactionReactorProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class PostCommentReactionEmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emoji
        fields = (
            'id',
            'keyword',
            'image'
        )


class PostCommentReactionSerializer(serializers.ModelSerializer):
    reactor = PostCommentReactionReactorSerializer()
    emoji = PostCommentReactionEmojiSerializer()
    post_comment = NotificationPostCommentSerializer()

    class Meta:
        model = PostCommentReaction
        fields = (
            'id',
            'reactor',
            'emoji',
            'post_comment',
            'created'
        )


class PostCommentReactionNotificationSerializer(serializers.ModelSerializer):
    post_comment_reaction = PostCommentReactionSerializer()

    class Meta:
        model = PostCommentReactionNotification
        fields = (
            'id',
            'post_comment_reaction'
        )


class PostReactionReactorProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class PostReactionReactorSerializer(serializers.ModelSerializer):
    profile = PostReactionReactorProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class PostReactionEmojiSerializer(serializers.ModelSerializer):
    class Meta:
        model = Emoji
        fields = (
            'id',
            'keyword',
            'image'
        )


class PostReactionSerializer(serializers.ModelSerializer):
    reactor = PostReactionReactorSerializer()
    emoji = PostReactionEmojiSerializer()
    post = NotificationPostSerializer()

    class Meta:
        model = PostReaction
        fields = (
            'id',
            'reactor',
            'emoji',
            'post'
        )


class PostReactionNotificationSerializer(serializers.ModelSerializer):
    post_reaction = PostReactionSerializer()

    class Meta:
        model = PostReactionNotification
        fields = (
            'id',
            'post_reaction'
        )


class ConnectionRequesterProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class ConnectionRequesterSerializer(serializers.ModelSerializer):
    profile = ConnectionRequesterProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class ConnectionRequestNotificationSerializer(serializers.ModelSerializer):
    connection_requester = ConnectionRequesterSerializer()

    class Meta:
        model = ConnectionRequestNotification
        fields = (
            'id',
            'connection_requester'
        )


class ConnectionConfirmatorProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class ConnectionConfirmatorSerializer(serializers.ModelSerializer):
    profile = ConnectionConfirmatorProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class ConnectionConfirmedNotificationSerializer(serializers.ModelSerializer):
    connection_confirmator = ConnectionConfirmatorSerializer()

    class Meta:
        model = ConnectionConfirmedNotification
        fields = (
            'id',
            'connection_confirmator'
        )


class FollowerProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class FollowerSerializer(serializers.ModelSerializer):
    profile = FollowerProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class FollowNotificationSerializer(serializers.ModelSerializer):
    follower = FollowerSerializer()

    class Meta:
        model = FollowNotification
        fields = (
            'id',
            'follower'
        )


class CommunityInviteCreatorProfileSerializer(serializers.ModelSerializer):
    badges = NotificationsBadgeSerializer(many=True)

    class Meta:
        model = UserProfile
        fields = (
            'id',
            'avatar',
            'name',
            'badges'
        )


class CommunityInviteCreatorSerializer(serializers.ModelSerializer):
    profile = CommunityInviteCreatorProfileSerializer()

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'profile'
        )


class CommunityInviteCommunitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Community
        fields = (
            'id',
            'name',
            'avatar',
            'cover',
            'color'
        )


class CommunityInviteSerializer(serializers.ModelSerializer):
    creator = CommunityInviteCreatorSerializer()
    community = CommunityInviteCommunitySerializer()

    class Meta:
        model = CommunityInvite
        fields = (
            'id',
            'creator',
            'invited_user_id',
            'community'
        )


class CommunityInviteNotificationSerializer(serializers.ModelSerializer):
    community_invite = CommunityInviteSerializer()

    class Meta:
        model = CommunityInviteNotification
        fields = (
            'id',
            'community_invite'
        )


class CommunityNewPostNotificationSerializer(serializers.ModelSerializer):
    post = NotificationPostSerializer()

    class Meta:
        model = CommunityNewPostNotification
        fields = (
            'id',
            'post'
        )


class UserNewPostNotificationSerializer(serializers.ModelSerializer):
    post = NotificationPostSerializer()

    class Meta:
        model = UserNewPostNotification
        fields = (
            'id',
            'post'
        )


class PostUserMentionSerializer(serializers.ModelSerializer):
    post = NotificationPostSerializer()
    user = PostCommentCreatorSerializer()

    class Meta:
        model = PostUserMention
        fields = (
            'id',
            'post',
            'user',
        )


class PostUserMentionNotificationSerializer(serializers.ModelSerializer):
    post_user_mention = PostUserMentionSerializer()

    class Meta:
        model = PostUserMentionNotification
        fields = (
            'id',
            'post_user_mention',
        )


class PostCommentUserMentionSerializer(serializers.ModelSerializer):
    post_comment = NotificationPostCommentSerializer()
    user = PostCommentCreatorSerializer()

    class Meta:
        model = PostCommentUserMention
        fields = (
            'id',
            'post_comment',
            'user',
        )


class PostCommentUserMentionNotificationSerializer(serializers.ModelSerializer):
    post_comment_user_mention = PostCommentUserMentionSerializer()

    class Meta:
        model = PostCommentUserMentionNotification
        fields = (
            'id',
            'post_comment_user_mention',
        )


class GetNotificationsNotificationSerializer(serializers.ModelSerializer):
    content_object = GenericRelatedField({
        PostCommentNotification: PostCommentNotificationSerializer(),
        PostCommentReplyNotification: PostCommentReplyNotificationSerializer(),
        PostCommentReactionNotification: PostCommentReactionNotificationSerializer(),
        PostReactionNotification: PostReactionNotificationSerializer(),
        ConnectionRequestNotification: ConnectionRequestNotificationSerializer(),
        ConnectionConfirmedNotification: ConnectionConfirmedNotificationSerializer(),
        FollowNotification: FollowNotificationSerializer(),
        PostCommentUserMentionNotification: PostCommentUserMentionNotificationSerializer(),
        PostUserMentionNotification: PostUserMentionNotificationSerializer(),
        CommunityNewPostNotification: CommunityNewPostNotificationSerializer(),
        UserNewPostNotification: UserNewPostNotificationSerializer(),
        CommunityInviteNotification: CommunityInviteNotificationSerializer()
    })

    class Meta:
        model = Notification
        fields = (
            'id',
            'notification_type',
            'content_object',
            'read',
            'created',
        )


class DeleteNotificationSerializer(serializers.Serializer):
    notification_id = serializers.IntegerField(required=True,
                                               validators=[notification_id_exists])


class ReadNotificationSerializer(serializers.Serializer):
    notification_id = serializers.IntegerField(required=True,
                                               validators=[notification_id_exists])
