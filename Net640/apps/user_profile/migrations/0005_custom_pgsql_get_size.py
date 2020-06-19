from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('user_profile', '0004_user_avatar_size'),
    ]

    operations = [
        migrations.RunSQL(sql="""
        CREATE OR REPLACE FUNCTION total_used_space(_user_id integer) RETURNS TABLE (page_sum bigint) AS $$
            BEGIN
            RETURN QUERY
                   WITH

                   posts AS (
                     SELECT (COALESCE(sum(octet_length(concat(t.id, t.content, t.date, t.image, t.user_id, t.image_size))), 0)
                                          + COALESCE(sum(t.image_size), 0)) AS sum
                     FROM user_posts_post AS t
                                  WHERE t.user_id=_user_id),

                   posts_likes AS (
                                SELECT COALESCE(sum(octet_length(concat(t.id, t.post_id, t.user_id))), 0) sum
                     FROM user_posts_post_likes AS t WHERE t.user_id=_user_id),

                   chat_message AS (
                               SELECT COALESCE(sum(octet_length(concat(t.id, t.chat_room, t.content, t.timestamp, t.author_id))), 0) sum
                    FROM chat_message AS t
                                WHERE t.author_id=_user_id),

                   images_info AS (
                                SELECT (COALESCE(sum(octet_length(concat(t.id, t.description, t.image, t.uploaded_at, t.user_id, t.image_size))), 0)
                             + COALESCE(sum(t.image_size), 0)) AS sum
                     FROM images_image AS t
                                  WHERE t.user_id=_user_id),

                   images_likes AS (
                                SELECT COALESCE(sum(octet_length(concat(t.id, t.image_id, t.user_id))), 0) sum
                     FROM images_image_likes AS t WHERE t.user_id=_user_id)

                   SELECT posts.sum + posts_likes.sum + chat_message.sum + images_info.sum + images_likes.sum
                                     + uprofile.avatar_size
                          + octet_length(concat(
                                uprofile.id,
                                uprofile.password,
                                uprofile.last_login,
                                uprofile.is_superuser,
                                uprofile.username,
                                uprofile.email,
                                uprofile.firstname,
                                uprofile.lastname,
                                uprofile.patronymic,
                                uprofile.birth_date,
                                uprofile.is_active,
                                uprofile.is_admin,
                                uprofile.avatar,
                                uprofile.email_confirmed,
                                uprofile.is_staff,
                                uprofile.avatar_size))
                   FROM posts, posts_likes, chat_message, images_info, images_likes, user_profile_user AS uprofile
                              WHERE uprofile.id = _user_id;
    END;
    $$ LANGUAGE plpgsql;""", reverse_sql="DROP FUNCTION IF EXISTS total_used_space;"),
    ]
