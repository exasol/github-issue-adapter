CREATE TABLE EXASOL_JABR.ISSUES (
		REPO VARCHAR(254) UTF8,
		ISSUE_NR DECIMAL(5,0),
		NAME VARCHAR(500) UTF8,
		FIXED TIMESTAMP WITH LOCAL TIME ZONE,
		FIRST_LABEL VARCHAR(50) UTF8,
		UPDATED TIMESTAMP WITH LOCAL TIME ZONE,
		CREATED TIMESTAMP WITH LOCAL TIME ZONE
);


CREATE OR REPLACE VIEW EXASOL_JABR.ALL_ISSUES AS (SELECT DISTINCT issues.* FROM EXASOL_JABR.ISSUES issues JOIN (SELECT MAX(UPDATED) AS LATEST_VERSION, REPO, ISSUE_NR FROM EXASOL_JABR.ISSUES GROUP BY REPO, ISSUE_NR) latest_filter
ON issues.UPDATED = latest_filter.LATEST_VERSION AND issues.REPO = latest_filter.REPO AND issues.ISSUE_NR = latest_filter.ISSUE_NR)