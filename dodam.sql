-- users
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY, --다른 DB와의 호환성 고려
    password VARCHAR(20),
    name VARCHAR(20),
    nickname VARCHAR(100),
    age INT,
    gender VARCHAR(10),
    phone VARCHAR(20) unique, -- String 형식이 안전, 010-1234-5678 형식으로 들어가서
    OAuth VARCHAR(20) CHECK (OAuth IN ('google','naver','kakao')),
    role VARCHAR(20) CHECK (role IN ('student','parent','admin')),
    email VARCHAR(255) UNIQUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- tests
CREATE TABLE IF NOT EXISTS tests (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    test_type VARCHAR(20) CHECK (test_type IN ('literacy','vocabulary')),
    test_date TIMESTAMP,
    duration INT,
    level INT,
    score INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_tests_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
        ON UPDATE CASCADE
);
-- answers
CREATE TABLE IF NOT EXISTS answers (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    question_id INT,
    answer TEXT,
    is_correct BOOLEAN,
    response_time INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- questions
CREATE TABLE IF NOT EXISTS questions (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    content TEXT,
    test_id INT,
    answers_id INT,
    test_type VARCHAR(20) CHECK (test_type IN ('literacy','vocabulary','game')),
    level INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_answers_test FOREIGN KEY (test_id)
        REFERENCES tests(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_answers_question FOREIGN KEY (answers_id)
        REFERENCES answers(id)
        ON DELETE CASCADE
);

-- recommendations
CREATE TABLE IF NOT EXISTS recommendations (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    content_type VARCHAR(20) CHECK (content_type IN ('book','game','exercise')),
    content_id INT,
    level INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_recommendations_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- activities
CREATE TABLE IF NOT EXISTS activities (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    activity_type VARCHAR(30) CHECK (activity_type IN ('reading_log','writing','vocabulary_search','game')),
    title VARCHAR(255),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_activities_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- community_posts
CREATE TABLE IF NOT EXISTS community_posts (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    community_type VARCHAR(20) CHECK (community_type IN ('student_forum','parent_forum')),
    title VARCHAR(255),
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_community_posts_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- subscriptions
CREATE TABLE IF NOT EXISTS subscriptions (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    plan_name VARCHAR(50),
    status VARCHAR(20) CHECK (status IN ('active','expired','canceled')),
    start_date TIMESTAMP,
    end_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_subscriptions_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- dashboards
CREATE TABLE IF NOT EXISTS dashboards (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    literacy_level INT,
    vocabulary_level INT,
    progress_json JSONB, --
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_dashboards_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- chatbot_conversations
CREATE TABLE IF NOT EXISTS chatbot_conversations (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT, --이건 구현할 AI의 반환 데이터 형식에 따라 바뀔 수 있습니다. 맞출 필요는 없습니다.
    message TEXT,
    response TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_chatbot_conversations_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- follows
CREATE TABLE IF NOT EXISTS follows (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    following_user_id INT,
    followed_user_id INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    PRIMARY KEY (following_user_id, followed_user_id),
    CONSTRAINT fk_follows_following FOREIGN KEY (following_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_follows_followed FOREIGN KEY (followed_user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- posts
CREATE TABLE IF NOT EXISTS posts (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    title VARCHAR(255),
    body TEXT,
    user_id INT,
    status VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_posts_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- 고객센터 문의
CREATE TABLE IF NOT EXISTS customer_support (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    user_id INT,
    category VARCHAR(50),
    title VARCHAR(255),
    content TEXT,
    status VARCHAR(20) CHECK (status IN ('open','in_progress','resolved','closed')),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_customer_support_user FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- 고객센터 답변
CREATE TABLE IF NOT EXISTS customer_support_response (
    id INT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    support_id INT,
    responder_id INT,
    content TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    CONSTRAINT fk_customer_support_response_support FOREIGN KEY (support_id)
        REFERENCES customer_support(id)
        ON DELETE CASCADE,
    CONSTRAINT fk_customer_support_response_responder FOREIGN KEY (responder_id)
        REFERENCES users(id)
        ON DELETE SET NULL
);

-- 학부모용 대시보드 뷰
CREATE OR REPLACE VIEW parent_dashboard_summary AS
WITH student_percentile AS (
    SELECT
        d.user_id AS student_id,
        d.literacy_level,
        d.vocabulary_level,
        PERCENT_RANK() OVER (ORDER BY d.literacy_level DESC) AS literacy_percentile,
        PERCENT_RANK() OVER (ORDER BY d.vocabulary_level DESC) AS vocabulary_percentile
    FROM dashboards d
),
student_progress AS (
    SELECT
        u.id AS student_id,
        COUNT(DISTINCT a.id) AS activity_count,
        COUNT(DISTINCT t.id) AS tests_taken,
        LEAST(ROUND(((COUNT(DISTINCT a.id) + COUNT(DISTINCT t.id))::decimal / NULLIF(20,0)) * 100, 2), 100) AS progress_percent
    FROM users u
    LEFT JOIN activities a ON a.user_id = u.id
    LEFT JOIN tests t ON t.user_id = u.id
    WHERE u.role = 'student'
    GROUP BY u.id
)
SELECT
    p.id AS parent_id,
    p.name AS parent_name,
    s.id AS student_id,
    s.name AS student_name,
    stp.literacy_level,
    stp.vocabulary_level,
    ROUND((stp.literacy_percentile * 100)::numeric, 2) AS literacy_percentile,
    ROUND((stp.vocabulary_percentile * 100)::numeric, 2) AS vocabulary_percentile,
    sp.activity_count,
    sp.tests_taken,
    sp.progress_percent
FROM users p
-- 학부모만 조회
JOIN subscriptions sub ON sub.user_id = p.id AND p.role = 'parent'
-- 학부모가 연결된 학생
JOIN users s ON s.id = sub.user_id AND s.role = 'student'
LEFT JOIN student_percentile stp ON stp.student_id = s.id
LEFT JOIN student_progress sp ON sp.student_id = s.id
ORDER BY p.id, s.id;

--고객센터 관리자용 통계 뷰(숫자, 개략적 문의 현황)
CREATE OR REPLACE VIEW admin_customer_support_summary AS
SELECT
    cs.category,
    COUNT(cs.id) AS total_count,
    COUNT(cs.id) FILTER (WHERE cs.status = 'open') AS open_count,
    COUNT(cs.id) FILTER (WHERE cs.status = 'in_progress') AS in_progress_count,
    COUNT(cs.id) FILTER (WHERE cs.status = 'resolved') AS resolved_count,
    COUNT(cs.id) FILTER (WHERE cs.status = 'closed') AS closed_count,
    COUNT(DISTINCT cs.user_id) AS unique_users
FROM customer_support cs
GROUP BY cs.category
ORDER BY cs.category;

--고객센터 관리자용 상세정보 뷰
CREATE OR REPLACE VIEW admin_customer_support_details AS
SELECT
    cs.id AS support_id,
    cs.user_id,
    u.name AS user_name,
    u.role AS user_role,
    cs.category,
    cs.title,
    cs.status,
    cs.created_at,
    cs.updated_at,
    csr.id AS response_id,
    csr.responder_id,
    ra.name AS responder_name,
    csr.content AS response_content,
    csr.created_at AS response_created_at
FROM customer_support cs
LEFT JOIN users u ON u.id = cs.user_id
LEFT JOIN customer_support_response csr ON csr.support_id = cs.id
LEFT JOIN users ra ON ra.id = csr.responder_id
ORDER BY cs.created_at DESC;
