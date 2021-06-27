CREATE OR REPLACE FUNCTION trigger_set_timestamp()
RETURNS TRIGGER AS $$
BEGIN
  NEW.modified_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TABLE doc (
    id  SERIAL PRIMARY KEY,
    created_at TIMESTAMP DEFAULT NOW(),
    modified_at TIMESTAMP DEFAULT NOW(),
    source TEXT
);

CREATE INDEX doc_id_idx ON doc(id);

CREATE TRIGGER set_timestamp
BEFORE UPDATE ON doc
FOR EACH ROW
EXECUTE PROCEDURE trigger_set_timestamp();

CREATE TABLE pdf (
    id SERIAL PRIMARY KEY,
    doc_id INT,
    numpages INT,
    author TEXT,
    title TEXT,
    doc_created TEXT,
    doc_modified TEXT
);

CREATE INDEX pdf_id_idx ON pdf(id);
CREATE INDEX pdf_doc_id_idx ON pdf(doc_id);
CREATE INDEX pdf_doc_created_idx ON pdf(doc_created);
CREATE INDEX pdf_doc_modified_idx ON pdf(doc_modified);

CREATE TABLE docx (
    id SERIAL PRIMARY KEY,
    doc_id INT,
    author TEXT,
    doc_created TIMESTAMP,
    doc_modified TIMESTAMP,
    last_author TEXT,
    num_edits INT,
    num_para INT,
    num_words INT
);

CREATE INDEX docx_id_idx ON docx(id);
CREATE INDEX docx_doc_id_idx ON docx(doc_id);
CREATE INDEX docx_created_idx ON docx(doc_created);
CREATE INDEX docx_modified_idx ON docx(doc_modified);

CREATE TABLE email (
    id SERIAL PRIMARY KEY,
    doc_id INT,
    num_emails INT
);

CREATE INDEX email_id_idx ON email(id);
CREATE INDEX email_doc_id_idx ON email(doc_id);

CREATE TABLE email_head (
    id SERIAL PRIMARY KEY,
    doc_id INT,
    loc INT,
    raw_txt TEXT
);

CREATE INDEX email_head_id_idx ON email_head(id);
CREATE INDEX email_head_doc_id_idx ON email_head(doc_id);
CREATE INDEX email_head_loc_idx ON email_head(loc);

CREATE TABLE textdata (
    id SERIAL PRIMARY KEY,
    doc_id INT,
    loc INT,
    raw_txt TEXT,
    txt TEXT
);
CREATE INDEX textdata_id_idx ON textdata(id);
CREATE INDEX textdata_doc_id_idx ON textdata(doc_id);
CREATE INDEX textdata_loc_idx ON textdata(loc);
--Create free text index in
ALTER TABLE textdata
    ADD COLUMN txt_index_col tsvector
        GENERATED ALWAYS AS (to_tsvector('english', txt)) STORED;
CREATE INDEX textdata_txt_index_col_idx ON textdata USING GIN (txt_index_col);

CREATE TABLE pdftextdata (
    id SERIAL PRIMARY KEY,
    textdata_id INT,
    pg INT
);
CREATE INDEX pdftextdata_id_idx ON pdftextdata(id);
CREATE INDEX pdftextdata_textdata_id_idx ON pdftextdata(textdata_id);
CREATE INDEX pdftextdata_pg_idx ON pdftextdata(pg);

CREATE TABLE transcriptdata(
    id SERIAL PRIMARY KEY,
    textdata_id INT,
    chunktime INT,
    confidence NUMERIC
);
CREATE INDEX transcriptdata_id_idx ON transcriptdata(id);
CREATE INDEX transcriptdata_textdata_id_idx ON transcriptdata(textdata_id);
CREATE INDEX transcriptdata_chunktime_idx ON transcriptdata(chunktime);

CREATE TABLE docxtextdata (
    id SERIAL PRIMARY KEY,
    textdata_id INT,
    para_num INT
);

CREATE INDEX doxctextdata_id_idx ON docxtextdata(id);
CREATE INDEX docxtextdata_textdata_id_idx ON docxtextdata(textdata_id);
CREATE INDEX docxtextdata_para_idx ON docxtextdata(para_num);
