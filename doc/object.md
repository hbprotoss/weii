**以下所有字段若无特殊说明均为string类型**

-----

# Tweet Object

|字段            | 说明                                             |
|----------------|--------------------------------------------------|
|created_at      | int, 微博创建时间，距1970-1-1 00:00:00秒数       |
|id              | 微博ID                                           |
|text            | 微博正文                                         |
|source          | 微博来源                                         |
|thumbnail_pic   | 缩略图片地址，没有时不返回此字段                 |
|original_pic    | 原始图片地址，没有时不返回此字段                 |
|user            | User Object                                      |
|retweeted_status| Tweet Object, 被转发的原微博信息字段，当该微博为转发微博时返回 |
|reposts_count   | int, 转发数                                      |
|comments_count  | int, 评论数                                      |

-----

# User Object

|字段            | 说明                                             |
|----------------|--------------------------------------------------|
|created_at      | int, 用户创建时间，距1970-1-1 00:00:00秒数       |
|id              | 用户ID                                           |
|screen_name     | 用户昵称                                         |
|location        | 用户所在地                                       |
|description     | 用户描述                                         |
|url             | 用户主页                                         |
|gender          | 性别，m：男、f：女、n：未知                      |
|followers_count | int, 粉丝数                                      |
|friends_count   | int, 关注数                                      |
|statuses_count  | int, 微博数                                      |
|avatar_large    | 大头像url                                        |
|follow_me       | bool, 该用户是否关注当前登录用户，true：是，false：否  |

-----

# Comment Object

|字段            | 说明                                             |
|----------------|--------------------------------------------------|
|created_at      | int, 评论创建时间，距1970-1-1 00:00:00秒数       |
|id              | 评论ID                                           |
|text            | 评论正文                                         |
|user            | User Object                                      |
|status          | Tweet Object, 评论的微博信息字段                 |
|reply_comment   | Comment Object, 评论来源评论，当本评论属于对另一评论的回复时返回此字段|

-----

# Unreads Object

|字段      | 说明           |
|----------|----------------|
|tweet     | 未读微博数     |
|mention   | 未读@数        |
|comment   | 未读评论数     |
|follower  | 新粉丝数       |
|private   | 未读私信数     |