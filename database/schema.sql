-- =============================================================
--  CrimeDatabase — PostgreSQL Schema & Setup
--  Run this file in psql or pgAdmin to initialize the database
-- =============================================================


-- -------------------------------------------------------------
-- TABLE: officer
-- Stores police officer details
-- -------------------------------------------------------------
CREATE TABLE officer (
    officer_id   SERIAL PRIMARY KEY,
    name         VARCHAR(100) NOT NULL,
    badge_number VARCHAR(20)  UNIQUE NOT NULL
);


-- -------------------------------------------------------------
-- TABLE: fir
-- First Information Reports — core records of the system
-- -------------------------------------------------------------
CREATE TABLE fir (
    fir_id      SERIAL PRIMARY KEY,
    date_filed  DATE         NOT NULL,
    description TEXT         NOT NULL,
    status      VARCHAR(20)  DEFAULT 'Pending'
);


-- -------------------------------------------------------------
-- TABLE: suspect
-- Suspects linked to a FIR (cascades on FIR delete)
-- -------------------------------------------------------------
CREATE TABLE suspect (
    suspect_id SERIAL PRIMARY KEY,
    fir_id     INT REFERENCES fir(fir_id) ON DELETE CASCADE,
    name       VARCHAR(100) NOT NULL,
    details    TEXT
);


-- -------------------------------------------------------------
-- TABLE: cases
-- One case per FIR, assigned to an officer
-- -------------------------------------------------------------
CREATE TABLE cases (
    case_id      SERIAL PRIMARY KEY,
    fir_id       INT UNIQUE REFERENCES fir(fir_id),
    officer_id   INT REFERENCES officer(officer_id),
    status       VARCHAR(20)  DEFAULT 'Open',
    last_updated TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);


-- -------------------------------------------------------------
-- TABLE: evidence
-- Evidence items linked to a case (cascades on case delete)
-- -------------------------------------------------------------
CREATE TABLE evidence (
    evidence_id SERIAL PRIMARY KEY,
    case_id     INT  REFERENCES cases(case_id) ON DELETE CASCADE,
    description TEXT NOT NULL,
    date_logged DATE NOT NULL
);


-- =============================================================
--  SEED DATA
-- =============================================================

INSERT INTO officer (name, badge_number) VALUES
    ('Inspector Vikram',      'B-101'),
    ('Sub-Inspector Anjali',  'B-102');


-- =============================================================
--  STORED PROCEDURE: AssignCase
--  Creates a case entry for a FIR and marks FIR as Assigned
-- =============================================================
CREATE OR REPLACE PROCEDURE AssignCase(p_fir_id INT, p_officer_id INT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO cases (fir_id, officer_id, status)
    VALUES (p_fir_id, p_officer_id, 'Open');

    UPDATE fir
    SET status = 'Assigned'
    WHERE fir_id = p_fir_id;
END;
$$;

-- Usage:
-- CALL AssignCase(1, 1);   -- Assign FIR #1 to Inspector Vikram


-- =============================================================
--  TRIGGER FUNCTION: update_case_timestamp
--  Auto-updates last_updated on cases when new evidence is added
-- =============================================================
CREATE OR REPLACE FUNCTION update_case_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE cases
    SET last_updated = CURRENT_TIMESTAMP
    WHERE case_id = NEW.case_id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;


CREATE TRIGGER UpdateCaseTimestamp
AFTER INSERT ON evidence
FOR EACH ROW
EXECUTE FUNCTION update_case_timestamp();


-- =============================================================
--  USEFUL QUERIES
-- =============================================================

-- View all FIRs
SELECT * FROM fir;

-- View a specific FIR by ID
SELECT * FROM fir WHERE fir_id = 1;

-- View all cases with assigned officer names
SELECT
    c.case_id,
    f.fir_id,
    f.description,
    f.status       AS fir_status,
    o.name         AS officer,
    o.badge_number,
    c.status       AS case_status,
    c.last_updated
FROM cases c
JOIN fir     f ON c.fir_id     = f.fir_id
JOIN officer o ON c.officer_id = o.officer_id
ORDER BY c.case_id DESC;

-- View all suspects for a specific FIR
SELECT s.*, f.description AS fir_description
FROM suspect s
JOIN fir f ON s.fir_id = f.fir_id
WHERE s.fir_id = 1;

-- View all evidence for a specific case
SELECT e.*, c.status AS case_status
FROM evidence e
JOIN cases c ON e.case_id = c.case_id
WHERE e.case_id = 1;

-- Count FIRs by status
SELECT status, COUNT(*) AS total
FROM fir
GROUP BY status
ORDER BY total DESC;

-- View all pending FIRs not yet assigned to a case
SELECT f.*
FROM fir f
LEFT JOIN cases c ON f.fir_id = c.fir_id
WHERE c.case_id IS NULL
  AND f.status = 'Pending'
ORDER BY f.date_filed ASC;

-- Delete a FIR (verify first with SELECT before running DELETE)
-- SELECT * FROM fir WHERE fir_id = 1;
-- DELETE FROM fir WHERE fir_id = 1;
