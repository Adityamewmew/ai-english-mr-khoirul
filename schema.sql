-- ponytail: migrate via DB constraint dulu, ORM later
CREATE TABLE IF NOT EXISTS users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS assessments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  overall_cefr TEXT CHECK (overall_cefr IN ('A1','A2','B1','B2','C1','C2')),
  overall_score INT CHECK (overall_score BETWEEN 0 AND 100),
  listening_cefr TEXT, reading_cefr TEXT, speaking_cefr TEXT, writing_cefr TEXT,
  uneven_profile BOOLEAN DEFAULT false,
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE TABLE IF NOT EXISTS assessment_items (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  skill TEXT CHECK (skill IN ('listening','reading','speaking','writing')),
  prompt TEXT,
  cefr_tag TEXT CHECK (cefr_tag IN ('A1','A2','B1','B2','C1','C2')),
  user_answer TEXT,
  is_correct BOOLEAN,
  weight NUMERIC,
  time_spent_s INT
);
CREATE TABLE IF NOT EXISTS assessment_rubrics (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  assessment_id UUID REFERENCES assessments(id) ON DELETE CASCADE,
  skill TEXT,
  criterion TEXT,
  score_0_5 NUMERIC CHECK (score_0_5 BETWEEN 0 AND 5),
  feedback_text TEXT
);
CREATE TABLE IF NOT EXISTS score_conversions (
  cefr TEXT PRIMARY KEY,
  ielts TEXT, toefl_1_6 TEXT, toefl_0_120 TEXT, score_range TEXT
);
INSERT INTO score_conversions VALUES
 ('A1','<4.0','1.0','0-30','0-19'),
 ('A2','4.0-5.0','2.0','31-45','20-39'),
 ('B1','5.0-6.0','3.0-3.5','42-71','40-59'),
 ('B2','6.5-7.5','4.0-5.0','72-94','60-79'),
 ('C1','8.0-8.5','5.5','95-106','80-92'),
 ('C2','9.0','6.0','107-120','93-100')
ON CONFLICT DO NOTHING;
