INSERT INTO user
    (username, password, email, status)
VALUES
    ('test', 'pbkdf2:sha256:50000$TCI4GzcX$0de171a4f4dac32e3364c7ddc7c14f3e2fa61f2d17574483f7ffbb431b4acb2f', 'test@baby.com', 1),
    ('other', 'pbkdf2:sha256:50000$kJPKsz6N$d2d4784f1b030a9761f5ccaeeaca413f27f2ecb76d6168407af962ddce849f79', 'other@baby.com', 0);

INSERT INTO category
    (name)
VALUES
    ('html');


INSERT INTO post
    (title, body, the_date, author_id, created)
VALUES
    ('test title', 'test' || x'0a' || 'body', '2018-01-01', 1, '2018-01-01 00:00:00');

INSERT INTO post_category
    (post_id, category_id)
VALUES
    (1, 1);