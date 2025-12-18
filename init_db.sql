-- جدول کاربران
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول دسته‌بندی‌ها
CREATE TABLE IF NOT EXISTS categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    emoji VARCHAR(10),
    slug VARCHAR(50) UNIQUE NOT NULL
);

-- دسته‌بندی‌های پیش‌فرض
INSERT INTO categories (name, emoji, slug) VALUES
    ('گیمینگ', '🎮', 'gaming'),
    ('آشپزی', '🍳', 'cooking'),
    ('تکنولوژی', '💻', 'tech'),
    ('آموزشی', '📚', 'education'),
    ('سرگرمی', '🎬', 'entertainment'),
    ('لایف‌استایل', '💄', 'lifestyle'),
    ('ورزشی', '⚽', 'sports'),
    ('موسیقی', '🎵', 'music'),
    ('سفر', '✈️', 'travel'),
    ('کسب‌وکار', '💼', 'business')
ON CONFLICT (slug) DO NOTHING;

-- جدول کریتورها (یوتیوبر/اینستاگرامر)
CREATE TABLE IF NOT EXISTS creators (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    platform VARCHAR(20) DEFAULT 'YOUTUBE',
    category VARCHAR(50),
    wallet_bsc VARCHAR(255),
    wallet_polygon VARCHAR(255),
    wallet_tron VARCHAR(255),
    commission_rate DECIMAL(5,2) DEFAULT 5.0,
    is_active BOOLEAN DEFAULT TRUE,
    is_public BOOLEAN DEFAULT FALSE,
    telegram_id BIGINT,
    followers_count INT,
    min_sponsor_price INT,
    max_sponsor_price INT,
    profile_link VARCHAR(255),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول تراکنش‌ها
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    ref_code VARCHAR(30) UNIQUE NOT NULL,
    user_id INT NOT NULL REFERENCES users(id),
    creator_id INT NOT NULL REFERENCES creators(id),
    amount_expected DECIMAL(10,2) NOT NULL,
    amount_received DECIMAL(10,2),
    network VARCHAR(20) NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING_TXID',
    tx_proof_type VARCHAR(20),
    tx_proof_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT chk_status CHECK (
        status IN ('PENDING_TXID', 'PENDING_REVIEW', 'APPROVED', 'REJECTED')
    )
);

-- جدول درخواست‌های اسپانسرینگ
CREATE TABLE IF NOT EXISTS sponsor_leads (
    id SERIAL PRIMARY KEY,
    creator_id INT REFERENCES creators(id),
    sponsor_name VARCHAR(255) NOT NULL,
    contact_info VARCHAR(255) NOT NULL,
    budget_range VARCHAR(50),
    description TEXT,
    sponsor_tg_id BIGINT,
    assigned_to INT REFERENCES creators(id),
    status VARCHAR(50) DEFAULT 'NEW',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
