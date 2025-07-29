from unlok_next.rath import UnlokRath
from pydantic import BaseModel, Field, ConfigDict
from typing import (
    Literal,
    Annotated,
    Tuple,
    Any,
    Optional,
    AsyncIterator,
    Iterable,
    Iterator,
    List,
    Union,
)
from datetime import datetime
from unlok_next.funcs import subscribe, asubscribe, aexecute, execute
from rath.scalars import ID
from enum import Enum


class DescendantKind(str, Enum):
    """The Kind of a Descendant"""

    LEAF = "LEAF"
    MENTION = "MENTION"
    PARAGRAPH = "PARAGRAPH"


class ClientKind(str, Enum):
    """No documentation"""

    DEVELOPMENT = "DEVELOPMENT"
    WEBSITE = "WEBSITE"
    DESKTOP = "DESKTOP"


class GroupFilter(BaseModel):
    """__doc__"""

    search: Optional[str] = None
    name: Optional["StrFilterLookup"] = None
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["GroupFilter"] = Field(alias="AND", default=None)
    or_: Optional["GroupFilter"] = Field(alias="OR", default=None)
    not_: Optional["GroupFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StrFilterLookup(BaseModel):
    """No documentation"""

    exact: Optional[str] = None
    i_exact: Optional[str] = Field(alias="iExact", default=None)
    contains: Optional[str] = None
    i_contains: Optional[str] = Field(alias="iContains", default=None)
    in_list: Optional[Tuple[str, ...]] = Field(alias="inList", default=None)
    gt: Optional[str] = None
    gte: Optional[str] = None
    lt: Optional[str] = None
    lte: Optional[str] = None
    starts_with: Optional[str] = Field(alias="startsWith", default=None)
    i_starts_with: Optional[str] = Field(alias="iStartsWith", default=None)
    ends_with: Optional[str] = Field(alias="endsWith", default=None)
    i_ends_with: Optional[str] = Field(alias="iEndsWith", default=None)
    range: Optional[Tuple[str, ...]] = None
    is_null: Optional[bool] = Field(alias="isNull", default=None)
    regex: Optional[str] = None
    i_regex: Optional[str] = Field(alias="iRegex", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class OffsetPaginationInput(BaseModel):
    """No documentation"""

    offset: int
    limit: Optional[int] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ServiceInstanceFilter(BaseModel):
    """ServiceInstance(id, service, logo, identifier, steward, template)"""

    search: Optional[str] = None
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["ServiceInstanceFilter"] = Field(alias="AND", default=None)
    or_: Optional["ServiceInstanceFilter"] = Field(alias="OR", default=None)
    not_: Optional["ServiceInstanceFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UserFilter(BaseModel):
    """A User of the System

    Lok Users are the main users of the system. They can be assigned to groups and have profiles, that can be used to display information about them.
    Each user is identifier by a unique username, and can have an email address associated with them.
    """

    search: Optional[str] = None
    username: Optional[StrFilterLookup] = None
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["UserFilter"] = Field(alias="AND", default=None)
    or_: Optional["UserFilter"] = Field(alias="OR", default=None)
    not_: Optional["UserFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ClientFilter(BaseModel):
    """Client(id, name, release, oauth2_client, kind, user, redirect_uris, public, token, tenant, created_at, requirements_hash, logo)"""

    search: Optional[str] = None
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["ClientFilter"] = Field(alias="AND", default=None)
    or_: Optional["ClientFilter"] = Field(alias="OR", default=None)
    not_: Optional["ClientFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class AppFilter(BaseModel):
    """App(id, name, identifier, logo)"""

    search: Optional[str] = None
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["AppFilter"] = Field(alias="AND", default=None)
    or_: Optional["AppFilter"] = Field(alias="OR", default=None)
    not_: Optional["AppFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class ServiceFilter(BaseModel):
    """Service(id, name, identifier, logo, description)"""

    search: Optional[str] = None
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["ServiceFilter"] = Field(alias="AND", default=None)
    or_: Optional["ServiceFilter"] = Field(alias="OR", default=None)
    not_: Optional["ServiceFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class LayerFilter(BaseModel):
    """Layer(id, name, identifier, logo, description, dns_probe, get_probe, kind)"""

    search: Optional[str] = None
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["LayerFilter"] = Field(alias="AND", default=None)
    or_: Optional["LayerFilter"] = Field(alias="OR", default=None)
    not_: Optional["LayerFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class RedeemTokenFilter(BaseModel):
    """A redeem token is a token that can be used to redeem the rights to create
    a client. It is used to give the recipient the right to create a client.

    If the token is not redeemed within the expires_at time, it will be invalid.
    If the token has been redeemed, but the manifest has changed, the token will be invalid.
    """

    search: Optional[str] = None
    ids: Optional[Tuple[ID, ...]] = None
    and_: Optional["RedeemTokenFilter"] = Field(alias="AND", default=None)
    or_: Optional["RedeemTokenFilter"] = Field(alias="OR", default=None)
    not_: Optional["RedeemTokenFilter"] = Field(alias="NOT", default=None)
    distinct: Optional[bool] = Field(alias="DISTINCT", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class DescendantInput(BaseModel):
    """No documentation"""

    kind: DescendantKind
    children: Optional[Tuple["DescendantInput", ...]] = None
    user: Optional[str] = None
    bold: Optional[bool] = None
    italic: Optional[bool] = None
    code: Optional[bool] = None
    text: Optional[str] = None
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class StashItemInput(BaseModel):
    """No documentation"""

    identifier: str
    description: Optional[str] = None
    object: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateServiceInstanceInput(BaseModel):
    """No documentation"""

    identifier: str
    service: ID
    allowed_users: Optional[Tuple[ID, ...]] = Field(alias="allowedUsers", default=None)
    allowed_groups: Optional[Tuple[ID, ...]] = Field(
        alias="allowedGroups", default=None
    )
    denied_groups: Optional[Tuple[ID, ...]] = Field(alias="deniedGroups", default=None)
    denied_users: Optional[Tuple[ID, ...]] = Field(alias="deniedUsers", default=None)
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateServiceInstanceInput(BaseModel):
    """No documentation"""

    allowed_users: Optional[Tuple[ID, ...]] = Field(alias="allowedUsers", default=None)
    allowed_groups: Optional[Tuple[ID, ...]] = Field(
        alias="allowedGroups", default=None
    )
    denied_groups: Optional[Tuple[ID, ...]] = Field(alias="deniedGroups", default=None)
    denied_users: Optional[Tuple[ID, ...]] = Field(alias="deniedUsers", default=None)
    id: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateProfileInput(BaseModel):
    """No documentation"""

    id: ID
    name: str
    avatar: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateProfileInput(BaseModel):
    """No documentation"""

    user: ID
    name: str
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class UpdateGroupProfileInput(BaseModel):
    """No documentation"""

    id: ID
    name: str
    avatar: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class CreateGroupProfileInput(BaseModel):
    """No documentation"""

    group: ID
    name: str
    avatar: ID
    model_config = ConfigDict(
        frozen=True, extra="forbid", populate_by_name=True, use_enum_values=True
    )


class PresignedPostCredentials(BaseModel):
    """Temporary Credentials for a file upload that can be used by a Client (e.g. in a python datalayer)"""

    typename: Literal["PresignedPostCredentials"] = Field(
        alias="__typename", default="PresignedPostCredentials", exclude=True
    )
    x_amz_algorithm: str = Field(alias="xAmzAlgorithm")
    x_amz_credential: str = Field(alias="xAmzCredential")
    x_amz_date: str = Field(alias="xAmzDate")
    x_amz_signature: str = Field(alias="xAmzSignature")
    key: str
    bucket: str
    datalayer: str
    policy: str
    store: str
    model_config = ConfigDict(frozen=True)


class ListLayerLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ListLayer(BaseModel):
    """A Service is a Webservice that a Client might want to access. It is not the configured instance of the service, but the service itself."""

    typename: Literal["Layer"] = Field(
        alias="__typename", default="Layer", exclude=True
    )
    id: ID
    name: str
    "The name of the layer"
    description: Optional[str] = Field(default=None)
    "The description of the service. This should be a human readable description of the service."
    logo: Optional[ListLayerLogo] = Field(default=None)
    "The logo of the service. This should be a url to a logo that can be used to represent the service."
    model_config = ConfigDict(frozen=True)


class ListRedeemTokenUser(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    id: ID
    email: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ListRedeemTokenClientReleaseApp(BaseModel):
    """An App is the Arkitekt equivalent of a Software Application. It is a collection of `Releases` that can be all part of the same application. E.g the App `Napari` could have the releases `0.1.0` and `0.2.0`."""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    identifier: str
    "The identifier of the app. This should be a globally unique string that identifies the app. We encourage you to use the reverse domain name notation. E.g. `com.example.myapp`"
    model_config = ConfigDict(frozen=True)


class ListRedeemTokenClientRelease(BaseModel):
    """A Release is a version of an app. Releases might change over time. E.g. a release might be updated to fix a bug, and the release might be updated to add a new feature. This is why they are the home for `scopes` and `requirements`, which might change over the release cycle."""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    version: str
    "The version of the release. This should be a string that identifies the version of the release. We enforce semantic versioning notation. E.g. `0.1.0`. The version is unique per app."
    app: ListRedeemTokenClientReleaseApp
    "The app that this release belongs to."
    model_config = ConfigDict(frozen=True)


class ListRedeemTokenClient(BaseModel):
    """A client is a way of authenticating users with a release.
    The strategy of authentication is defined by the kind of client. And allows for different authentication flow.
    E.g a client can be a DESKTOP app, that might be used by multiple users, or a WEBSITE that wants to connect to a user's account,
    but also a DEVELOPMENT client that is used by a developer to test the app. The client model thinly wraps the oauth2 client model, which is used to authenticate users.
    """

    typename: Literal["Client"] = Field(
        alias="__typename", default="Client", exclude=True
    )
    id: ID
    release: ListRedeemTokenClientRelease
    "The release that this client belongs to."
    model_config = ConfigDict(frozen=True)


class ListRedeemToken(BaseModel):
    """A redeem token is a token that can be used to redeem the rights to create
    a client. It is used to give the recipient the right to create a client.

    If the token is not redeemed within the expires_at time, it will be invalid.
    If the token has been redeemed, but the manifest has changed, the token will be invalid.
    """

    typename: Literal["RedeemToken"] = Field(
        alias="__typename", default="RedeemToken", exclude=True
    )
    id: ID
    token: str
    "The token of the redeem token"
    user: ListRedeemTokenUser
    "The user that this redeem token belongs to."
    client: Optional[ListRedeemTokenClient] = Field(default=None)
    "The client that this redeem token belongs to."
    model_config = ConfigDict(frozen=True)


class ListGroupProfileAvatar(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ListGroupProfile(BaseModel):
    """
    A Profile of a User. A Profile can be used to display personalied information about a user.




    """

    typename: Literal["GroupProfile"] = Field(
        alias="__typename", default="GroupProfile", exclude=True
    )
    id: ID
    bio: Optional[str] = Field(default=None)
    "A short bio of the group"
    avatar: Optional[ListGroupProfileAvatar] = Field(default=None)
    "The avatar of the group"
    model_config = ConfigDict(frozen=True)


class ListGroup(BaseModel):
    """
    A Group is the base unit of Role Based Access Control. A Group can have many users and many permissions. A user can have many groups. A user with a group that has a permission can perform the action that the permission allows.
    Groups are propagated to the respecting subservices. Permissions are not. Each subservice has to define its own permissions and mappings to groups.
    """

    typename: Literal["Group"] = Field(
        alias="__typename", default="Group", exclude=True
    )
    id: ID
    name: str
    profile: Optional[ListGroupProfile] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class Leaf(BaseModel):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )
    bold: Optional[bool] = Field(default=None)
    italic: Optional[bool] = Field(default=None)
    code: Optional[str] = Field(default=None)
    text: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class CommentUserProfileAvatar(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class CommentUserProfile(BaseModel):
    """
    A Profile of a User. A Profile can be used to display personalied information about a user.

    """

    typename: Literal["Profile"] = Field(
        alias="__typename", default="Profile", exclude=True
    )
    avatar: Optional[CommentUserProfileAvatar] = Field(default=None)
    "The avatar of the user"
    model_config = ConfigDict(frozen=True)


class CommentUser(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    id: ID
    username: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    avatar: Optional[str] = Field(default=None)
    profile: CommentUserProfile
    model_config = ConfigDict(frozen=True)


class Paragraph(BaseModel):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )
    size: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ListAppLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ListApp(BaseModel):
    """An App is the Arkitekt equivalent of a Software Application. It is a collection of `Releases` that can be all part of the same application. E.g the App `Napari` could have the releases `0.1.0` and `0.2.0`."""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    id: ID
    identifier: str
    "The identifier of the app. This should be a globally unique string that identifies the app. We encourage you to use the reverse domain name notation. E.g. `com.example.myapp`"
    logo: Optional[ListAppLogo] = Field(default=None)
    "The logo of the app. This should be a url to a logo that can be used to represent the app."
    model_config = ConfigDict(frozen=True)


class ListClientUser(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    id: ID
    username: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    model_config = ConfigDict(frozen=True)


class ListClientReleaseLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ListClientReleaseAppLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ListClientReleaseApp(BaseModel):
    """An App is the Arkitekt equivalent of a Software Application. It is a collection of `Releases` that can be all part of the same application. E.g the App `Napari` could have the releases `0.1.0` and `0.2.0`."""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    id: ID
    identifier: str
    "The identifier of the app. This should be a globally unique string that identifies the app. We encourage you to use the reverse domain name notation. E.g. `com.example.myapp`"
    logo: Optional[ListClientReleaseAppLogo] = Field(default=None)
    "The logo of the app. This should be a url to a logo that can be used to represent the app."
    model_config = ConfigDict(frozen=True)


class ListClientRelease(BaseModel):
    """A Release is a version of an app. Releases might change over time. E.g. a release might be updated to fix a bug, and the release might be updated to add a new feature. This is why they are the home for `scopes` and `requirements`, which might change over the release cycle."""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    version: str
    "The version of the release. This should be a string that identifies the version of the release. We enforce semantic versioning notation. E.g. `0.1.0`. The version is unique per app."
    logo: Optional[ListClientReleaseLogo] = Field(default=None)
    "The logo of the release. This should be a url to a logo that can be used to represent the release."
    app: ListClientReleaseApp
    "The app that this release belongs to."
    model_config = ConfigDict(frozen=True)


class ListClient(BaseModel):
    """A client is a way of authenticating users with a release.
    The strategy of authentication is defined by the kind of client. And allows for different authentication flow.
    E.g a client can be a DESKTOP app, that might be used by multiple users, or a WEBSITE that wants to connect to a user's account,
    but also a DEVELOPMENT client that is used by a developer to test the app. The client model thinly wraps the oauth2 client model, which is used to authenticate users.
    """

    typename: Literal["Client"] = Field(
        alias="__typename", default="Client", exclude=True
    )
    id: ID
    user: Optional[ListClientUser] = Field(default=None)
    "If the client is a DEVELOPMENT client, which requires no further authentication, this is the user that is authenticated with the client."
    name: str
    "The name of the client. This is a human readable name of the client."
    kind: ClientKind
    "The configuration of the client. This is the configuration that will be sent to the client. It should never contain sensitive information."
    release: ListClientRelease
    "The release that this client belongs to."
    model_config = ConfigDict(frozen=True)


class GroupProfileAvatar(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class GroupProfile(BaseModel):
    """
    A Profile of a User. A Profile can be used to display personalied information about a user.




    """

    typename: Literal["GroupProfile"] = Field(
        alias="__typename", default="GroupProfile", exclude=True
    )
    id: ID
    name: Optional[str] = Field(default=None)
    "The name of the group"
    avatar: Optional[GroupProfileAvatar] = Field(default=None)
    "The avatar of the group"
    model_config = ConfigDict(frozen=True)


class ProfileAvatar(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class Profile(BaseModel):
    """
    A Profile of a User. A Profile can be used to display personalied information about a user.

    """

    typename: Literal["Profile"] = Field(
        alias="__typename", default="Profile", exclude=True
    )
    id: ID
    name: Optional[str] = Field(default=None)
    "The name of the user"
    avatar: Optional[ProfileAvatar] = Field(default=None)
    "The avatar of the user"
    model_config = ConfigDict(frozen=True)


class StashOwner(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    id: ID
    username: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    model_config = ConfigDict(frozen=True)


class Stash(BaseModel):
    """
    A Stash
    """

    typename: Literal["Stash"] = Field(
        alias="__typename", default="Stash", exclude=True
    )
    id: ID
    name: str
    description: Optional[str] = Field(default=None)
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    owner: StashOwner
    "The number of items in the stash"
    model_config = ConfigDict(frozen=True)


class StashItem(BaseModel):
    """
    A stashed item
    """

    typename: Literal["StashItem"] = Field(
        alias="__typename", default="StashItem", exclude=True
    )
    id: ID
    identifier: str
    object: str
    model_config = ConfigDict(frozen=True)


class ListUser(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    username: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    email: Optional[str] = Field(default=None)
    avatar: Optional[str] = Field(default=None)
    id: ID
    model_config = ConfigDict(frozen=True)


class MeUser(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    id: ID
    username: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    email: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    avatar: Optional[str] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class Mention(BaseModel):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )
    user: Optional[CommentUser] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class ListReleaseLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ListRelease(BaseModel):
    """A Release is a version of an app. Releases might change over time. E.g. a release might be updated to fix a bug, and the release might be updated to add a new feature. This is why they are the home for `scopes` and `requirements`, which might change over the release cycle."""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    id: ID
    version: str
    "The version of the release. This should be a string that identifies the version of the release. We enforce semantic versioning notation. E.g. `0.1.0`. The version is unique per app."
    logo: Optional[ListReleaseLogo] = Field(default=None)
    "The logo of the release. This should be a url to a logo that can be used to represent the release."
    app: ListApp
    "The app that this release belongs to."
    model_config = ConfigDict(frozen=True)


class DetailReleaseLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class DetailRelease(BaseModel):
    """A Release is a version of an app. Releases might change over time. E.g. a release might be updated to fix a bug, and the release might be updated to add a new feature. This is why they are the home for `scopes` and `requirements`, which might change over the release cycle."""

    typename: Literal["Release"] = Field(
        alias="__typename", default="Release", exclude=True
    )
    id: ID
    version: str
    "The version of the release. This should be a string that identifies the version of the release. We enforce semantic versioning notation. E.g. `0.1.0`. The version is unique per app."
    logo: Optional[DetailReleaseLogo] = Field(default=None)
    "The logo of the release. This should be a url to a logo that can be used to represent the release."
    app: ListApp
    "The app that this release belongs to."
    clients: Tuple[ListClient, ...]
    "The clients of the release"
    model_config = ConfigDict(frozen=True)


class DetailUserGroups(BaseModel):
    """
    A Group is the base unit of Role Based Access Control. A Group can have many users and many permissions. A user can have many groups. A user with a group that has a permission can perform the action that the permission allows.
    Groups are propagated to the respecting subservices. Permissions are not. Each subservice has to define its own permissions and mappings to groups.
    """

    typename: Literal["Group"] = Field(
        alias="__typename", default="Group", exclude=True
    )
    id: ID
    name: str
    model_config = ConfigDict(frozen=True)


class DetailUser(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    id: ID
    username: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    email: Optional[str] = Field(default=None)
    first_name: Optional[str] = Field(default=None, alias="firstName")
    last_name: Optional[str] = Field(default=None, alias="lastName")
    avatar: Optional[str] = Field(default=None)
    groups: Tuple[DetailUserGroups, ...]
    "The groups this user belongs to. A user will get all permissions granted to each of their groups."
    profile: Profile
    model_config = ConfigDict(frozen=True)


class ListStash(Stash, BaseModel):
    """
    A Stash
    """

    typename: Literal["Stash"] = Field(
        alias="__typename", default="Stash", exclude=True
    )
    items: Tuple[StashItem, ...]
    model_config = ConfigDict(frozen=True)


class ListServiceInstance(BaseModel):
    """A ServiceInstance is a configured instance of a Service. It will be configured by a configuration backend and will be used to send to the client as a configuration. It should never contain sensitive information."""

    typename: Literal["ServiceInstance"] = Field(
        alias="__typename", default="ServiceInstance", exclude=True
    )
    id: ID
    identifier: str
    "The identifier of the instance. This is a unique string that identifies the instance. It is used to identify the instance in the code and in the database."
    allowed_users: Tuple[ListUser, ...] = Field(alias="allowedUsers")
    "The users that are allowed to use this instance."
    denied_users: Tuple[ListUser, ...] = Field(alias="deniedUsers")
    "The users that are denied to use this instance."
    model_config = ConfigDict(frozen=True)


class DetailGroup(BaseModel):
    """
    A Group is the base unit of Role Based Access Control. A Group can have many users and many permissions. A user can have many groups. A user with a group that has a permission can perform the action that the permission allows.
    Groups are propagated to the respecting subservices. Permissions are not. Each subservice has to define its own permissions and mappings to groups.
    """

    typename: Literal["Group"] = Field(
        alias="__typename", default="Group", exclude=True
    )
    id: ID
    name: str
    users: Tuple[ListUser, ...]
    "The users that are in the group"
    profile: Optional[GroupProfile] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class DescendantChildrenChildrenBase(BaseModel):
    """A descendant of a comment. Descendend are used to render rich text in the frontend."""

    kind: DescendantKind
    unsafe_children: Optional[Tuple[Any, ...]] = Field(
        default=None, alias="unsafeChildren"
    )
    "Unsafe children are not typed and fall back to json. This is a workaround if queries get too complex."
    model_config = ConfigDict(frozen=True)


class DescendantChildrenChildrenBaseMentionDescendant(
    Mention, DescendantChildrenChildrenBase, BaseModel
):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )


class DescendantChildrenChildrenBaseParagraphDescendant(
    Paragraph, DescendantChildrenChildrenBase, BaseModel
):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )


class DescendantChildrenChildrenBaseLeafDescendant(
    Leaf, DescendantChildrenChildrenBase, BaseModel
):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )


class DescendantChildrenChildrenBaseCatchAll(DescendantChildrenChildrenBase, BaseModel):
    """Catch all class for DescendantChildrenChildrenBase"""

    typename: str = Field(alias="__typename", exclude=True)


class DescendantChildrenBase(BaseModel):
    """A descendant of a comment. Descendend are used to render rich text in the frontend."""

    kind: DescendantKind
    children: Optional[
        Tuple[
            Union[
                Annotated[
                    Union[
                        DescendantChildrenChildrenBaseMentionDescendant,
                        DescendantChildrenChildrenBaseParagraphDescendant,
                        DescendantChildrenChildrenBaseLeafDescendant,
                    ],
                    Field(discriminator="typename"),
                ],
                DescendantChildrenChildrenBaseCatchAll,
            ],
            ...,
        ]
    ] = Field(default=None)
    model_config = ConfigDict(frozen=True)


class DescendantChildrenBaseMentionDescendant(
    Mention, DescendantChildrenBase, BaseModel
):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )


class DescendantChildrenBaseParagraphDescendant(
    Paragraph, DescendantChildrenBase, BaseModel
):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )


class DescendantChildrenBaseLeafDescendant(Leaf, DescendantChildrenBase, BaseModel):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )


class DescendantChildrenBaseCatchAll(DescendantChildrenBase, BaseModel):
    """Catch all class for DescendantChildrenBase"""

    typename: str = Field(alias="__typename", exclude=True)


class DescendantBase(BaseModel):
    """A descendant of a comment. Descendend are used to render rich text in the frontend."""

    kind: DescendantKind
    children: Optional[
        Tuple[
            Union[
                Annotated[
                    Union[
                        DescendantChildrenBaseMentionDescendant,
                        DescendantChildrenBaseParagraphDescendant,
                        DescendantChildrenBaseLeafDescendant,
                    ],
                    Field(discriminator="typename"),
                ],
                DescendantChildrenBaseCatchAll,
            ],
            ...,
        ]
    ] = Field(default=None)


class DescendantCatch(DescendantBase):
    """Catch all class for DescendantBase"""

    typename: str = Field(alias="__typename", exclude=True)
    "A descendant of a comment. Descendend are used to render rich text in the frontend."
    kind: DescendantKind
    children: Optional[
        Tuple[
            Union[
                Annotated[
                    Union[
                        DescendantChildrenBaseMentionDescendant,
                        DescendantChildrenBaseParagraphDescendant,
                        DescendantChildrenBaseLeafDescendant,
                    ],
                    Field(discriminator="typename"),
                ],
                DescendantChildrenBaseCatchAll,
            ],
            ...,
        ]
    ] = Field(default=None)


class DescendantMentionDescendant(Mention, DescendantBase, BaseModel):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )


class DescendantParagraphDescendant(Paragraph, DescendantBase, BaseModel):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )


class DescendantLeafDescendant(Leaf, DescendantBase, BaseModel):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )


class DetailAppLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class DetailApp(BaseModel):
    """An App is the Arkitekt equivalent of a Software Application. It is a collection of `Releases` that can be all part of the same application. E.g the App `Napari` could have the releases `0.1.0` and `0.2.0`."""

    typename: Literal["App"] = Field(alias="__typename", default="App", exclude=True)
    id: ID
    identifier: str
    "The identifier of the app. This should be a globally unique string that identifies the app. We encourage you to use the reverse domain name notation. E.g. `com.example.myapp`"
    logo: Optional[DetailAppLogo] = Field(default=None)
    "The logo of the app. This should be a url to a logo that can be used to represent the app."
    releases: Tuple[ListRelease, ...]
    "The releases of the app. A release is a version of the app that can be installed by a user."
    model_config = ConfigDict(frozen=True)


class LayerLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class Layer(BaseModel):
    """A Service is a Webservice that a Client might want to access. It is not the configured instance of the service, but the service itself."""

    typename: Literal["Layer"] = Field(
        alias="__typename", default="Layer", exclude=True
    )
    id: ID
    name: str
    "The name of the layer"
    description: Optional[str] = Field(default=None)
    "The description of the service. This should be a human readable description of the service."
    logo: Optional[LayerLogo] = Field(default=None)
    "The logo of the service. This should be a url to a logo that can be used to represent the service."
    instances: Tuple[ListServiceInstance, ...]
    "The instances of the service. A service instance is a configured instance of a service. It will be configured by a configuration backend and will be used to send to the client as a configuration. It should never contain sensitive information."
    model_config = ConfigDict(frozen=True)


class ListServiceInstanceMapping(BaseModel):
    """A ServiceInstance is a configured instance of a Service. It will be configured by a configuration backend and will be used to send to the client as a configuration. It should never contain sensitive information."""

    typename: Literal["ServiceInstanceMapping"] = Field(
        alias="__typename", default="ServiceInstanceMapping", exclude=True
    )
    id: ID
    key: str
    "The key of the instance. This is a unique string that identifies the instance. It is used to identify the instance in the code and in the database."
    instance: ListServiceInstance
    "The service that this instance belongs to."
    client: ListClient
    "The client that this instance belongs to."
    optional: bool
    "Is this mapping optional? If a mapping is optional, you can configure the client without this mapping."
    model_config = ConfigDict(frozen=True)


class ListServiceLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ListService(BaseModel):
    """A Service is a Webservice that a Client might want to access. It is not the configured instance of the service, but the service itself."""

    typename: Literal["Service"] = Field(
        alias="__typename", default="Service", exclude=True
    )
    identifier: str
    "The identifier of the service. This should be a globally unique string that identifies the service. We encourage you to use the reverse domain name notation. E.g. `com.example.myservice`"
    id: ID
    name: str
    "The name of the service"
    logo: Optional[ListServiceLogo] = Field(default=None)
    "The logo of the app. This should be a url to a logo that can be used to represent the app."
    description: Optional[str] = Field(default=None)
    "The description of the service. This should be a human readable description of the service."
    instances: Tuple[ListServiceInstance, ...]
    "The instances of the service. A service instance is a configured instance of a service. It will be configured by a configuration backend and will be used to send to the client as a configuration. It should never contain sensitive information."
    model_config = ConfigDict(frozen=True)


class ServiceLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class Service(BaseModel):
    """A Service is a Webservice that a Client might want to access. It is not the configured instance of the service, but the service itself."""

    typename: Literal["Service"] = Field(
        alias="__typename", default="Service", exclude=True
    )
    identifier: str
    "The identifier of the service. This should be a globally unique string that identifies the service. We encourage you to use the reverse domain name notation. E.g. `com.example.myservice`"
    id: ID
    name: str
    "The name of the service"
    logo: Optional[ServiceLogo] = Field(default=None)
    "The logo of the app. This should be a url to a logo that can be used to represent the app."
    description: Optional[str] = Field(default=None)
    "The description of the service. This should be a human readable description of the service."
    instances: Tuple[ListServiceInstance, ...]
    "The instances of the service. A service instance is a configured instance of a service. It will be configured by a configuration backend and will be used to send to the client as a configuration. It should never contain sensitive information."
    model_config = ConfigDict(frozen=True)


class SubthreadCommentParent(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class SubthreadCommentDescendantsBase(BaseModel):
    """A descendant of a comment. Descendend are used to render rich text in the frontend."""

    model_config = ConfigDict(frozen=True)


class SubthreadCommentDescendantsBaseMentionDescendant(
    DescendantMentionDescendant, SubthreadCommentDescendantsBase, BaseModel
):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )


class SubthreadCommentDescendantsBaseParagraphDescendant(
    DescendantParagraphDescendant, SubthreadCommentDescendantsBase, BaseModel
):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )


class SubthreadCommentDescendantsBaseLeafDescendant(
    DescendantLeafDescendant, SubthreadCommentDescendantsBase, BaseModel
):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )


class SubthreadCommentDescendantsBaseCatchAll(
    SubthreadCommentDescendantsBase, BaseModel
):
    """Catch all class for SubthreadCommentDescendantsBase"""

    typename: str = Field(alias="__typename", exclude=True)


class SubthreadComment(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    user: CommentUser
    "The user that created this comment"
    parent: Optional[SubthreadCommentParent] = Field(default=None)
    "The parent of this comment. Think Thread"
    created_at: datetime = Field(alias="createdAt")
    "The time this comment got created"
    descendants: Tuple[
        Union[
            Annotated[
                Union[
                    SubthreadCommentDescendantsBaseMentionDescendant,
                    SubthreadCommentDescendantsBaseParagraphDescendant,
                    SubthreadCommentDescendantsBaseLeafDescendant,
                ],
                Field(discriminator="typename"),
            ],
            SubthreadCommentDescendantsBaseCatchAll,
        ],
        ...,
    ]
    "The immediate descendends of the comments. Think typed Rich Representation"
    model_config = ConfigDict(frozen=True)


class ServiceInstanceService(BaseModel):
    """A Service is a Webservice that a Client might want to access. It is not the configured instance of the service, but the service itself."""

    typename: Literal["Service"] = Field(
        alias="__typename", default="Service", exclude=True
    )
    identifier: str
    "The identifier of the service. This should be a globally unique string that identifies the service. We encourage you to use the reverse domain name notation. E.g. `com.example.myservice`"
    id: ID
    description: Optional[str] = Field(default=None)
    "The description of the service. This should be a human readable description of the service."
    name: str
    "The name of the service"
    model_config = ConfigDict(frozen=True)


class ServiceInstanceLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class ServiceInstance(BaseModel):
    """A ServiceInstance is a configured instance of a Service. It will be configured by a configuration backend and will be used to send to the client as a configuration. It should never contain sensitive information."""

    typename: Literal["ServiceInstance"] = Field(
        alias="__typename", default="ServiceInstance", exclude=True
    )
    id: ID
    identifier: str
    "The identifier of the instance. This is a unique string that identifies the instance. It is used to identify the instance in the code and in the database."
    service: ServiceInstanceService
    "The service that this instance belongs to."
    allowed_users: Tuple[ListUser, ...] = Field(alias="allowedUsers")
    "The users that are allowed to use this instance."
    denied_users: Tuple[ListUser, ...] = Field(alias="deniedUsers")
    "The users that are denied to use this instance."
    allowed_groups: Tuple[ListGroup, ...] = Field(alias="allowedGroups")
    "The groups that are allowed to use this instance."
    denied_groups: Tuple[ListGroup, ...] = Field(alias="deniedGroups")
    "The groups that are denied to use this instance."
    mappings: Tuple[ListServiceInstanceMapping, ...]
    "The mappings of the composition. A mapping is a mapping of a service to a service instance. This is used to configure the composition."
    logo: Optional[ServiceInstanceLogo] = Field(default=None)
    "The logo of the app. This should be a url to a logo that can be used to represent the app."
    model_config = ConfigDict(frozen=True)


class DetailClientUser(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    id: ID
    username: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    model_config = ConfigDict(frozen=True)


class DetailClientLogo(BaseModel):
    """MediaStore(id, path, key, bucket, populated, s3store_ptr)"""

    typename: Literal["MediaStore"] = Field(
        alias="__typename", default="MediaStore", exclude=True
    )
    presigned_url: str = Field(alias="presignedUrl")
    model_config = ConfigDict(frozen=True)


class DetailClientOauth2client(BaseModel):
    """OAuth2Client(id, user, client_id, client_secret, redirect_uris, scope, token_endpoint_auth_method, grant_types, response_types)"""

    typename: Literal["Oauth2Client"] = Field(
        alias="__typename", default="Oauth2Client", exclude=True
    )
    client_id: str = Field(alias="clientId")
    model_config = ConfigDict(frozen=True)


class DetailClient(BaseModel):
    """A client is a way of authenticating users with a release.
    The strategy of authentication is defined by the kind of client. And allows for different authentication flow.
    E.g a client can be a DESKTOP app, that might be used by multiple users, or a WEBSITE that wants to connect to a user's account,
    but also a DEVELOPMENT client that is used by a developer to test the app. The client model thinly wraps the oauth2 client model, which is used to authenticate users.
    """

    typename: Literal["Client"] = Field(
        alias="__typename", default="Client", exclude=True
    )
    id: ID
    token: str
    "The configuration of the client. This is the configuration that will be sent to the client. It should never contain sensitive information."
    name: str
    "The name of the client. This is a human readable name of the client."
    user: Optional[DetailClientUser] = Field(default=None)
    "If the client is a DEVELOPMENT client, which requires no further authentication, this is the user that is authenticated with the client."
    kind: ClientKind
    "The configuration of the client. This is the configuration that will be sent to the client. It should never contain sensitive information."
    release: ListRelease
    "The release that this client belongs to."
    logo: Optional[DetailClientLogo] = Field(default=None)
    "The logo of the release. This should be a url to a logo that can be used to represent the release."
    oauth2_client: DetailClientOauth2client = Field(alias="oauth2Client")
    "The real oauth2 client that is used to authenticate users with this client."
    mappings: Tuple[ListServiceInstanceMapping, ...]
    "The mappings of the client. A mapping is a mapping of a service to a service instance. This is used to configure the composition."
    model_config = ConfigDict(frozen=True)


class ListCommentParent(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class ListCommentDescendantsBase(BaseModel):
    """A descendant of a comment. Descendend are used to render rich text in the frontend."""

    model_config = ConfigDict(frozen=True)


class ListCommentDescendantsBaseMentionDescendant(
    DescendantMentionDescendant, ListCommentDescendantsBase, BaseModel
):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )


class ListCommentDescendantsBaseParagraphDescendant(
    DescendantParagraphDescendant, ListCommentDescendantsBase, BaseModel
):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )


class ListCommentDescendantsBaseLeafDescendant(
    DescendantLeafDescendant, ListCommentDescendantsBase, BaseModel
):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )


class ListCommentDescendantsBaseCatchAll(ListCommentDescendantsBase, BaseModel):
    """Catch all class for ListCommentDescendantsBase"""

    typename: str = Field(alias="__typename", exclude=True)


class ListComment(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    user: CommentUser
    "The user that created this comment"
    parent: Optional[ListCommentParent] = Field(default=None)
    "The parent of this comment. Think Thread"
    descendants: Tuple[
        Union[
            Annotated[
                Union[
                    ListCommentDescendantsBaseMentionDescendant,
                    ListCommentDescendantsBaseParagraphDescendant,
                    ListCommentDescendantsBaseLeafDescendant,
                ],
                Field(discriminator="typename"),
            ],
            ListCommentDescendantsBaseCatchAll,
        ],
        ...,
    ]
    "The immediate descendends of the comments. Think typed Rich Representation"
    resolved: bool
    resolved_by: Optional[CommentUser] = Field(default=None, alias="resolvedBy")
    "The user that resolved this comment"
    id: ID
    created_at: datetime = Field(alias="createdAt")
    "The time this comment got created"
    children: Tuple[SubthreadComment, ...]
    "The children of this comment"
    model_config = ConfigDict(frozen=True)


class MentionCommentParent(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class MentionCommentDescendantsBase(BaseModel):
    """A descendant of a comment. Descendend are used to render rich text in the frontend."""

    model_config = ConfigDict(frozen=True)


class MentionCommentDescendantsBaseMentionDescendant(
    DescendantMentionDescendant, MentionCommentDescendantsBase, BaseModel
):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )


class MentionCommentDescendantsBaseParagraphDescendant(
    DescendantParagraphDescendant, MentionCommentDescendantsBase, BaseModel
):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )


class MentionCommentDescendantsBaseLeafDescendant(
    DescendantLeafDescendant, MentionCommentDescendantsBase, BaseModel
):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )


class MentionCommentDescendantsBaseCatchAll(MentionCommentDescendantsBase, BaseModel):
    """Catch all class for MentionCommentDescendantsBase"""

    typename: str = Field(alias="__typename", exclude=True)


class MentionComment(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    user: CommentUser
    "The user that created this comment"
    parent: Optional[MentionCommentParent] = Field(default=None)
    "The parent of this comment. Think Thread"
    descendants: Tuple[
        Union[
            Annotated[
                Union[
                    MentionCommentDescendantsBaseMentionDescendant,
                    MentionCommentDescendantsBaseParagraphDescendant,
                    MentionCommentDescendantsBaseLeafDescendant,
                ],
                Field(discriminator="typename"),
            ],
            MentionCommentDescendantsBaseCatchAll,
        ],
        ...,
    ]
    "The immediate descendends of the comments. Think typed Rich Representation"
    id: ID
    created_at: datetime = Field(alias="createdAt")
    "The time this comment got created"
    children: Tuple[SubthreadComment, ...]
    "The children of this comment"
    mentions: Tuple[CommentUser, ...]
    "The users that got mentioned in this comment"
    resolved: bool
    resolved_by: Optional[CommentUser] = Field(default=None, alias="resolvedBy")
    "The user that resolved this comment"
    object: str
    "The object id of the object, on its associated service"
    identifier: str
    "The identifier of the object. Consult the documentation for the format"
    model_config = ConfigDict(frozen=True)


class DetailCommentParent(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class DetailCommentDescendantsBase(BaseModel):
    """A descendant of a comment. Descendend are used to render rich text in the frontend."""

    model_config = ConfigDict(frozen=True)


class DetailCommentDescendantsBaseMentionDescendant(
    DescendantMentionDescendant, DetailCommentDescendantsBase, BaseModel
):
    """A mention of a user"""

    typename: Literal["MentionDescendant"] = Field(
        alias="__typename", default="MentionDescendant", exclude=True
    )


class DetailCommentDescendantsBaseParagraphDescendant(
    DescendantParagraphDescendant, DetailCommentDescendantsBase, BaseModel
):
    """A Paragraph of text"""

    typename: Literal["ParagraphDescendant"] = Field(
        alias="__typename", default="ParagraphDescendant", exclude=True
    )


class DetailCommentDescendantsBaseLeafDescendant(
    DescendantLeafDescendant, DetailCommentDescendantsBase, BaseModel
):
    """A leaf of text. This is the most basic descendant and always ends a tree."""

    typename: Literal["LeafDescendant"] = Field(
        alias="__typename", default="LeafDescendant", exclude=True
    )


class DetailCommentDescendantsBaseCatchAll(DetailCommentDescendantsBase, BaseModel):
    """Catch all class for DetailCommentDescendantsBase"""

    typename: str = Field(alias="__typename", exclude=True)


class DetailComment(BaseModel):
    """Comments represent the comments of a user on a specific data item
    tart are identified by the unique combination of `identifier` and `object`.
    E.g a comment for an Image on the Mikro services would be serverd as
    `@mikro/image:imageID`.

    Comments always belong to the user that created it. Comments in threads
    get a parent attribute set, that points to the immediate parent.

    Each comment contains multiple descendents, that make up a *rich* representation
    of the underlying comment data including potential mentions, or links, or
    paragraphs."""

    typename: Literal["Comment"] = Field(
        alias="__typename", default="Comment", exclude=True
    )
    user: CommentUser
    "The user that created this comment"
    parent: Optional[DetailCommentParent] = Field(default=None)
    "The parent of this comment. Think Thread"
    descendants: Tuple[
        Union[
            Annotated[
                Union[
                    DetailCommentDescendantsBaseMentionDescendant,
                    DetailCommentDescendantsBaseParagraphDescendant,
                    DetailCommentDescendantsBaseLeafDescendant,
                ],
                Field(discriminator="typename"),
            ],
            DetailCommentDescendantsBaseCatchAll,
        ],
        ...,
    ]
    "The immediate descendends of the comments. Think typed Rich Representation"
    id: ID
    resolved: bool
    resolved_by: Optional[CommentUser] = Field(default=None, alias="resolvedBy")
    "The user that resolved this comment"
    created_at: datetime = Field(alias="createdAt")
    "The time this comment got created"
    children: Tuple[SubthreadComment, ...]
    "The children of this comment"
    mentions: Tuple[CommentUser, ...]
    "The users that got mentioned in this comment"
    object: str
    "The object id of the object, on its associated service"
    identifier: str
    "The identifier of the object. Consult the documentation for the format"
    model_config = ConfigDict(frozen=True)


class UpdateServiceInstanceMutation(BaseModel):
    """No documentation found for this operation."""

    update_service_instance: ServiceInstance = Field(alias="updateServiceInstance")

    class Arguments(BaseModel):
        """Arguments for UpdateServiceInstance"""

        input: UpdateServiceInstanceInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateServiceInstance"""

        document = "fragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListGroup on Group {\n  id\n  name\n  profile {\n    id\n    bio\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListServiceInstanceMapping on ServiceInstanceMapping {\n  id\n  key\n  instance {\n    ...ListServiceInstance\n    __typename\n  }\n  client {\n    ...ListClient\n    __typename\n  }\n  optional\n  __typename\n}\n\nfragment ServiceInstance on ServiceInstance {\n  id\n  identifier\n  service {\n    identifier\n    id\n    description\n    name\n    __typename\n  }\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  allowedGroups {\n    ...ListGroup\n    __typename\n  }\n  deniedGroups {\n    ...ListGroup\n    __typename\n  }\n  mappings {\n    ...ListServiceInstanceMapping\n    __typename\n  }\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateServiceInstance($input: UpdateServiceInstanceInput!) {\n  updateServiceInstance(input: $input) {\n    ...ServiceInstance\n    __typename\n  }\n}"


class CreateServiceInstanceMutation(BaseModel):
    """No documentation found for this operation."""

    create_service_instance: ServiceInstance = Field(alias="createServiceInstance")

    class Arguments(BaseModel):
        """Arguments for CreateServiceInstance"""

        input: CreateServiceInstanceInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateServiceInstance"""

        document = "fragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListGroup on Group {\n  id\n  name\n  profile {\n    id\n    bio\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListServiceInstanceMapping on ServiceInstanceMapping {\n  id\n  key\n  instance {\n    ...ListServiceInstance\n    __typename\n  }\n  client {\n    ...ListClient\n    __typename\n  }\n  optional\n  __typename\n}\n\nfragment ServiceInstance on ServiceInstance {\n  id\n  identifier\n  service {\n    identifier\n    id\n    description\n    name\n    __typename\n  }\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  allowedGroups {\n    ...ListGroup\n    __typename\n  }\n  deniedGroups {\n    ...ListGroup\n    __typename\n  }\n  mappings {\n    ...ListServiceInstanceMapping\n    __typename\n  }\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nmutation CreateServiceInstance($input: CreateServiceInstanceInput!) {\n  createServiceInstance(input: $input) {\n    ...ServiceInstance\n    __typename\n  }\n}"


class RequestMediaUploadMutation(BaseModel):
    """No documentation found for this operation."""

    request_media_upload: PresignedPostCredentials = Field(alias="requestMediaUpload")

    class Arguments(BaseModel):
        """Arguments for RequestMediaUpload"""

        key: str
        datalayer: str
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RequestMediaUpload"""

        document = "fragment PresignedPostCredentials on PresignedPostCredentials {\n  xAmzAlgorithm\n  xAmzCredential\n  xAmzDate\n  xAmzSignature\n  key\n  bucket\n  datalayer\n  policy\n  store\n  __typename\n}\n\nmutation RequestMediaUpload($key: String!, $datalayer: String!) {\n  requestMediaUpload(input: {key: $key, datalayer: $datalayer}) {\n    ...PresignedPostCredentials\n    __typename\n  }\n}"


class CreateCommentMutation(BaseModel):
    """No documentation found for this operation."""

    create_comment: ListComment = Field(alias="createComment")

    class Arguments(BaseModel):
        """Arguments for CreateComment"""

        object: ID
        identifier: str
        descendants: List[DescendantInput]
        parent: Optional[ID] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateComment"""

        document = "fragment Leaf on LeafDescendant {\n  bold\n  italic\n  code\n  text\n  __typename\n}\n\nfragment Mention on MentionDescendant {\n  user {\n    ...CommentUser\n    __typename\n  }\n  __typename\n}\n\nfragment Paragraph on ParagraphDescendant {\n  size\n  __typename\n}\n\nfragment CommentUser on User {\n  id\n  username\n  avatar\n  profile {\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubthreadComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  createdAt\n  descendants {\n    ...Descendant\n    __typename\n  }\n  __typename\n}\n\nfragment Descendant on Descendant {\n  kind\n  children {\n    kind\n    children {\n      kind\n      unsafeChildren\n      ...Leaf\n      ...Mention\n      ...Paragraph\n      __typename\n    }\n    ...Leaf\n    ...Mention\n    ...Paragraph\n    __typename\n  }\n  ...Mention\n  ...Paragraph\n  ...Leaf\n  __typename\n}\n\nfragment ListComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  descendants {\n    ...Descendant\n    __typename\n  }\n  resolved\n  resolvedBy {\n    ...CommentUser\n    __typename\n  }\n  id\n  createdAt\n  children {\n    ...SubthreadComment\n    __typename\n  }\n  __typename\n}\n\nmutation CreateComment($object: ID!, $identifier: Identifier!, $descendants: [DescendantInput!]!, $parent: ID) {\n  createComment(\n    input: {object: $object, identifier: $identifier, descendants: $descendants, parent: $parent}\n  ) {\n    ...ListComment\n    __typename\n  }\n}"


class ReplyToMutation(BaseModel):
    """No documentation found for this operation."""

    reply_to: ListComment = Field(alias="replyTo")

    class Arguments(BaseModel):
        """Arguments for ReplyTo"""

        descendants: List[DescendantInput]
        parent: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ReplyTo"""

        document = "fragment Leaf on LeafDescendant {\n  bold\n  italic\n  code\n  text\n  __typename\n}\n\nfragment Mention on MentionDescendant {\n  user {\n    ...CommentUser\n    __typename\n  }\n  __typename\n}\n\nfragment Paragraph on ParagraphDescendant {\n  size\n  __typename\n}\n\nfragment CommentUser on User {\n  id\n  username\n  avatar\n  profile {\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubthreadComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  createdAt\n  descendants {\n    ...Descendant\n    __typename\n  }\n  __typename\n}\n\nfragment Descendant on Descendant {\n  kind\n  children {\n    kind\n    children {\n      kind\n      unsafeChildren\n      ...Leaf\n      ...Mention\n      ...Paragraph\n      __typename\n    }\n    ...Leaf\n    ...Mention\n    ...Paragraph\n    __typename\n  }\n  ...Mention\n  ...Paragraph\n  ...Leaf\n  __typename\n}\n\nfragment ListComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  descendants {\n    ...Descendant\n    __typename\n  }\n  resolved\n  resolvedBy {\n    ...CommentUser\n    __typename\n  }\n  id\n  createdAt\n  children {\n    ...SubthreadComment\n    __typename\n  }\n  __typename\n}\n\nmutation ReplyTo($descendants: [DescendantInput!]!, $parent: ID!) {\n  replyTo(input: {descendants: $descendants, parent: $parent}) {\n    ...ListComment\n    __typename\n  }\n}"


class ResolveCommentMutation(BaseModel):
    """No documentation found for this operation."""

    resolve_comment: ListComment = Field(alias="resolveComment")

    class Arguments(BaseModel):
        """Arguments for ResolveComment"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ResolveComment"""

        document = "fragment Leaf on LeafDescendant {\n  bold\n  italic\n  code\n  text\n  __typename\n}\n\nfragment Mention on MentionDescendant {\n  user {\n    ...CommentUser\n    __typename\n  }\n  __typename\n}\n\nfragment Paragraph on ParagraphDescendant {\n  size\n  __typename\n}\n\nfragment CommentUser on User {\n  id\n  username\n  avatar\n  profile {\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubthreadComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  createdAt\n  descendants {\n    ...Descendant\n    __typename\n  }\n  __typename\n}\n\nfragment Descendant on Descendant {\n  kind\n  children {\n    kind\n    children {\n      kind\n      unsafeChildren\n      ...Leaf\n      ...Mention\n      ...Paragraph\n      __typename\n    }\n    ...Leaf\n    ...Mention\n    ...Paragraph\n    __typename\n  }\n  ...Mention\n  ...Paragraph\n  ...Leaf\n  __typename\n}\n\nfragment ListComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  descendants {\n    ...Descendant\n    __typename\n  }\n  resolved\n  resolvedBy {\n    ...CommentUser\n    __typename\n  }\n  id\n  createdAt\n  children {\n    ...SubthreadComment\n    __typename\n  }\n  __typename\n}\n\nmutation ResolveComment($id: ID!) {\n  resolveComment(input: {id: $id}) {\n    ...ListComment\n    __typename\n  }\n}"


class CreateClientMutationCreatedevelopmentalclient(BaseModel):
    """A client is a way of authenticating users with a release.
    The strategy of authentication is defined by the kind of client. And allows for different authentication flow.
    E.g a client can be a DESKTOP app, that might be used by multiple users, or a WEBSITE that wants to connect to a user's account,
    but also a DEVELOPMENT client that is used by a developer to test the app. The client model thinly wraps the oauth2 client model, which is used to authenticate users.
    """

    typename: Literal["Client"] = Field(
        alias="__typename", default="Client", exclude=True
    )
    id: ID
    model_config = ConfigDict(frozen=True)


class CreateClientMutation(BaseModel):
    """No documentation found for this operation."""

    create_developmental_client: CreateClientMutationCreatedevelopmentalclient = Field(
        alias="createDevelopmentalClient"
    )

    class Arguments(BaseModel):
        """Arguments for CreateClient"""

        identifier: str
        version: str
        scopes: List[str]
        logo: Optional[str] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateClient"""

        document = "mutation CreateClient($identifier: String!, $version: String!, $scopes: [String!]!, $logo: String) {\n  createDevelopmentalClient(\n    input: {manifest: {identifier: $identifier, version: $version, scopes: $scopes, logo: $logo}}\n  ) {\n    id\n    __typename\n  }\n}"


class CreateGroupProfileMutation(BaseModel):
    """No documentation found for this operation."""

    create_group_profile: GroupProfile = Field(alias="createGroupProfile")

    class Arguments(BaseModel):
        """Arguments for CreateGroupProfile"""

        input: CreateGroupProfileInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateGroupProfile"""

        document = "fragment GroupProfile on GroupProfile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nmutation CreateGroupProfile($input: CreateGroupProfileInput!) {\n  createGroupProfile(input: $input) {\n    ...GroupProfile\n    __typename\n  }\n}"


class UpdateGroupProfileMutation(BaseModel):
    """No documentation found for this operation."""

    update_group_profile: GroupProfile = Field(alias="updateGroupProfile")

    class Arguments(BaseModel):
        """Arguments for UpdateGroupProfile"""

        input: UpdateGroupProfileInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateGroupProfile"""

        document = "fragment GroupProfile on GroupProfile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateGroupProfile($input: UpdateGroupProfileInput!) {\n  updateGroupProfile(input: $input) {\n    ...GroupProfile\n    __typename\n  }\n}"


class CreateUserProfileMutation(BaseModel):
    """No documentation found for this operation."""

    create_profile: Profile = Field(alias="createProfile")

    class Arguments(BaseModel):
        """Arguments for CreateUserProfile"""

        input: CreateProfileInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateUserProfile"""

        document = "fragment Profile on Profile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nmutation CreateUserProfile($input: CreateProfileInput!) {\n  createProfile(input: $input) {\n    ...Profile\n    __typename\n  }\n}"


class UpdateUserProfileMutation(BaseModel):
    """No documentation found for this operation."""

    update_profile: Profile = Field(alias="updateProfile")

    class Arguments(BaseModel):
        """Arguments for UpdateUserProfile"""

        input: UpdateProfileInput
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UpdateUserProfile"""

        document = "fragment Profile on Profile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nmutation UpdateUserProfile($input: UpdateProfileInput!) {\n  updateProfile(input: $input) {\n    ...Profile\n    __typename\n  }\n}"


class CreateStashMutation(BaseModel):
    """No documentation found for this operation."""

    create_stash: ListStash = Field(alias="createStash")
    "Create a new stash"

    class Arguments(BaseModel):
        """Arguments for CreateStash"""

        name: Optional[str] = Field(default=None)
        description: Optional[str] = Field(default="")
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CreateStash"""

        document = 'fragment Stash on Stash {\n  id\n  name\n  description\n  createdAt\n  updatedAt\n  owner {\n    id\n    username\n    __typename\n  }\n  __typename\n}\n\nfragment StashItem on StashItem {\n  id\n  identifier\n  object\n  __typename\n}\n\nfragment ListStash on Stash {\n  ...Stash\n  items {\n    ...StashItem\n    __typename\n  }\n  __typename\n}\n\nmutation CreateStash($name: String, $description: String = "") {\n  createStash(input: {name: $name, description: $description}) {\n    ...ListStash\n    __typename\n  }\n}'


class AddItemsToStashMutation(BaseModel):
    """No documentation found for this operation."""

    add_items_to_stash: Tuple[StashItem, ...] = Field(alias="addItemsToStash")
    "Add items to a stash"

    class Arguments(BaseModel):
        """Arguments for AddItemsToStash"""

        stash: ID
        items: List[StashItemInput]
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for AddItemsToStash"""

        document = "fragment StashItem on StashItem {\n  id\n  identifier\n  object\n  __typename\n}\n\nmutation AddItemsToStash($stash: ID!, $items: [StashItemInput!]!) {\n  addItemsToStash(input: {stash: $stash, items: $items}) {\n    ...StashItem\n    __typename\n  }\n}"


class DeleteStashItemsMutation(BaseModel):
    """No documentation found for this operation."""

    delete_stash_items: Tuple[ID, ...] = Field(alias="deleteStashItems")
    "Delete items from a stash"

    class Arguments(BaseModel):
        """Arguments for DeleteStashItems"""

        items: List[ID]
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DeleteStashItems"""

        document = "mutation DeleteStashItems($items: [ID!]!) {\n  deleteStashItems(input: {items: $items})\n}"


class DeleteStashMutation(BaseModel):
    """No documentation found for this operation."""

    delete_stash: ID = Field(alias="deleteStash")

    class Arguments(BaseModel):
        """Arguments for DeleteStash"""

        stash: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DeleteStash"""

        document = "mutation DeleteStash($stash: ID!) {\n  deleteStash(input: {stash: $stash})\n}"


class ListServiceInstancesQuery(BaseModel):
    """No documentation found for this operation."""

    service_instances: Tuple[ListServiceInstance, ...] = Field(alias="serviceInstances")

    class Arguments(BaseModel):
        """Arguments for ListServiceInstances"""

        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        filters: Optional[ServiceInstanceFilter] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListServiceInstances"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nquery ListServiceInstances($pagination: OffsetPaginationInput, $filters: ServiceInstanceFilter) {\n  serviceInstances(pagination: $pagination, filters: $filters) {\n    ...ListServiceInstance\n    __typename\n  }\n}"


class GetServiceInstanceQuery(BaseModel):
    """No documentation found for this operation."""

    service_instance: ServiceInstance = Field(alias="serviceInstance")

    class Arguments(BaseModel):
        """Arguments for GetServiceInstance"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetServiceInstance"""

        document = "fragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListGroup on Group {\n  id\n  name\n  profile {\n    id\n    bio\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListServiceInstanceMapping on ServiceInstanceMapping {\n  id\n  key\n  instance {\n    ...ListServiceInstance\n    __typename\n  }\n  client {\n    ...ListClient\n    __typename\n  }\n  optional\n  __typename\n}\n\nfragment ServiceInstance on ServiceInstance {\n  id\n  identifier\n  service {\n    identifier\n    id\n    description\n    name\n    __typename\n  }\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  allowedGroups {\n    ...ListGroup\n    __typename\n  }\n  deniedGroups {\n    ...ListGroup\n    __typename\n  }\n  mappings {\n    ...ListServiceInstanceMapping\n    __typename\n  }\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nquery GetServiceInstance($id: ID!) {\n  serviceInstance(id: $id) {\n    ...ServiceInstance\n    __typename\n  }\n}"


class ListServicesQuery(BaseModel):
    """No documentation found for this operation."""

    services: Tuple[ListService, ...]

    class Arguments(BaseModel):
        """Arguments for ListServices"""

        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        filters: Optional[ServiceFilter] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ListServices"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment ListService on Service {\n  identifier\n  id\n  name\n  logo {\n    presignedUrl\n    __typename\n  }\n  description\n  instances {\n    ...ListServiceInstance\n    __typename\n  }\n  __typename\n}\n\nquery ListServices($pagination: OffsetPaginationInput, $filters: ServiceFilter) {\n  services(pagination: $pagination, filters: $filters) {\n    ...ListService\n    __typename\n  }\n}"


class GetServiceQuery(BaseModel):
    """No documentation found for this operation."""

    service: Service

    class Arguments(BaseModel):
        """Arguments for GetService"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GetService"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment Service on Service {\n  identifier\n  id\n  name\n  logo {\n    presignedUrl\n    __typename\n  }\n  description\n  instances {\n    ...ListServiceInstance\n    __typename\n  }\n  __typename\n}\n\nquery GetService($id: ID!) {\n  service(id: $id) {\n    ...Service\n    __typename\n  }\n}"


class ReleasesQuery(BaseModel):
    """No documentation found for this operation."""

    releases: Tuple[ListRelease, ...]

    class Arguments(BaseModel):
        """Arguments for Releases"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Releases"""

        document = "fragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment ListRelease on Release {\n  id\n  version\n  logo {\n    presignedUrl\n    __typename\n  }\n  app {\n    ...ListApp\n    __typename\n  }\n  __typename\n}\n\nquery Releases {\n  releases {\n    ...ListRelease\n    __typename\n  }\n}"


class ReleaseQuery(BaseModel):
    """No documentation found for this operation."""

    release: DetailRelease

    class Arguments(BaseModel):
        """Arguments for Release"""

        identifier: Optional[str] = Field(default=None)
        version: Optional[str] = Field(default=None)
        id: Optional[ID] = Field(default=None)
        client_id: Optional[ID] = Field(alias="clientId", default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Release"""

        document = "fragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment DetailRelease on Release {\n  id\n  version\n  logo {\n    presignedUrl\n    __typename\n  }\n  app {\n    ...ListApp\n    __typename\n  }\n  clients {\n    ...ListClient\n    __typename\n  }\n  __typename\n}\n\nquery Release($identifier: AppIdentifier, $version: Version, $id: ID, $clientId: ID) {\n  release(\n    identifier: $identifier\n    version: $version\n    id: $id\n    clientId: $clientId\n  ) {\n    ...DetailRelease\n    __typename\n  }\n}"


class DetailReleaseQuery(BaseModel):
    """No documentation found for this operation."""

    release: DetailRelease

    class Arguments(BaseModel):
        """Arguments for DetailRelease"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DetailRelease"""

        document = "fragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment DetailRelease on Release {\n  id\n  version\n  logo {\n    presignedUrl\n    __typename\n  }\n  app {\n    ...ListApp\n    __typename\n  }\n  clients {\n    ...ListClient\n    __typename\n  }\n  __typename\n}\n\nquery DetailRelease($id: ID!) {\n  release(id: $id) {\n    ...DetailRelease\n    __typename\n  }\n}"


class LayersQuery(BaseModel):
    """No documentation found for this operation."""

    layers: Tuple[ListLayer, ...]

    class Arguments(BaseModel):
        """Arguments for Layers"""

        filters: Optional[LayerFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Layers"""

        document = "fragment ListLayer on Layer {\n  id\n  name\n  description\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nquery Layers($filters: LayerFilter, $pagination: OffsetPaginationInput) {\n  layers(filters: $filters, pagination: $pagination) {\n    ...ListLayer\n    __typename\n  }\n}"


class DetailLayerQuery(BaseModel):
    """No documentation found for this operation."""

    layer: Layer

    class Arguments(BaseModel):
        """Arguments for DetailLayer"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DetailLayer"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment Layer on Layer {\n  id\n  name\n  description\n  logo {\n    presignedUrl\n    __typename\n  }\n  instances {\n    ...ListServiceInstance\n    __typename\n  }\n  __typename\n}\n\nquery DetailLayer($id: ID!) {\n  layer(id: $id) {\n    ...Layer\n    __typename\n  }\n}"


class GlobalSearchQuery(BaseModel):
    """No documentation found for this operation."""

    users: Tuple[ListUser, ...]
    groups: Tuple[ListGroup, ...]

    class Arguments(BaseModel):
        """Arguments for GlobalSearch"""

        search: Optional[str] = Field(default=None)
        no_users: bool = Field(alias="noUsers")
        no_groups: bool = Field(alias="noGroups")
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GlobalSearch"""

        document = "fragment ListGroup on Group {\n  id\n  name\n  profile {\n    id\n    bio\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nquery GlobalSearch($search: String, $noUsers: Boolean!, $noGroups: Boolean!, $pagination: OffsetPaginationInput) {\n  users: users(filters: {search: $search}, pagination: $pagination) @skip(if: $noUsers) {\n    ...ListUser\n    __typename\n  }\n  groups: groups(filters: {search: $search}, pagination: $pagination) @skip(if: $noGroups) {\n    ...ListGroup\n    __typename\n  }\n}"


class AppsQuery(BaseModel):
    """No documentation found for this operation."""

    apps: Tuple[ListApp, ...]

    class Arguments(BaseModel):
        """Arguments for Apps"""

        filters: Optional[AppFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Apps"""

        document = "fragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nquery Apps($filters: AppFilter, $pagination: OffsetPaginationInput) {\n  apps(filters: $filters, pagination: $pagination) {\n    ...ListApp\n    __typename\n  }\n}"


class AppQuery(BaseModel):
    """No documentation found for this operation."""

    app: DetailApp

    class Arguments(BaseModel):
        """Arguments for App"""

        identifier: Optional[str] = Field(default=None)
        id: Optional[ID] = Field(default=None)
        client_id: Optional[ID] = Field(alias="clientId", default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for App"""

        document = "fragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment ListRelease on Release {\n  id\n  version\n  logo {\n    presignedUrl\n    __typename\n  }\n  app {\n    ...ListApp\n    __typename\n  }\n  __typename\n}\n\nfragment DetailApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  releases {\n    ...ListRelease\n    __typename\n  }\n  __typename\n}\n\nquery App($identifier: AppIdentifier, $id: ID, $clientId: ID) {\n  app(identifier: $identifier, id: $id, clientId: $clientId) {\n    ...DetailApp\n    __typename\n  }\n}"


class DetailAppQuery(BaseModel):
    """No documentation found for this operation."""

    app: DetailApp

    class Arguments(BaseModel):
        """Arguments for DetailApp"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DetailApp"""

        document = "fragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment ListRelease on Release {\n  id\n  version\n  logo {\n    presignedUrl\n    __typename\n  }\n  app {\n    ...ListApp\n    __typename\n  }\n  __typename\n}\n\nfragment DetailApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  releases {\n    ...ListRelease\n    __typename\n  }\n  __typename\n}\n\nquery DetailApp($id: ID!) {\n  app(id: $id) {\n    ...DetailApp\n    __typename\n  }\n}"


class ClientsQuery(BaseModel):
    """No documentation found for this operation."""

    clients: Tuple[ListClient, ...]

    class Arguments(BaseModel):
        """Arguments for Clients"""

        filters: Optional[ClientFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Clients"""

        document = "fragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery Clients($filters: ClientFilter, $pagination: OffsetPaginationInput) {\n  clients(filters: $filters, pagination: $pagination) {\n    ...ListClient\n    __typename\n  }\n}"


class DetailClientQuery(BaseModel):
    """No documentation found for this operation."""

    client: DetailClient

    class Arguments(BaseModel):
        """Arguments for DetailClient"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DetailClient"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListRelease on Release {\n  id\n  version\n  logo {\n    presignedUrl\n    __typename\n  }\n  app {\n    ...ListApp\n    __typename\n  }\n  __typename\n}\n\nfragment ListServiceInstanceMapping on ServiceInstanceMapping {\n  id\n  key\n  instance {\n    ...ListServiceInstance\n    __typename\n  }\n  client {\n    ...ListClient\n    __typename\n  }\n  optional\n  __typename\n}\n\nfragment DetailClient on Client {\n  id\n  token\n  name\n  user {\n    id\n    username\n    __typename\n  }\n  kind\n  release {\n    ...ListRelease\n    __typename\n  }\n  logo {\n    presignedUrl\n    __typename\n  }\n  oauth2Client {\n    clientId\n    __typename\n  }\n  mappings {\n    ...ListServiceInstanceMapping\n    __typename\n  }\n  __typename\n}\n\nquery DetailClient($id: ID!) {\n  client(id: $id) {\n    ...DetailClient\n    __typename\n  }\n}"


class MyManagedClientsQuery(BaseModel):
    """No documentation found for this operation."""

    my_managed_clients: ListClient = Field(alias="myManagedClients")

    class Arguments(BaseModel):
        """Arguments for MyManagedClients"""

        kind: ClientKind
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for MyManagedClients"""

        document = "fragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery MyManagedClients($kind: ClientKind!) {\n  myManagedClients(kind: $kind) {\n    ...ListClient\n    __typename\n  }\n}"


class ClientQuery(BaseModel):
    """No documentation found for this operation."""

    client: DetailClient

    class Arguments(BaseModel):
        """Arguments for Client"""

        client_id: ID = Field(alias="clientId")
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Client"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment ListApp on App {\n  id\n  identifier\n  logo {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment ListServiceInstance on ServiceInstance {\n  id\n  identifier\n  allowedUsers {\n    ...ListUser\n    __typename\n  }\n  deniedUsers {\n    ...ListUser\n    __typename\n  }\n  __typename\n}\n\nfragment ListClient on Client {\n  id\n  user {\n    id\n    username\n    __typename\n  }\n  name\n  kind\n  release {\n    version\n    logo {\n      presignedUrl\n      __typename\n    }\n    app {\n      id\n      identifier\n      logo {\n        presignedUrl\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment ListRelease on Release {\n  id\n  version\n  logo {\n    presignedUrl\n    __typename\n  }\n  app {\n    ...ListApp\n    __typename\n  }\n  __typename\n}\n\nfragment ListServiceInstanceMapping on ServiceInstanceMapping {\n  id\n  key\n  instance {\n    ...ListServiceInstance\n    __typename\n  }\n  client {\n    ...ListClient\n    __typename\n  }\n  optional\n  __typename\n}\n\nfragment DetailClient on Client {\n  id\n  token\n  name\n  user {\n    id\n    username\n    __typename\n  }\n  kind\n  release {\n    ...ListRelease\n    __typename\n  }\n  logo {\n    presignedUrl\n    __typename\n  }\n  oauth2Client {\n    clientId\n    __typename\n  }\n  mappings {\n    ...ListServiceInstanceMapping\n    __typename\n  }\n  __typename\n}\n\nquery Client($clientId: ID!) {\n  client(clientId: $clientId) {\n    ...DetailClient\n    __typename\n  }\n}"


class ScopesQueryScopes(BaseModel):
    """A scope that can be assigned to a client. Scopes are used to limit the access of a client to a user's data. They represent app-level permissions."""

    typename: Literal["Scope"] = Field(
        alias="__typename", default="Scope", exclude=True
    )
    description: str
    "The description of the scope. This is a human readable description of the scope."
    value: str
    "The value of the scope. This is the value that is used in the OAuth2 flow."
    label: str
    "The label of the scope. This is the human readable name of the scope."
    model_config = ConfigDict(frozen=True)


class ScopesQuery(BaseModel):
    """No documentation found for this operation."""

    scopes: Tuple[ScopesQueryScopes, ...]

    class Arguments(BaseModel):
        """Arguments for Scopes"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Scopes"""

        document = "query Scopes {\n  scopes {\n    description\n    value\n    label\n    __typename\n  }\n}"


class ScopesOptionsQueryOptions(BaseModel):
    """A scope that can be assigned to a client. Scopes are used to limit the access of a client to a user's data. They represent app-level permissions."""

    typename: Literal["Scope"] = Field(
        alias="__typename", default="Scope", exclude=True
    )
    value: str
    "The value of the scope. This is the value that is used in the OAuth2 flow."
    label: str
    "The label of the scope. This is the human readable name of the scope."
    model_config = ConfigDict(frozen=True)


class ScopesOptionsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[ScopesOptionsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for ScopesOptions"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for ScopesOptions"""

        document = "query ScopesOptions {\n  options: scopes {\n    value\n    label\n    __typename\n  }\n}"


class RedeemTokensQuery(BaseModel):
    """No documentation found for this operation."""

    redeem_tokens: Tuple[ListRedeemToken, ...] = Field(alias="redeemTokens")

    class Arguments(BaseModel):
        """Arguments for RedeemTokens"""

        filters: Optional[RedeemTokenFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for RedeemTokens"""

        document = "fragment ListRedeemToken on RedeemToken {\n  id\n  token\n  user {\n    id\n    email\n    __typename\n  }\n  client {\n    id\n    release {\n      version\n      app {\n        identifier\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery RedeemTokens($filters: RedeemTokenFilter, $pagination: OffsetPaginationInput) {\n  redeemTokens(filters: $filters, pagination: $pagination) {\n    ...ListRedeemToken\n    __typename\n  }\n}"


class GroupOptionsQueryOptions(BaseModel):
    """
    A Group is the base unit of Role Based Access Control. A Group can have many users and many permissions. A user can have many groups. A user with a group that has a permission can perform the action that the permission allows.
    Groups are propagated to the respecting subservices. Permissions are not. Each subservice has to define its own permissions and mappings to groups.
    """

    typename: Literal["Group"] = Field(
        alias="__typename", default="Group", exclude=True
    )
    value: ID
    label: str
    model_config = ConfigDict(frozen=True)


class GroupOptionsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[GroupOptionsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for GroupOptions"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for GroupOptions"""

        document = "query GroupOptions($search: String, $values: [ID!]) {\n  options: groups(filters: {search: $search, ids: $values}) {\n    value: id\n    label: name\n    __typename\n  }\n}"


class DetailGroupQuery(BaseModel):
    """No documentation found for this operation."""

    group: DetailGroup

    class Arguments(BaseModel):
        """Arguments for DetailGroup"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DetailGroup"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nfragment GroupProfile on GroupProfile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment DetailGroup on Group {\n  id\n  name\n  users {\n    ...ListUser\n    __typename\n  }\n  profile {\n    ...GroupProfile\n    __typename\n  }\n  __typename\n}\n\nquery DetailGroup($id: ID!) {\n  group(id: $id) {\n    ...DetailGroup\n    __typename\n  }\n}"


class GroupsQuery(BaseModel):
    """No documentation found for this operation."""

    groups: Tuple[ListGroup, ...]

    class Arguments(BaseModel):
        """Arguments for Groups"""

        filters: Optional[GroupFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Groups"""

        document = "fragment ListGroup on Group {\n  id\n  name\n  profile {\n    id\n    bio\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nquery Groups($filters: GroupFilter, $pagination: OffsetPaginationInput) {\n  groups(filters: $filters, pagination: $pagination) {\n    ...ListGroup\n    __typename\n  }\n}"


class MyStashesQuery(BaseModel):
    """No documentation found for this operation."""

    stashes: Tuple[ListStash, ...]

    class Arguments(BaseModel):
        """Arguments for MyStashes"""

        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for MyStashes"""

        document = "fragment Stash on Stash {\n  id\n  name\n  description\n  createdAt\n  updatedAt\n  owner {\n    id\n    username\n    __typename\n  }\n  __typename\n}\n\nfragment StashItem on StashItem {\n  id\n  identifier\n  object\n  __typename\n}\n\nfragment ListStash on Stash {\n  ...Stash\n  items {\n    ...StashItem\n    __typename\n  }\n  __typename\n}\n\nquery MyStashes($pagination: OffsetPaginationInput) {\n  stashes(pagination: $pagination) {\n    ...ListStash\n    __typename\n  }\n}"


class MeQuery(BaseModel):
    """No documentation found for this operation."""

    me: DetailUser

    class Arguments(BaseModel):
        """Arguments for Me"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Me"""

        document = "fragment Profile on Profile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment DetailUser on User {\n  id\n  username\n  email\n  firstName\n  lastName\n  avatar\n  groups {\n    id\n    name\n    __typename\n  }\n  profile {\n    ...Profile\n    __typename\n  }\n  __typename\n}\n\nquery Me {\n  me {\n    ...DetailUser\n    __typename\n  }\n}"


class UserQuery(BaseModel):
    """No documentation found for this operation."""

    user: DetailUser

    class Arguments(BaseModel):
        """Arguments for User"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for User"""

        document = "fragment Profile on Profile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment DetailUser on User {\n  id\n  username\n  email\n  firstName\n  lastName\n  avatar\n  groups {\n    id\n    name\n    __typename\n  }\n  profile {\n    ...Profile\n    __typename\n  }\n  __typename\n}\n\nquery User($id: ID!) {\n  user(id: $id) {\n    ...DetailUser\n    __typename\n  }\n}"


class DetailUserQuery(BaseModel):
    """No documentation found for this operation."""

    user: DetailUser

    class Arguments(BaseModel):
        """Arguments for DetailUser"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DetailUser"""

        document = "fragment Profile on Profile {\n  id\n  name\n  avatar {\n    presignedUrl\n    __typename\n  }\n  __typename\n}\n\nfragment DetailUser on User {\n  id\n  username\n  email\n  firstName\n  lastName\n  avatar\n  groups {\n    id\n    name\n    __typename\n  }\n  profile {\n    ...Profile\n    __typename\n  }\n  __typename\n}\n\nquery DetailUser($id: ID!) {\n  user(id: $id) {\n    ...DetailUser\n    __typename\n  }\n}"


class UsersQuery(BaseModel):
    """No documentation found for this operation."""

    users: Tuple[ListUser, ...]

    class Arguments(BaseModel):
        """Arguments for Users"""

        filters: Optional[UserFilter] = Field(default=None)
        pagination: Optional[OffsetPaginationInput] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Users"""

        document = "fragment ListUser on User {\n  username\n  firstName\n  lastName\n  email\n  avatar\n  id\n  __typename\n}\n\nquery Users($filters: UserFilter, $pagination: OffsetPaginationInput) {\n  users(filters: $filters, pagination: $pagination) {\n    ...ListUser\n    __typename\n  }\n}"


class UserOptionsQueryOptions(BaseModel):
    """
    A User is a person that can log in to the system. They are uniquely identified by their username.
    And can have an email address associated with them (but don't have to).

    A user can be assigned to groups and has a profile that can be used to display information about them.
    Detail information about a user can be found in the profile.

    All users can have social accounts associated with them. These are used to authenticate the user with external services,
    such as ORCID or GitHub.

    """

    typename: Literal["User"] = Field(alias="__typename", default="User", exclude=True)
    value: ID
    label: str
    "Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only."
    model_config = ConfigDict(frozen=True)


class UserOptionsQuery(BaseModel):
    """No documentation found for this operation."""

    options: Tuple[UserOptionsQueryOptions, ...]

    class Arguments(BaseModel):
        """Arguments for UserOptions"""

        search: Optional[str] = Field(default=None)
        values: Optional[List[ID]] = Field(default=None)
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for UserOptions"""

        document = "query UserOptions($search: String, $values: [ID!]) {\n  options: users(filters: {search: $search, ids: $values}) {\n    value: id\n    label: username\n    __typename\n  }\n}"


class ProfileQuery(BaseModel):
    """No documentation found for this operation."""

    me: MeUser

    class Arguments(BaseModel):
        """Arguments for Profile"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for Profile"""

        document = "fragment MeUser on User {\n  id\n  username\n  email\n  firstName\n  lastName\n  avatar\n  __typename\n}\n\nquery Profile {\n  me {\n    ...MeUser\n    __typename\n  }\n}"


class CommentsForQuery(BaseModel):
    """No documentation found for this operation."""

    comments_for: Tuple[ListComment, ...] = Field(alias="commentsFor")

    class Arguments(BaseModel):
        """Arguments for CommentsFor"""

        object: ID
        identifier: str
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for CommentsFor"""

        document = "fragment Leaf on LeafDescendant {\n  bold\n  italic\n  code\n  text\n  __typename\n}\n\nfragment Mention on MentionDescendant {\n  user {\n    ...CommentUser\n    __typename\n  }\n  __typename\n}\n\nfragment Paragraph on ParagraphDescendant {\n  size\n  __typename\n}\n\nfragment CommentUser on User {\n  id\n  username\n  avatar\n  profile {\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubthreadComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  createdAt\n  descendants {\n    ...Descendant\n    __typename\n  }\n  __typename\n}\n\nfragment Descendant on Descendant {\n  kind\n  children {\n    kind\n    children {\n      kind\n      unsafeChildren\n      ...Leaf\n      ...Mention\n      ...Paragraph\n      __typename\n    }\n    ...Leaf\n    ...Mention\n    ...Paragraph\n    __typename\n  }\n  ...Mention\n  ...Paragraph\n  ...Leaf\n  __typename\n}\n\nfragment ListComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  descendants {\n    ...Descendant\n    __typename\n  }\n  resolved\n  resolvedBy {\n    ...CommentUser\n    __typename\n  }\n  id\n  createdAt\n  children {\n    ...SubthreadComment\n    __typename\n  }\n  __typename\n}\n\nquery CommentsFor($object: ID!, $identifier: Identifier!) {\n  commentsFor(identifier: $identifier, object: $object) {\n    ...ListComment\n    __typename\n  }\n}"


class MyMentionsQuery(BaseModel):
    """No documentation found for this operation."""

    my_mentions: Tuple[MentionComment, ...] = Field(alias="myMentions")

    class Arguments(BaseModel):
        """Arguments for MyMentions"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for MyMentions"""

        document = "fragment Leaf on LeafDescendant {\n  bold\n  italic\n  code\n  text\n  __typename\n}\n\nfragment Mention on MentionDescendant {\n  user {\n    ...CommentUser\n    __typename\n  }\n  __typename\n}\n\nfragment Paragraph on ParagraphDescendant {\n  size\n  __typename\n}\n\nfragment CommentUser on User {\n  id\n  username\n  avatar\n  profile {\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubthreadComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  createdAt\n  descendants {\n    ...Descendant\n    __typename\n  }\n  __typename\n}\n\nfragment Descendant on Descendant {\n  kind\n  children {\n    kind\n    children {\n      kind\n      unsafeChildren\n      ...Leaf\n      ...Mention\n      ...Paragraph\n      __typename\n    }\n    ...Leaf\n    ...Mention\n    ...Paragraph\n    __typename\n  }\n  ...Mention\n  ...Paragraph\n  ...Leaf\n  __typename\n}\n\nfragment MentionComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  descendants {\n    ...Descendant\n    __typename\n  }\n  id\n  createdAt\n  children {\n    ...SubthreadComment\n    __typename\n  }\n  mentions {\n    ...CommentUser\n    __typename\n  }\n  resolved\n  resolvedBy {\n    ...CommentUser\n    __typename\n  }\n  object\n  identifier\n  __typename\n}\n\nquery MyMentions {\n  myMentions {\n    ...MentionComment\n    __typename\n  }\n}"


class DetailCommentQuery(BaseModel):
    """No documentation found for this operation."""

    comment: DetailComment

    class Arguments(BaseModel):
        """Arguments for DetailComment"""

        id: ID
        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for DetailComment"""

        document = "fragment Leaf on LeafDescendant {\n  bold\n  italic\n  code\n  text\n  __typename\n}\n\nfragment Mention on MentionDescendant {\n  user {\n    ...CommentUser\n    __typename\n  }\n  __typename\n}\n\nfragment Paragraph on ParagraphDescendant {\n  size\n  __typename\n}\n\nfragment CommentUser on User {\n  id\n  username\n  avatar\n  profile {\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubthreadComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  createdAt\n  descendants {\n    ...Descendant\n    __typename\n  }\n  __typename\n}\n\nfragment Descendant on Descendant {\n  kind\n  children {\n    kind\n    children {\n      kind\n      unsafeChildren\n      ...Leaf\n      ...Mention\n      ...Paragraph\n      __typename\n    }\n    ...Leaf\n    ...Mention\n    ...Paragraph\n    __typename\n  }\n  ...Mention\n  ...Paragraph\n  ...Leaf\n  __typename\n}\n\nfragment DetailComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  descendants {\n    ...Descendant\n    __typename\n  }\n  id\n  resolved\n  resolvedBy {\n    ...CommentUser\n    __typename\n  }\n  createdAt\n  children {\n    ...SubthreadComment\n    __typename\n  }\n  mentions {\n    ...CommentUser\n    __typename\n  }\n  object\n  identifier\n  __typename\n}\n\nquery DetailComment($id: ID!) {\n  comment(id: $id) {\n    ...DetailComment\n    __typename\n  }\n}"


class WatchMentionsSubscription(BaseModel):
    """No documentation found for this operation."""

    mentions: MentionComment

    class Arguments(BaseModel):
        """Arguments for WatchMentions"""

        model_config = ConfigDict(populate_by_name=True)

    class Meta:
        """Meta class for WatchMentions"""

        document = "fragment Leaf on LeafDescendant {\n  bold\n  italic\n  code\n  text\n  __typename\n}\n\nfragment Mention on MentionDescendant {\n  user {\n    ...CommentUser\n    __typename\n  }\n  __typename\n}\n\nfragment Paragraph on ParagraphDescendant {\n  size\n  __typename\n}\n\nfragment CommentUser on User {\n  id\n  username\n  avatar\n  profile {\n    avatar {\n      presignedUrl\n      __typename\n    }\n    __typename\n  }\n  __typename\n}\n\nfragment SubthreadComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  createdAt\n  descendants {\n    ...Descendant\n    __typename\n  }\n  __typename\n}\n\nfragment Descendant on Descendant {\n  kind\n  children {\n    kind\n    children {\n      kind\n      unsafeChildren\n      ...Leaf\n      ...Mention\n      ...Paragraph\n      __typename\n    }\n    ...Leaf\n    ...Mention\n    ...Paragraph\n    __typename\n  }\n  ...Mention\n  ...Paragraph\n  ...Leaf\n  __typename\n}\n\nfragment MentionComment on Comment {\n  user {\n    ...CommentUser\n    __typename\n  }\n  parent {\n    id\n    __typename\n  }\n  descendants {\n    ...Descendant\n    __typename\n  }\n  id\n  createdAt\n  children {\n    ...SubthreadComment\n    __typename\n  }\n  mentions {\n    ...CommentUser\n    __typename\n  }\n  resolved\n  resolvedBy {\n    ...CommentUser\n    __typename\n  }\n  object\n  identifier\n  __typename\n}\n\nsubscription WatchMentions {\n  mentions {\n    ...MentionComment\n    __typename\n  }\n}"


async def aupdate_service_instance(
    id: ID,
    allowed_users: Optional[Iterable[ID]] = None,
    allowed_groups: Optional[Iterable[ID]] = None,
    denied_groups: Optional[Iterable[ID]] = None,
    denied_users: Optional[Iterable[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> ServiceInstance:
    """UpdateServiceInstance


    Args:
        allowed_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        allowed_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ServiceInstance
    """
    return (
        await aexecute(
            UpdateServiceInstanceMutation,
            {
                "input": {
                    "allowedUsers": allowed_users,
                    "allowedGroups": allowed_groups,
                    "deniedGroups": denied_groups,
                    "deniedUsers": denied_users,
                    "id": id,
                }
            },
            rath=rath,
        )
    ).update_service_instance


def update_service_instance(
    id: ID,
    allowed_users: Optional[Iterable[ID]] = None,
    allowed_groups: Optional[Iterable[ID]] = None,
    denied_groups: Optional[Iterable[ID]] = None,
    denied_users: Optional[Iterable[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> ServiceInstance:
    """UpdateServiceInstance


    Args:
        allowed_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        allowed_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ServiceInstance
    """
    return execute(
        UpdateServiceInstanceMutation,
        {
            "input": {
                "allowedUsers": allowed_users,
                "allowedGroups": allowed_groups,
                "deniedGroups": denied_groups,
                "deniedUsers": denied_users,
                "id": id,
            }
        },
        rath=rath,
    ).update_service_instance


async def acreate_service_instance(
    identifier: str,
    service: ID,
    allowed_users: Optional[Iterable[ID]] = None,
    allowed_groups: Optional[Iterable[ID]] = None,
    denied_groups: Optional[Iterable[ID]] = None,
    denied_users: Optional[Iterable[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> ServiceInstance:
    """CreateServiceInstance


    Args:
        identifier: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        service: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        allowed_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        allowed_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ServiceInstance
    """
    return (
        await aexecute(
            CreateServiceInstanceMutation,
            {
                "input": {
                    "identifier": identifier,
                    "service": service,
                    "allowedUsers": allowed_users,
                    "allowedGroups": allowed_groups,
                    "deniedGroups": denied_groups,
                    "deniedUsers": denied_users,
                }
            },
            rath=rath,
        )
    ).create_service_instance


def create_service_instance(
    identifier: str,
    service: ID,
    allowed_users: Optional[Iterable[ID]] = None,
    allowed_groups: Optional[Iterable[ID]] = None,
    denied_groups: Optional[Iterable[ID]] = None,
    denied_users: Optional[Iterable[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> ServiceInstance:
    """CreateServiceInstance


    Args:
        identifier: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        service: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        allowed_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        allowed_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_groups: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        denied_users: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required) (list)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ServiceInstance
    """
    return execute(
        CreateServiceInstanceMutation,
        {
            "input": {
                "identifier": identifier,
                "service": service,
                "allowedUsers": allowed_users,
                "allowedGroups": allowed_groups,
                "deniedGroups": denied_groups,
                "deniedUsers": denied_users,
            }
        },
        rath=rath,
    ).create_service_instance


async def arequest_media_upload(
    key: str, datalayer: str, rath: Optional[UnlokRath] = None
) -> PresignedPostCredentials:
    """RequestMediaUpload


    Args:
        key (str): No description
        datalayer (str): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PresignedPostCredentials
    """
    return (
        await aexecute(
            RequestMediaUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
        )
    ).request_media_upload


def request_media_upload(
    key: str, datalayer: str, rath: Optional[UnlokRath] = None
) -> PresignedPostCredentials:
    """RequestMediaUpload


    Args:
        key (str): No description
        datalayer (str): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        PresignedPostCredentials
    """
    return execute(
        RequestMediaUploadMutation, {"key": key, "datalayer": datalayer}, rath=rath
    ).request_media_upload


async def acreate_comment(
    object: ID,
    identifier: str,
    descendants: List[DescendantInput],
    parent: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> ListComment:
    """CreateComment


    Args:
        object (ID): No description
        identifier (str): No description
        descendants (List[DescendantInput]): No description
        parent (Optional[ID], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListComment
    """
    return (
        await aexecute(
            CreateCommentMutation,
            {
                "object": object,
                "identifier": identifier,
                "descendants": descendants,
                "parent": parent,
            },
            rath=rath,
        )
    ).create_comment


def create_comment(
    object: ID,
    identifier: str,
    descendants: List[DescendantInput],
    parent: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> ListComment:
    """CreateComment


    Args:
        object (ID): No description
        identifier (str): No description
        descendants (List[DescendantInput]): No description
        parent (Optional[ID], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListComment
    """
    return execute(
        CreateCommentMutation,
        {
            "object": object,
            "identifier": identifier,
            "descendants": descendants,
            "parent": parent,
        },
        rath=rath,
    ).create_comment


async def areply_to(
    descendants: List[DescendantInput], parent: ID, rath: Optional[UnlokRath] = None
) -> ListComment:
    """ReplyTo


    Args:
        descendants (List[DescendantInput]): No description
        parent (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListComment
    """
    return (
        await aexecute(
            ReplyToMutation, {"descendants": descendants, "parent": parent}, rath=rath
        )
    ).reply_to


def reply_to(
    descendants: List[DescendantInput], parent: ID, rath: Optional[UnlokRath] = None
) -> ListComment:
    """ReplyTo


    Args:
        descendants (List[DescendantInput]): No description
        parent (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListComment
    """
    return execute(
        ReplyToMutation, {"descendants": descendants, "parent": parent}, rath=rath
    ).reply_to


async def aresolve_comment(id: ID, rath: Optional[UnlokRath] = None) -> ListComment:
    """ResolveComment


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListComment
    """
    return (
        await aexecute(ResolveCommentMutation, {"id": id}, rath=rath)
    ).resolve_comment


def resolve_comment(id: ID, rath: Optional[UnlokRath] = None) -> ListComment:
    """ResolveComment


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListComment
    """
    return execute(ResolveCommentMutation, {"id": id}, rath=rath).resolve_comment


async def acreate_client(
    identifier: str,
    version: str,
    scopes: List[str],
    logo: Optional[str] = None,
    rath: Optional[UnlokRath] = None,
) -> CreateClientMutationCreatedevelopmentalclient:
    """CreateClient


    Args:
        identifier (str): No description
        version (str): No description
        scopes (List[str]): No description
        logo (Optional[str], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateClientMutationCreatedevelopmentalclient
    """
    return (
        await aexecute(
            CreateClientMutation,
            {
                "identifier": identifier,
                "version": version,
                "scopes": scopes,
                "logo": logo,
            },
            rath=rath,
        )
    ).create_developmental_client


def create_client(
    identifier: str,
    version: str,
    scopes: List[str],
    logo: Optional[str] = None,
    rath: Optional[UnlokRath] = None,
) -> CreateClientMutationCreatedevelopmentalclient:
    """CreateClient


    Args:
        identifier (str): No description
        version (str): No description
        scopes (List[str]): No description
        logo (Optional[str], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        CreateClientMutationCreatedevelopmentalclient
    """
    return execute(
        CreateClientMutation,
        {"identifier": identifier, "version": version, "scopes": scopes, "logo": logo},
        rath=rath,
    ).create_developmental_client


async def acreate_group_profile(
    group: ID, name: str, avatar: ID, rath: Optional[UnlokRath] = None
) -> GroupProfile:
    """CreateGroupProfile


    Args:
        group: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        avatar: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GroupProfile
    """
    return (
        await aexecute(
            CreateGroupProfileMutation,
            {"input": {"group": group, "name": name, "avatar": avatar}},
            rath=rath,
        )
    ).create_group_profile


def create_group_profile(
    group: ID, name: str, avatar: ID, rath: Optional[UnlokRath] = None
) -> GroupProfile:
    """CreateGroupProfile


    Args:
        group: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        avatar: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GroupProfile
    """
    return execute(
        CreateGroupProfileMutation,
        {"input": {"group": group, "name": name, "avatar": avatar}},
        rath=rath,
    ).create_group_profile


async def aupdate_group_profile(
    id: ID, name: str, avatar: ID, rath: Optional[UnlokRath] = None
) -> GroupProfile:
    """UpdateGroupProfile


    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        avatar: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GroupProfile
    """
    return (
        await aexecute(
            UpdateGroupProfileMutation,
            {"input": {"id": id, "name": name, "avatar": avatar}},
            rath=rath,
        )
    ).update_group_profile


def update_group_profile(
    id: ID, name: str, avatar: ID, rath: Optional[UnlokRath] = None
) -> GroupProfile:
    """UpdateGroupProfile


    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        avatar: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GroupProfile
    """
    return execute(
        UpdateGroupProfileMutation,
        {"input": {"id": id, "name": name, "avatar": avatar}},
        rath=rath,
    ).update_group_profile


async def acreate_user_profile(
    user: ID, name: str, rath: Optional[UnlokRath] = None
) -> Profile:
    """CreateUserProfile


    Args:
        user: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Profile
    """
    return (
        await aexecute(
            CreateUserProfileMutation,
            {"input": {"user": user, "name": name}},
            rath=rath,
        )
    ).create_profile


def create_user_profile(
    user: ID, name: str, rath: Optional[UnlokRath] = None
) -> Profile:
    """CreateUserProfile


    Args:
        user: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Profile
    """
    return execute(
        CreateUserProfileMutation, {"input": {"user": user, "name": name}}, rath=rath
    ).create_profile


async def aupdate_user_profile(
    id: ID, name: str, avatar: ID, rath: Optional[UnlokRath] = None
) -> Profile:
    """UpdateUserProfile


    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        avatar: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Profile
    """
    return (
        await aexecute(
            UpdateUserProfileMutation,
            {"input": {"id": id, "name": name, "avatar": avatar}},
            rath=rath,
        )
    ).update_profile


def update_user_profile(
    id: ID, name: str, avatar: ID, rath: Optional[UnlokRath] = None
) -> Profile:
    """UpdateUserProfile


    Args:
        id: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        name: The `String` scalar type represents textual data, represented as UTF-8 character sequences. The String type is most often used by GraphQL to represent free-form human-readable text. (required)
        avatar: The `ID` scalar type represents a unique identifier, often used to refetch an object or as key for a cache. The ID type appears in a JSON response as a String; however, it is not intended to be human-readable. When expected as an input type, any string (such as `"4"`) or integer (such as `4`) input value will be accepted as an ID. (required)
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Profile
    """
    return execute(
        UpdateUserProfileMutation,
        {"input": {"id": id, "name": name, "avatar": avatar}},
        rath=rath,
    ).update_profile


async def acreate_stash(
    name: Optional[str] = None,
    description: Optional[str] = "",
    rath: Optional[UnlokRath] = None,
) -> ListStash:
    """CreateStash

    Create a new stash

    Args:
        name (Optional[str], optional): No description.
        description (Optional[str], optional): No description. Defaults to
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListStash
    """
    return (
        await aexecute(
            CreateStashMutation, {"name": name, "description": description}, rath=rath
        )
    ).create_stash


def create_stash(
    name: Optional[str] = None,
    description: Optional[str] = "",
    rath: Optional[UnlokRath] = None,
) -> ListStash:
    """CreateStash

    Create a new stash

    Args:
        name (Optional[str], optional): No description.
        description (Optional[str], optional): No description. Defaults to
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListStash
    """
    return execute(
        CreateStashMutation, {"name": name, "description": description}, rath=rath
    ).create_stash


async def aadd_items_to_stash(
    stash: ID, items: List[StashItemInput], rath: Optional[UnlokRath] = None
) -> Tuple[StashItem, ...]:
    """AddItemsToStash

    Add items to a stash

    Args:
        stash (ID): No description
        items (List[StashItemInput]): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[StashItem]
    """
    return (
        await aexecute(
            AddItemsToStashMutation, {"stash": stash, "items": items}, rath=rath
        )
    ).add_items_to_stash


def add_items_to_stash(
    stash: ID, items: List[StashItemInput], rath: Optional[UnlokRath] = None
) -> Tuple[StashItem, ...]:
    """AddItemsToStash

    Add items to a stash

    Args:
        stash (ID): No description
        items (List[StashItemInput]): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[StashItem]
    """
    return execute(
        AddItemsToStashMutation, {"stash": stash, "items": items}, rath=rath
    ).add_items_to_stash


async def adelete_stash_items(
    items: List[ID], rath: Optional[UnlokRath] = None
) -> Tuple[ID, ...]:
    """DeleteStashItems

    Delete items from a stash

    Args:
        items (List[ID]): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ID]
    """
    return (
        await aexecute(DeleteStashItemsMutation, {"items": items}, rath=rath)
    ).delete_stash_items


def delete_stash_items(
    items: List[ID], rath: Optional[UnlokRath] = None
) -> Tuple[ID, ...]:
    """DeleteStashItems

    Delete items from a stash

    Args:
        items (List[ID]): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ID]
    """
    return execute(
        DeleteStashItemsMutation, {"items": items}, rath=rath
    ).delete_stash_items


async def adelete_stash(stash: ID, rath: Optional[UnlokRath] = None) -> ID:
    """DeleteStash


    Args:
        stash (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ID
    """
    return (
        await aexecute(DeleteStashMutation, {"stash": stash}, rath=rath)
    ).delete_stash


def delete_stash(stash: ID, rath: Optional[UnlokRath] = None) -> ID:
    """DeleteStash


    Args:
        stash (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ID
    """
    return execute(DeleteStashMutation, {"stash": stash}, rath=rath).delete_stash


async def alist_service_instances(
    pagination: Optional[OffsetPaginationInput] = None,
    filters: Optional[ServiceInstanceFilter] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListServiceInstance, ...]:
    """ListServiceInstances


    Args:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        filters (Optional[ServiceInstanceFilter], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListServiceInstance]
    """
    return (
        await aexecute(
            ListServiceInstancesQuery,
            {"pagination": pagination, "filters": filters},
            rath=rath,
        )
    ).service_instances


def list_service_instances(
    pagination: Optional[OffsetPaginationInput] = None,
    filters: Optional[ServiceInstanceFilter] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListServiceInstance, ...]:
    """ListServiceInstances


    Args:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        filters (Optional[ServiceInstanceFilter], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListServiceInstance]
    """
    return execute(
        ListServiceInstancesQuery,
        {"pagination": pagination, "filters": filters},
        rath=rath,
    ).service_instances


async def aget_service_instance(
    id: ID, rath: Optional[UnlokRath] = None
) -> ServiceInstance:
    """GetServiceInstance


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ServiceInstance
    """
    return (
        await aexecute(GetServiceInstanceQuery, {"id": id}, rath=rath)
    ).service_instance


def get_service_instance(id: ID, rath: Optional[UnlokRath] = None) -> ServiceInstance:
    """GetServiceInstance


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ServiceInstance
    """
    return execute(GetServiceInstanceQuery, {"id": id}, rath=rath).service_instance


async def alist_services(
    pagination: Optional[OffsetPaginationInput] = None,
    filters: Optional[ServiceFilter] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListService, ...]:
    """ListServices


    Args:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        filters (Optional[ServiceFilter], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListService]
    """
    return (
        await aexecute(
            ListServicesQuery, {"pagination": pagination, "filters": filters}, rath=rath
        )
    ).services


def list_services(
    pagination: Optional[OffsetPaginationInput] = None,
    filters: Optional[ServiceFilter] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListService, ...]:
    """ListServices


    Args:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        filters (Optional[ServiceFilter], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListService]
    """
    return execute(
        ListServicesQuery, {"pagination": pagination, "filters": filters}, rath=rath
    ).services


async def aget_service(id: ID, rath: Optional[UnlokRath] = None) -> Service:
    """GetService


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Service
    """
    return (await aexecute(GetServiceQuery, {"id": id}, rath=rath)).service


def get_service(id: ID, rath: Optional[UnlokRath] = None) -> Service:
    """GetService


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Service
    """
    return execute(GetServiceQuery, {"id": id}, rath=rath).service


async def areleases(rath: Optional[UnlokRath] = None) -> Tuple[ListRelease, ...]:
    """Releases


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListRelease]
    """
    return (await aexecute(ReleasesQuery, {}, rath=rath)).releases


def releases(rath: Optional[UnlokRath] = None) -> Tuple[ListRelease, ...]:
    """Releases


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListRelease]
    """
    return execute(ReleasesQuery, {}, rath=rath).releases


async def arelease(
    identifier: Optional[str] = None,
    version: Optional[str] = None,
    id: Optional[ID] = None,
    client_id: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> DetailRelease:
    """Release


    Args:
        identifier (Optional[str], optional): No description.
        version (Optional[str], optional): No description.
        id (Optional[ID], optional): No description.
        client_id (Optional[ID], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailRelease
    """
    return (
        await aexecute(
            ReleaseQuery,
            {
                "identifier": identifier,
                "version": version,
                "id": id,
                "clientId": client_id,
            },
            rath=rath,
        )
    ).release


def release(
    identifier: Optional[str] = None,
    version: Optional[str] = None,
    id: Optional[ID] = None,
    client_id: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> DetailRelease:
    """Release


    Args:
        identifier (Optional[str], optional): No description.
        version (Optional[str], optional): No description.
        id (Optional[ID], optional): No description.
        client_id (Optional[ID], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailRelease
    """
    return execute(
        ReleaseQuery,
        {"identifier": identifier, "version": version, "id": id, "clientId": client_id},
        rath=rath,
    ).release


async def adetail_release(id: ID, rath: Optional[UnlokRath] = None) -> DetailRelease:
    """DetailRelease


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailRelease
    """
    return (await aexecute(DetailReleaseQuery, {"id": id}, rath=rath)).release


def detail_release(id: ID, rath: Optional[UnlokRath] = None) -> DetailRelease:
    """DetailRelease


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailRelease
    """
    return execute(DetailReleaseQuery, {"id": id}, rath=rath).release


async def alayers(
    filters: Optional[LayerFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListLayer, ...]:
    """Layers


    Args:
        filters (Optional[LayerFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListLayer]
    """
    return (
        await aexecute(
            LayersQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).layers


def layers(
    filters: Optional[LayerFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListLayer, ...]:
    """Layers


    Args:
        filters (Optional[LayerFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListLayer]
    """
    return execute(
        LayersQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).layers


async def adetail_layer(id: ID, rath: Optional[UnlokRath] = None) -> Layer:
    """DetailLayer


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Layer
    """
    return (await aexecute(DetailLayerQuery, {"id": id}, rath=rath)).layer


def detail_layer(id: ID, rath: Optional[UnlokRath] = None) -> Layer:
    """DetailLayer


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        Layer
    """
    return execute(DetailLayerQuery, {"id": id}, rath=rath).layer


async def aglobal_search(
    no_users: bool,
    no_groups: bool,
    search: Optional[str] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> GlobalSearchQuery:
    """GlobalSearch


    Args:
        no_users (bool): No description
        no_groups (bool): No description
        search (Optional[str], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GlobalSearchQuery
    """
    return await aexecute(
        GlobalSearchQuery,
        {
            "search": search,
            "noUsers": no_users,
            "noGroups": no_groups,
            "pagination": pagination,
        },
        rath=rath,
    )


def global_search(
    no_users: bool,
    no_groups: bool,
    search: Optional[str] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> GlobalSearchQuery:
    """GlobalSearch


    Args:
        no_users (bool): No description
        no_groups (bool): No description
        search (Optional[str], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        GlobalSearchQuery
    """
    return execute(
        GlobalSearchQuery,
        {
            "search": search,
            "noUsers": no_users,
            "noGroups": no_groups,
            "pagination": pagination,
        },
        rath=rath,
    )


async def aapps(
    filters: Optional[AppFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListApp, ...]:
    """Apps


    Args:
        filters (Optional[AppFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListApp]
    """
    return (
        await aexecute(
            AppsQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).apps


def apps(
    filters: Optional[AppFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListApp, ...]:
    """Apps


    Args:
        filters (Optional[AppFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListApp]
    """
    return execute(
        AppsQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).apps


async def aapp(
    identifier: Optional[str] = None,
    id: Optional[ID] = None,
    client_id: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> DetailApp:
    """App


    Args:
        identifier (Optional[str], optional): No description.
        id (Optional[ID], optional): No description.
        client_id (Optional[ID], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailApp
    """
    return (
        await aexecute(
            AppQuery,
            {"identifier": identifier, "id": id, "clientId": client_id},
            rath=rath,
        )
    ).app


def app(
    identifier: Optional[str] = None,
    id: Optional[ID] = None,
    client_id: Optional[ID] = None,
    rath: Optional[UnlokRath] = None,
) -> DetailApp:
    """App


    Args:
        identifier (Optional[str], optional): No description.
        id (Optional[ID], optional): No description.
        client_id (Optional[ID], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailApp
    """
    return execute(
        AppQuery, {"identifier": identifier, "id": id, "clientId": client_id}, rath=rath
    ).app


async def adetail_app(id: ID, rath: Optional[UnlokRath] = None) -> DetailApp:
    """DetailApp


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailApp
    """
    return (await aexecute(DetailAppQuery, {"id": id}, rath=rath)).app


def detail_app(id: ID, rath: Optional[UnlokRath] = None) -> DetailApp:
    """DetailApp


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailApp
    """
    return execute(DetailAppQuery, {"id": id}, rath=rath).app


async def aclients(
    filters: Optional[ClientFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListClient, ...]:
    """Clients


    Args:
        filters (Optional[ClientFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListClient]
    """
    return (
        await aexecute(
            ClientsQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).clients


def clients(
    filters: Optional[ClientFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListClient, ...]:
    """Clients


    Args:
        filters (Optional[ClientFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListClient]
    """
    return execute(
        ClientsQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).clients


async def adetail_client(id: ID, rath: Optional[UnlokRath] = None) -> DetailClient:
    """DetailClient


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailClient
    """
    return (await aexecute(DetailClientQuery, {"id": id}, rath=rath)).client


def detail_client(id: ID, rath: Optional[UnlokRath] = None) -> DetailClient:
    """DetailClient


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailClient
    """
    return execute(DetailClientQuery, {"id": id}, rath=rath).client


async def amy_managed_clients(
    kind: ClientKind, rath: Optional[UnlokRath] = None
) -> ListClient:
    """MyManagedClients


    Args:
        kind (ClientKind): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListClient
    """
    return (
        await aexecute(MyManagedClientsQuery, {"kind": kind}, rath=rath)
    ).my_managed_clients


def my_managed_clients(
    kind: ClientKind, rath: Optional[UnlokRath] = None
) -> ListClient:
    """MyManagedClients


    Args:
        kind (ClientKind): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        ListClient
    """
    return execute(MyManagedClientsQuery, {"kind": kind}, rath=rath).my_managed_clients


async def aclient(client_id: ID, rath: Optional[UnlokRath] = None) -> DetailClient:
    """Client


    Args:
        client_id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailClient
    """
    return (await aexecute(ClientQuery, {"clientId": client_id}, rath=rath)).client


def client(client_id: ID, rath: Optional[UnlokRath] = None) -> DetailClient:
    """Client


    Args:
        client_id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailClient
    """
    return execute(ClientQuery, {"clientId": client_id}, rath=rath).client


async def ascopes(rath: Optional[UnlokRath] = None) -> Tuple[ScopesQueryScopes, ...]:
    """Scopes


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ScopesQueryScopes]
    """
    return (await aexecute(ScopesQuery, {}, rath=rath)).scopes


def scopes(rath: Optional[UnlokRath] = None) -> Tuple[ScopesQueryScopes, ...]:
    """Scopes


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ScopesQueryScopes]
    """
    return execute(ScopesQuery, {}, rath=rath).scopes


async def ascopes_options(
    rath: Optional[UnlokRath] = None,
) -> Tuple[ScopesOptionsQueryOptions, ...]:
    """ScopesOptions


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ScopesOptionsQueryScopes]
    """
    return (await aexecute(ScopesOptionsQuery, {}, rath=rath)).options


def scopes_options(
    rath: Optional[UnlokRath] = None,
) -> Tuple[ScopesOptionsQueryOptions, ...]:
    """ScopesOptions


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ScopesOptionsQueryScopes]
    """
    return execute(ScopesOptionsQuery, {}, rath=rath).options


async def aredeem_tokens(
    filters: Optional[RedeemTokenFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListRedeemToken, ...]:
    """RedeemTokens


    Args:
        filters (Optional[RedeemTokenFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListRedeemToken]
    """
    return (
        await aexecute(
            RedeemTokensQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).redeem_tokens


def redeem_tokens(
    filters: Optional[RedeemTokenFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListRedeemToken, ...]:
    """RedeemTokens


    Args:
        filters (Optional[RedeemTokenFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListRedeemToken]
    """
    return execute(
        RedeemTokensQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).redeem_tokens


async def agroup_options(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[GroupOptionsQueryOptions, ...]:
    """GroupOptions


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[GroupOptionsQueryGroups]
    """
    return (
        await aexecute(
            GroupOptionsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def group_options(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[GroupOptionsQueryOptions, ...]:
    """GroupOptions


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[GroupOptionsQueryGroups]
    """
    return execute(
        GroupOptionsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def adetail_group(id: ID, rath: Optional[UnlokRath] = None) -> DetailGroup:
    """DetailGroup


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailGroup
    """
    return (await aexecute(DetailGroupQuery, {"id": id}, rath=rath)).group


def detail_group(id: ID, rath: Optional[UnlokRath] = None) -> DetailGroup:
    """DetailGroup


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailGroup
    """
    return execute(DetailGroupQuery, {"id": id}, rath=rath).group


async def agroups(
    filters: Optional[GroupFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListGroup, ...]:
    """Groups


    Args:
        filters (Optional[GroupFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListGroup]
    """
    return (
        await aexecute(
            GroupsQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).groups


def groups(
    filters: Optional[GroupFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListGroup, ...]:
    """Groups


    Args:
        filters (Optional[GroupFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListGroup]
    """
    return execute(
        GroupsQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).groups


async def amy_stashes(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[UnlokRath] = None
) -> Tuple[ListStash, ...]:
    """MyStashes


    Args:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListStash]
    """
    return (
        await aexecute(MyStashesQuery, {"pagination": pagination}, rath=rath)
    ).stashes


def my_stashes(
    pagination: Optional[OffsetPaginationInput] = None, rath: Optional[UnlokRath] = None
) -> Tuple[ListStash, ...]:
    """MyStashes


    Args:
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListStash]
    """
    return execute(MyStashesQuery, {"pagination": pagination}, rath=rath).stashes


async def ame(rath: Optional[UnlokRath] = None) -> DetailUser:
    """Me


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailUser
    """
    return (await aexecute(MeQuery, {}, rath=rath)).me


def me(rath: Optional[UnlokRath] = None) -> DetailUser:
    """Me


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailUser
    """
    return execute(MeQuery, {}, rath=rath).me


async def auser(id: ID, rath: Optional[UnlokRath] = None) -> DetailUser:
    """User


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailUser
    """
    return (await aexecute(UserQuery, {"id": id}, rath=rath)).user


def user(id: ID, rath: Optional[UnlokRath] = None) -> DetailUser:
    """User


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailUser
    """
    return execute(UserQuery, {"id": id}, rath=rath).user


async def adetail_user(id: ID, rath: Optional[UnlokRath] = None) -> DetailUser:
    """DetailUser


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailUser
    """
    return (await aexecute(DetailUserQuery, {"id": id}, rath=rath)).user


def detail_user(id: ID, rath: Optional[UnlokRath] = None) -> DetailUser:
    """DetailUser


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailUser
    """
    return execute(DetailUserQuery, {"id": id}, rath=rath).user


async def ausers(
    filters: Optional[UserFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListUser, ...]:
    """Users


    Args:
        filters (Optional[UserFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListUser]
    """
    return (
        await aexecute(
            UsersQuery, {"filters": filters, "pagination": pagination}, rath=rath
        )
    ).users


def users(
    filters: Optional[UserFilter] = None,
    pagination: Optional[OffsetPaginationInput] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[ListUser, ...]:
    """Users


    Args:
        filters (Optional[UserFilter], optional): No description.
        pagination (Optional[OffsetPaginationInput], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListUser]
    """
    return execute(
        UsersQuery, {"filters": filters, "pagination": pagination}, rath=rath
    ).users


async def auser_options(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[UserOptionsQueryOptions, ...]:
    """UserOptions


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[UserOptionsQueryUsers]
    """
    return (
        await aexecute(
            UserOptionsQuery, {"search": search, "values": values}, rath=rath
        )
    ).options


def user_options(
    search: Optional[str] = None,
    values: Optional[List[ID]] = None,
    rath: Optional[UnlokRath] = None,
) -> Tuple[UserOptionsQueryOptions, ...]:
    """UserOptions


    Args:
        search (Optional[str], optional): No description.
        values (Optional[List[ID]], optional): No description.
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[UserOptionsQueryUsers]
    """
    return execute(
        UserOptionsQuery, {"search": search, "values": values}, rath=rath
    ).options


async def aprofile(rath: Optional[UnlokRath] = None) -> MeUser:
    """Profile


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MeUser
    """
    return (await aexecute(ProfileQuery, {}, rath=rath)).me


def profile(rath: Optional[UnlokRath] = None) -> MeUser:
    """Profile


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MeUser
    """
    return execute(ProfileQuery, {}, rath=rath).me


async def acomments_for(
    object: ID, identifier: str, rath: Optional[UnlokRath] = None
) -> Tuple[ListComment, ...]:
    """CommentsFor


    Args:
        object (ID): No description
        identifier (str): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListComment]
    """
    return (
        await aexecute(
            CommentsForQuery, {"object": object, "identifier": identifier}, rath=rath
        )
    ).comments_for


def comments_for(
    object: ID, identifier: str, rath: Optional[UnlokRath] = None
) -> Tuple[ListComment, ...]:
    """CommentsFor


    Args:
        object (ID): No description
        identifier (str): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[ListComment]
    """
    return execute(
        CommentsForQuery, {"object": object, "identifier": identifier}, rath=rath
    ).comments_for


async def amy_mentions(rath: Optional[UnlokRath] = None) -> Tuple[MentionComment, ...]:
    """MyMentions


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[MentionComment]
    """
    return (await aexecute(MyMentionsQuery, {}, rath=rath)).my_mentions


def my_mentions(rath: Optional[UnlokRath] = None) -> Tuple[MentionComment, ...]:
    """MyMentions


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        List[MentionComment]
    """
    return execute(MyMentionsQuery, {}, rath=rath).my_mentions


async def adetail_comment(id: ID, rath: Optional[UnlokRath] = None) -> DetailComment:
    """DetailComment


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailComment
    """
    return (await aexecute(DetailCommentQuery, {"id": id}, rath=rath)).comment


def detail_comment(id: ID, rath: Optional[UnlokRath] = None) -> DetailComment:
    """DetailComment


    Args:
        id (ID): No description
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        DetailComment
    """
    return execute(DetailCommentQuery, {"id": id}, rath=rath).comment


async def awatch_mentions(
    rath: Optional[UnlokRath] = None,
) -> AsyncIterator[MentionComment]:
    """WatchMentions


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MentionComment
    """
    async for event in asubscribe(WatchMentionsSubscription, {}, rath=rath):
        yield event.mentions


def watch_mentions(rath: Optional[UnlokRath] = None) -> Iterator[MentionComment]:
    """WatchMentions


    Args:
        rath (unlok_next.rath.UnlokRath, optional): The client we want to use (defaults to the currently active client)

    Returns:
        MentionComment
    """
    for event in subscribe(WatchMentionsSubscription, {}, rath=rath):
        yield event.mentions


AppFilter.model_rebuild()
ClientFilter.model_rebuild()
DescendantInput.model_rebuild()
GroupFilter.model_rebuild()
LayerFilter.model_rebuild()
RedeemTokenFilter.model_rebuild()
ServiceFilter.model_rebuild()
ServiceInstanceFilter.model_rebuild()
UserFilter.model_rebuild()
