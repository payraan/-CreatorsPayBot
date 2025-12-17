-- جدول کاربران
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- جدول یوتیوبرها
CREATE TABLE IF NOT EXISTS creators (
    id SERIAL PRIMARY KEY,
    slug VARCHAR(100) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    wallet_bsc VARCHAR(255),
    wallet_polygon VARCHAR(255),
    wallet_tron VARCHAR(255),
    commission_rate DECIMAL(5,2) DEFAULT 5.0,
    is_active BOOLEAN DEFAULT TRUE,
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
