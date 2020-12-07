WITH series AS (SELECT * from generate_series(1,10)),
     new_user AS (INSERT INTO user_profile_user
                   (
                     password,
                     is_superuser,
                     username,
                     email,
                     firstname,
                     lastname,
                     patronymic,
                     birth_date,
                     is_active,
                     is_admin,
                     avatar,
                     email_confirmed,
                     is_staff,
                     avatar_size
                   )
                   SELECT
                     'password_value',
                     True,
                     uuid_generate_v1(),
                     uuid_generate_v1() || 'email',
                     'firstname_value',
                     'lastname_value',
                     'patronymic_value',
                     '01.04.2014',
                     True,
                     False,
                     'avatar_value',
                     True,
                     False,
                     100
                   )

SELECT '1';
